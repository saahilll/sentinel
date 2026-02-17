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
from app.core.security import create_access_token, verify_password, hash_password

logger = logging.getLogger(__name__)


# Placeholder for email service (prints to console in dev)
def _send_magic_link_email(email: str, token: str) -> None:
    print(
        f"MAGIC LINK for {email}: "
        f"http://localhost:3000/verify?token={token}&flow=signup"
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

    # ── Profile Management ────────────────────────────────────────

    async def get_profile(self, user_id: UUID) -> dict:
        """Get full profile for account settings page."""
        from app.core.exceptions import NotFoundError

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        # Build display name from first/last name
        display_name = user.first_name or ""
        if user.last_name:
            display_name = f"{display_name} {user.last_name}".strip()
        if not display_name:
            display_name = user.email.split("@")[0]

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "display_name": display_name,
            "picture": user.avatar_url,
            "email_verified": user.email_verified,
            "has_password": bool(user.hashed_password and user.hashed_password != "!"),
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
        }

    async def update_profile(self, user_id: UUID, name: str) -> dict:
        """Update user's display name (split into first_name/last_name)."""
        from app.core.exceptions import NotFoundError

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        # Parse display name into first/last name
        parts = name.strip().split(maxsplit=1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else None

        await self.user_repo.update(user)
        logger.info(f"Profile updated for user {user_id}")

        return await self.get_profile(user_id)

    async def set_password(
        self,
        user_id: UUID,
        new_password: str,
        confirm_password: str,
        current_password: str | None = None,
    ) -> None:
        """Set or change password with validation."""
        from app.core.exceptions import NotFoundError, ValidationError

        if new_password != confirm_password:
            raise ValidationError("Passwords do not match")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        has_password = bool(user.hashed_password and user.hashed_password != "!")

        # If user already has a password, require current password
        if has_password:
            if not current_password:
                raise AuthenticationError("Current password is required")
            if not verify_password(current_password, user.hashed_password):
                raise AuthenticationError("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.user_repo.update(user)
        logger.info(f"Password {'changed' if has_password else 'set'} for user {user_id}")

    async def delete_account(self, user_id: UUID) -> None:
        """Soft-delete account: deactivate and revoke all sessions."""
        from app.core.exceptions import NotFoundError

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        # Soft-delete: deactivate instead of hard delete
        user.is_active = False
        user.deactivated_at = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        # Revoke all sessions
        revoked = await self.token_repo.revoke_all_user_sessions(user_id)
        logger.info(
            f"Account deactivated for user {user_id}, "
            f"{revoked} sessions revoked"
        )

    async def logout_all(self, user_id: UUID) -> int:
        """Revoke all active sessions for a user."""
        count = await self.token_repo.revoke_all_user_sessions(user_id)
        logger.info(f"All sessions revoked for user {user_id}: {count} revoked")
        return count

