"""
User schemas (DTOs) for API request/response validation.
Separates API contracts from database models.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.auth.models.membership import OrgRole


# === Request Schemas ===


class InviteRequest(BaseModel):
    """Schema for inviting a user."""

    email: EmailStr
    role: OrgRole = OrgRole.MEMBER


class UserCreate(BaseModel):
    """Schema for org owner registration (creates user + organization)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    organization_name: str = Field(min_length=2, max_length=255)
    invites: list[InviteRequest] = Field(default_factory=list)


class UserCreateInvite(BaseModel):
    """Schema for invited user registration (joins existing org)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""

    refresh_token: str


class OrganizationCreate(BaseModel):
    """Schema for creating a new organization (authenticated user)."""

    name: str = Field(min_length=2, max_length=255)
    invites: list[InviteRequest] = Field(default_factory=list)


# === Response Schemas ===


class UserResponse(BaseModel):
    """Schema for user data in responses (no password)."""

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None
    is_superadmin: bool
    is_active: bool
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationBrief(BaseModel):
    """Brief organization info for login response."""

    id: uuid.UUID
    name: str
    slug: str
    role: str


class OrganizationResponse(BaseModel):
    """Full organization info for create response."""

    id: uuid.UUID
    name: str
    slug: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Schema for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class RegisterResult(BaseModel):
    """Internal result from registration (not exposed to API)."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    organization_id: uuid.UUID


class LoginResponse(BaseModel):
    """Schema for login response with tokens and organizations."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    organizations: list[OrganizationBrief]


class InviteResponse(BaseModel):
    """Schema for invitation response."""

    id: uuid.UUID
    email: str
    role: str
    token: str
    expires_at: datetime

    model_config = {"from_attributes": True}


class InviteValidation(BaseModel):
    """Schema for validating an invite token."""

    email: str
    organization_name: str
    role: str
    is_valid: bool


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class MagicLinkRequest(BaseModel):
    email: EmailStr
    flow: str | None = None  # "login", "signup", "reset"


class VerifyRequest(BaseModel):
    token: str
    flow: str | None = None
    device_info: str | None = ""
    remember_me: bool = True


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    flow: str | None = None
    device_info: str | None = ""
    remember_me: bool = True


class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = True


class ValidateRequest(BaseModel):
    """Schema for session validation."""

    refresh_token: str


class ValidateResponse(BaseModel):
    """Schema for session validation response."""

    valid: bool


class SessionResponse(BaseModel):
    """Schema for active session info."""

    id: uuid.UUID
    device_info: str
    ip_address: str | None = None
    last_used_at: datetime
    created_at: datetime
    is_current: bool = False

    model_config = {"from_attributes": True}


# === Account / Profile Schemas ===


class ProfileResponse(BaseModel):
    """Full user profile for account settings."""

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str | None = None
    display_name: str
    picture: str | None = None
    email_verified: bool
    has_password: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None


class UpdateProfileRequest(BaseModel):
    """Request to update user profile (display name)."""

    name: str = Field(min_length=1, max_length=200)


class SetPasswordRequest(BaseModel):
    """Request to set or change password."""

    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    current_password: str | None = None
