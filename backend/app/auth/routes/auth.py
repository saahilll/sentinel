"""
Authentication API endpoints.
Handles user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, get_db
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.auth.schemas import (
    InviteValidation,
    LoginResponse,
    MessageResponse,
    OrganizationBrief,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserCreateInvite,
    UserLogin,
    UserResponse,
)
from app.auth.services.auth import AuthService

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
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user and create their organization."""
    auth_service = AuthService(db)

    try:
        return await auth_service.register(user_data)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.message),
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
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Register using an invitation token."""
    auth_service = AuthService(db)

    try:
        return await auth_service.register_with_invite(user_data, token)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.message),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )


@router.get(
    "/invites/{token}",
    response_model=InviteValidation,
    summary="Validate invitation",
)
async def validate_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> InviteValidation:
    """Validate an invitation token and get details."""
    auth_service = AuthService(db)
    result = await auth_service.validate_invite(token)
    return InviteValidation(**result)


@router.post(
    "/accept-invite",
    response_model=OrganizationBrief,
    summary="Accept invitation (existing user)",
)
async def accept_invite(
    token: str = Query(..., description="Invitation token"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> OrganizationBrief:
    """Accept an invitation to join an organization. Requires authentication."""
    auth_service = AuthService(db)

    try:
        return await auth_service.accept_invite(user_id, token)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.message),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Authenticate with email and password."""
    auth_service = AuthService(db)

    try:
        return await auth_service.login(credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token",
)
async def refresh_token(
    request_body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Get a new access token using a valid refresh token."""
    auth_service = AuthService(db)

    try:
        return await auth_service.refresh_tokens(request_body.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the currently authenticated user's profile."""
    auth_service = AuthService(db)

    try:
        user = await auth_service.get_current_user(user_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
)
async def logout() -> MessageResponse:
    """Logout the current user (client-side token cleanup)."""
    return MessageResponse(message="Successfully logged out")
