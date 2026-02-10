"""
User domain model using SQLModel.
Represents the users table in the database.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user fields shared across schemas."""

    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    avatar_url: str | None = Field(default=None, max_length=512)
    is_active: bool = Field(default=True)
    is_superadmin: bool = Field(default=False)
    email_verified: bool = Field(default=False)


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
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
    )
    last_login_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    deactivated_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

