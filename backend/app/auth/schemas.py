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

