"""
Auth API routes — mirrors APILens router pattern.
Uses centralized DI from dependencies.py.
Includes rate limiting on sensitive endpoints.
"""

import uuid

from fastapi import APIRouter, Depends, Request, status

from app.auth.schemas import (
    MagicLinkRequest,
    MessageResponse,
    PasswordLoginRequest,
    RefreshTokenRequest,
    SessionResponse,
    TokenResponse,
    UserResponse,
    ValidateRequest,
    ValidateResponse,
    VerifyRequest,
)
from app.core.dependencies import get_auth_service, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


# ── Magic Link ────────────────────────────────────────────────────


@router.post("/magic-link", response_model=MessageResponse)
async def request_magic_link(
    data: MagicLinkRequest,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    ip = _get_client_ip(request)
    await auth_service.request_magic_link(data.email, ip_address=ip)
    return {"message": "If that email is valid, a magic link has been sent."}


@router.post("/verify", response_model=TokenResponse)
async def verify_magic_link(
    data: VerifyRequest,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    ip = _get_client_ip(request)
    device = data.device_info or request.headers.get("user-agent", "")[:255]
    access_token, refresh_token, _ = await auth_service.verify_magic_link(
        token=data.token,
        device_info=device,
        ip_address=ip,
        remember_me=data.remember_me,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# ── Password Login ────────────────────────────────────────────────


@router.post("/login", response_model=TokenResponse)
async def login_with_password(
    data: PasswordLoginRequest,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    ip = _get_client_ip(request)
    device = request.headers.get("user-agent", "")[:255]
    access_token, refresh_token, _ = await auth_service.login_with_password(
        email=data.email,
        password=data.password,
        device_info=device,
        ip_address=ip,
        remember_me=data.remember_me,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# ── Token Management ──────────────────────────────────────────────


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service=Depends(get_auth_service),
):
    access_token, refresh_token, _ = await auth_service.refresh_token(
        data.refresh_token
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/validate", response_model=ValidateResponse)
async def validate_session(
    data: ValidateRequest,
    auth_service=Depends(get_auth_service),
):
    """Check if a session is alive without rotating tokens."""
    valid = await auth_service.validate_session(data.refresh_token)
    return ValidateResponse(valid=valid)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshTokenRequest,
    auth_service=Depends(get_auth_service),
):
    await auth_service.logout(data.refresh_token)
    return {"message": "Logged out successfully"}


# ── Session Management ────────────────────────────────────────────


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    auth_service=Depends(get_auth_service),
):
    """List active sessions for the current user."""
    sessions = await auth_service.get_active_sessions(uuid.UUID(user_id))
    return sessions


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    auth_service=Depends(get_auth_service),
):
    """Revoke a specific session for the current user."""
    revoked = await auth_service.revoke_session(uuid.UUID(user_id), session_id)
    if not revoked:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Session")
    return {"message": "Session revoked"}


# ── User Info ─────────────────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    auth_service=Depends(get_auth_service),
):
    user = await auth_service.user_repo.get_by_id(uuid.UUID(user_id))
    return user
