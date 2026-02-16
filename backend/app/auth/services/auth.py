"""
Authentication service — orchestrates auth flows.
Matches APILens pattern: returns (access_token, refresh_token, user) tuples.
Includes rate limiting, reuse detection, session management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.auth.models.user import User
from app.auth.repositories.token import TokenRepository, MAGIC_LINK_RATE_LIMIT
from app.auth.repositories.user import UserRepository
from app.core.exceptions import AuthenticationError, RateLimitError
from app.core.security import create_access_token, verify_password

logger = logging.getLogger(__name__)


# Placeholder for email service (prints to console in dev)
def _send_magic_link_email(email: str, token: str) -> None:
    print(
        f"MAGIC LINK for {email}: "
        f"http://localhost:3000/auth/verify?token={token}&flow=signup"
    )


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

    # ── Magic Link ────────────────────────────────────────────────

    async def request_magic_link(
        self, email: str, ip_address: Optional[str] = None
    ) -> None:
        """Request a magic link. Rate limited to 3/min/email."""
        email = email.lower().strip()

        # Rate limit check (same as APILens)
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        recent = await self.token_repo.count_recent_magic_links(email, one_minute_ago)
        if recent >= MAGIC_LINK_RATE_LIMIT:
            raise RateLimitError(
                "Too many magic link requests. Please wait a moment."
            )

        raw_token = await self.token_repo.create_magic_link_token(email, ip_address)
        _send_magic_link_email(email, raw_token)

    async def verify_magic_link(
        self,
        token: str,
        device_info: str = "",
        ip_address: Optional[str] = None,
        remember_me: bool = True,
    ) -> tuple[str, str, User]:
        """Verify a magic link and return (access_token, refresh_token, user)."""
        magic_token = await self.token_repo.get_magic_link_token(token)
        if not magic_token:
            raise AuthenticationError("Invalid or expired magic link")

        await self.token_repo.mark_magic_link_used(magic_token)

        # Get or create user (same pattern as APILens)
        user = await self.user_repo.get_by_email(magic_token.email)
        if not user:
            new_user = User(
                email=magic_token.email,
                first_name="User",
                hashed_password="!",  # unusable password
                email_verified=True,
                auth_provider="magic_link",
            )
            user = await self.user_repo.create(new_user)
            logger.info(f"New user created via magic link: {magic_token.email}")
        elif not user.email_verified:
            user.email_verified = True
            await self.user_repo.update(user)

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        # Create tokens (pass remember_me)
        raw_refresh, _ = await self.token_repo.create_refresh_token(
            user, device_info, ip_address, remember_me=remember_me
        )
        access_token = create_access_token(subject=str(user.id))

        return access_token, raw_refresh, user

    # ── Password Login ────────────────────────────────────────────

    async def login_with_password(
        self,
        email: str,
        password: str,
        device_info: str = "",
        ip_address: Optional[str] = None,
        remember_me: bool = True,
    ) -> tuple[str, str, User]:
        """Authenticate with email+password. Returns (access_token, refresh_token, user)."""
        email = email.lower().strip()

        # Filter by is_active (gap #9 fix)
        user = await self.user_repo.get_active_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        raw_refresh, _ = await self.token_repo.create_refresh_token(
            user, device_info, ip_address, remember_me=remember_me
        )
        access_token = create_access_token(subject=str(user.id))

        return access_token, raw_refresh, user

    # ── Refresh (with reuse detection) ────────────────────────────

    async def refresh_token(self, raw_refresh_token: str) -> tuple[str, str, User]:
        """Rotate refresh token with reuse detection. Returns (access, refresh, user)."""
        new_raw, _, user = await self.token_repo.rotate_refresh_token(
            raw_refresh_token
        )
        access_token = create_access_token(subject=str(user.id))
        return access_token, new_raw, user

    # ── Validate ──────────────────────────────────────────────────

    async def validate_session(self, raw_refresh_token: str) -> bool:
        """Check if a session is alive without rotating."""
        return await self.token_repo.is_session_alive(raw_refresh_token)

    # ── Sessions ──────────────────────────────────────────────────

    async def get_active_sessions(self, user_id: UUID):
        """List active sessions for a user (deduplicated by device/IP)."""
        return await self.token_repo.get_active_sessions(user_id)

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> bool:
        """Revoke a specific session."""
        return await self.token_repo.revoke_session(user_id, session_id)

    # ── Logout ────────────────────────────────────────────────────

    async def logout(self, raw_refresh_token: str) -> None:
        token_obj = await self.token_repo.get_refresh_token(raw_refresh_token)
        if token_obj:
            await self.token_repo.revoke_refresh_token(token_obj)
