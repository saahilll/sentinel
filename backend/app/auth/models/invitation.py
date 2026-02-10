"""
Invitation model for user invitations to organizations.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.auth.models.membership import OrgRole


class InviteStatus(str, Enum):
    """Status of an invitation."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


def generate_invite_token() -> str:
    """Generate a secure random invite token."""
    return secrets.token_urlsafe(32)


def default_expiry() -> datetime:
    """Default expiration: 7 days from now."""
    return datetime.now(timezone.utc) + timedelta(days=7)


class Invitation(SQLModel, table=True):
    """
    Invitation to join an organization.
    Maps to 'invitations' table in PostgreSQL.
    """

    __tablename__ = "invitations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    email: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )
    role: OrgRole = Field(default=OrgRole.MEMBER)
    token: str = Field(
        default_factory=generate_invite_token,
        sa_column=Column(String(64), unique=True, index=True, nullable=False),
    )
    status: InviteStatus = Field(
        sa_column=Column(
            SAEnum(InviteStatus),
            nullable=False,
            default=InviteStatus.PENDING,
        )
    )
    invited_by: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=default_expiry,
            nullable=False,
        )
    )
    accepted_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    revoked_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    revoked_by: uuid.UUID | None = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
        )
    )

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """Check if invitation has been accepted."""
        return self.accepted_at is not None

