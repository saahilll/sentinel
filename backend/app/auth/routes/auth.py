"""
Authentication API endpoints.
Handles user registration, login, and token management.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.dependencies import get_auth_service, get_current_user_id, get_invite_service
from app.auth.schemas import (
    InviteValidation,
    LoginResponse,
    MessageResponse,
    OrganizationBrief,
    OrganizationCreate,
    OrganizationResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserCreateInvite,
    UserLogin,
    UserResponse,
)
from app.auth.services.auth import AuthService
from app.auth.services.invite import InviteService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as org owner",
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    invite_service: InviteService = Depends(get_invite_service),
) -> TokenResponse:
    """Register a new user and create their organization."""
    result = await auth_service.register(user_data)

    # Create invitations for team members (if any)
    if user_data.invites:
        await invite_service.create_invites_for_registration(
            org_id=result.organization_id,
            invites=user_data.invites,
            inviter_id=result.user_id,
        )

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/register/invite",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register with invitation",
)
@limiter.limit("5/minute")
async def register_with_invite(
    request: Request,
    user_data: UserCreateInvite,
    token: str = Query(..., description="Invitation token"),
    invite_service: InviteService = Depends(get_invite_service),
) -> LoginResponse:
    """Register using an invitation token."""
    return await invite_service.register_with_invite(user_data, token)


@router.get(
    "/invites/{token}",
    response_model=InviteValidation,
    summary="Validate invitation",
)
async def validate_invite(
    token: str,
    invite_service: InviteService = Depends(get_invite_service),
) -> InviteValidation:
    """Validate an invitation token and get details."""
    return await invite_service.validate_invite(token)


@router.post(
    "/accept-invite",
    response_model=OrganizationBrief,
    summary="Accept invitation (existing user)",
)
async def accept_invite(
    token: str = Query(..., description="Invitation token"),
    user_id: str = Depends(get_current_user_id),
    invite_service: InviteService = Depends(get_invite_service),
) -> OrganizationBrief:
    """Accept an invitation to join an organization. Requires authentication."""
    return await invite_service.accept_invite(user_id, token)


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
async def create_organization(
    org_data: OrganizationCreate,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
    invite_service: InviteService = Depends(get_invite_service),
) -> OrganizationResponse:
    """Create a new organization. The authenticated user becomes the owner."""
    result = await auth_service.create_organization(user_id, org_data)

    # Create invitations for team members (if any)
    if org_data.invites:
        await invite_service.create_invites_for_registration(
            org_id=result.id,
            invites=org_data.invites,
            inviter_id=uuid.UUID(user_id),
        )

    return result


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Authenticate with email and password."""
    return await auth_service.login(credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token",
)
async def refresh_token(
    request_body: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Get a new access token using a valid refresh token."""
    return await auth_service.refresh_tokens(request_body.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Get the currently authenticated user's profile."""
    user = await auth_service.get_current_user(user_id)
    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
)
async def logout() -> MessageResponse:
    """Logout the current user (client-side token cleanup)."""
    return MessageResponse(message="Successfully logged out")
