"""
User domain model using SQLModel.
Represents the users table in the database.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """User roles for authorization."""

    USER = "user"
    ADMIN = "admin"
    AGENT = "agent"  # Support agent


class UserBase(SQLModel):
    """Base user fields shared across schemas."""

    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)  # TODO: Implement email verification


class User(UserBase, table=True):
    """
    User database model.
    Maps to 'user' table in PostgreSQL.
    """

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    )

