"""
Token repository — data access for RefreshToken and MagicLinkToken.
Implements reuse detection, family-based revocation, rate limiting,
session-touch debounce, and cleanup — matching APILens patterns.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, func, delete

from app.auth.models.token import RefreshToken, MagicLinkToken
from app.auth.models.user import User

logger = logging.getLogger(__name__)

# ── Constants (mirror APILens) ────────────────────────────────────
REFRESH_TOKEN_LIFETIME = timedelta(days=30)
REFRESH_TOKEN_SESSION_LIFETIME = timedelta(hours=24)
MAGIC_LINK_LIFETIME = timedelta(minutes=15)
MAGIC_LINK_RATE_LIMIT = 3  # per minute per email
_LAST_USED_DEBOUNCE = timedelta(seconds=60)


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    @staticmethod
    def _normalized_device(device_info: str) -> str:
        return (device_info or "").strip()[:255]

    # ── Refresh Token CRUD ────────────────────────────────────────

    async def create_refresh_token(
        self,
        user: User,
        device_info: str = "",
        ip_address: Optional[str] = None,
        remember_me: bool = True,
        token_family: Optional[UUID] = None,
    ) -> tuple[str, RefreshToken]:
        """Create a new refresh token. Revokes existing sessions from same device."""
        raw_token = secrets.token_urlsafe(48)
        lifetime = REFRESH_TOKEN_LIFETIME if remember_me else REFRESH_TOKEN_SESSION_LIFETIME
        normalized = self._normalized_device(device_info)

        # Dedupe: revoke existing tokens from the same device (APILens pattern)
        if normalized:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.device_info == normalized,
                RefreshToken.is_revoked == False,
            )
            result = await self.session.execute(stmt)
            for existing in result.scalars().all():
                existing.is_revoked = True
                self.session.add(existing)
        elif ip_address:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.ip_address == ip_address,
                RefreshToken.is_revoked == False,
            )
            result = await self.session.execute(stmt)
            for existing in result.scalars().all():
                existing.is_revoked = True
                self.session.add(existing)

        now = datetime.now(timezone.utc)
        token = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(raw_token),
            expires_at=now + lifetime,
            device_info=normalized,
            ip_address=ip_address,
            last_used_at=now,
        )
        # Preserve family if rotating within an existing chain
        if token_family:
            token.token_family = token_family

        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return raw_token, token

    async def get_refresh_token(self, raw_token: str) -> Optional[RefreshToken]:
        token_hash = self._hash_token(raw_token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.is_revoked = True
        self.session.add(token)
        await self.session.flush()

    async def revoke_family(self, token_family: UUID) -> None:
        """Revoke all tokens in a family (reuse detection response)."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_family == token_family,
            RefreshToken.is_revoked == False,
        )
        result = await self.session.execute(stmt)
        for t in result.scalars().all():
            t.is_revoked = True
            self.session.add(t)
        await self.session.flush()

    async def rotate_refresh_token(
        self, raw_token: str
    ) -> tuple[str, RefreshToken, User]:
        """
        Rotate a refresh token (APILens pattern):
        1. If already revoked → revoke entire family (token theft) → raise
        2. If expired → raise
        3. Revoke old, create new in same family
        Returns (new_raw_token, new_token_obj, user).
        Note: caller must create access token separately.
        """
        from app.core.exceptions import AuthenticationError, TokenExpiredError

        token_hash = self._hash_token(raw_token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        token_obj = result.scalar_one_or_none()

        if token_obj is None:
            raise AuthenticationError("Invalid refresh token")

        # Reuse detection: if token is already revoked, someone replayed it
        if token_obj.is_revoked:
            await self.revoke_family(token_obj.token_family)
            # CRITICAL: commit the family revocation before raising,
            # because get_session() rolls back on exception
            await self.session.commit()
            logger.warning(
                f"Refresh token reuse detected for user {token_obj.user_id}, "
                f"family {token_obj.token_family}"
            )
            raise AuthenticationError("Refresh token reuse detected")

        now = datetime.now(timezone.utc)
        expires = token_obj.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now:
            raise TokenExpiredError("Refresh token has expired")

        # Revoke old token
        token_obj.is_revoked = True
        self.session.add(token_obj)

        # Get user
        from app.auth.repositories.user import UserRepository
        user_stmt = select(User).where(User.id == token_obj.user_id)
        user_result = await self.session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise AuthenticationError("User not found")

        # Issue new token in the same family
        remaining = expires - now
        new_raw = secrets.token_urlsafe(48)
        new_token = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(new_raw),
            token_family=token_obj.token_family,
            expires_at=now + remaining,
            device_info=token_obj.device_info,
            ip_address=token_obj.ip_address,
            last_used_at=now,
        )
        self.session.add(new_token)
        await self.session.flush()
        await self.session.refresh(new_token)

        return new_raw, new_token, user

    # ── Session Management ────────────────────────────────────────

    async def is_session_alive(self, raw_token: str) -> bool:
        """Check if a refresh token is valid without rotating."""
        token_hash = self._hash_token(raw_token)
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_active_sessions(self, user_id: UUID) -> list[RefreshToken]:
        """Get deduplicated active sessions for a user (latest per device/IP)."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now,
            )
            .order_by(col(RefreshToken.last_used_at).desc())
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        # Dedupe by device+IP fingerprint (APILens pattern)
        seen: set[str] = set()
        deduplicated: list[RefreshToken] = []
        for row in rows:
            fp = f"{self._normalized_device(row.device_info)}|{row.ip_address or ''}"
            if fp not in seen:
                seen.add(fp)
                deduplicated.append(row)
        return deduplicated

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> bool:
        """Revoke a specific session by ID."""
        stmt = select(RefreshToken).where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
        result = await self.session.execute(stmt)
        token = result.scalar_one_or_none()
        if token:
            token.is_revoked = True
            self.session.add(token)
            await self.session.flush()
            return True
        return False

    async def touch_session(self, token_family: UUID) -> None:
        """Update last_used_at (debounced — only if >60s since last update)."""
        now = datetime.now(timezone.utc)
        threshold = now - _LAST_USED_DEBOUNCE
        stmt = select(RefreshToken).where(
            RefreshToken.token_family == token_family,
            RefreshToken.is_revoked == False,
            RefreshToken.last_used_at < threshold,
        )
        result = await self.session.execute(stmt)
        for t in result.scalars().all():
            t.last_used_at = now
            self.session.add(t)
        await self.session.flush()

    async def revoke_all_user_sessions(self, user_id: UUID) -> int:
        """Revoke all active sessions for a user. Returns count revoked."""
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        count = 0
        for t in result.scalars().all():
            t.is_revoked = True
            self.session.add(t)
            count += 1
        await self.session.flush()
        return count

    # ── Magic Link CRUD ───────────────────────────────────────────

    async def count_recent_magic_links(self, email: str, since: datetime) -> int:
        """Count recent magic links for rate limiting."""
        stmt = select(func.count()).select_from(MagicLinkToken).where(
            MagicLinkToken.email == email,
            MagicLinkToken.created_at >= since,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_magic_link_token(
        self, email: str, ip_address: Optional[str] = None
    ) -> str:
        raw_token = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)

        token = MagicLinkToken(
            email=email.lower().strip(),
            token_hash=self._hash_token(raw_token),
            expires_at=now + MAGIC_LINK_LIFETIME,
            ip_address=ip_address,
            created_at=now,
        )
        self.session.add(token)
        await self.session.flush()
        return raw_token

    async def get_magic_link_token(self, raw_token: str) -> Optional[MagicLinkToken]:
        token_hash = self._hash_token(raw_token)
        now = datetime.now(timezone.utc)
        stmt = select(MagicLinkToken).where(
            MagicLinkToken.token_hash == token_hash,
            MagicLinkToken.is_used == False,
            MagicLinkToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_magic_link_used(self, token: MagicLinkToken) -> None:
        token.is_used = True
        self.session.add(token)
        await self.session.flush()

    # ── Cleanup ───────────────────────────────────────────────────

    async def cleanup_expired(self) -> int:
        """Delete expired/used tokens (housekeeping)."""
        now = datetime.now(timezone.utc)
        # Expired refresh tokens
        stmt1 = delete(RefreshToken).where(RefreshToken.expires_at <= now)
        r1 = await self.session.execute(stmt1)
        # Expired or used magic links
        stmt2 = delete(MagicLinkToken).where(MagicLinkToken.expires_at <= now)
        r2 = await self.session.execute(stmt2)
        await self.session.flush()
        return r1.rowcount + r2.rowcount
