"""
UserOrganization join table model.
Represents the many-to-many relationship between users and organizations.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class OrgRole(str, Enum):
    """User roles within an organization."""

    OWNER = "owner"  # Full control, can delete org
    ADMIN = "admin"  # Can manage members and settings
    MEMBER = "member"  # Regular access
    VIEWER = "viewer"  # Read-only access for stakeholders


class UserOrganization(SQLModel, table=True):
    """
    Join table for User ↔ Organization many-to-many relationship.
    Maps to 'user_organizations' table in PostgreSQL.
    """

    __tablename__ = "user_organizations"
    __table_args__ = (
        # Unique constraint on (user_id, organization_id) serves two purposes:
        # 1. Data Integrity: A user cannot join the same org twice.
        # 2. Performance: implicitly creates a composite index for optimizing user-org lookups.
        UniqueConstraint("user_id", "organization_id", name="uq_user_org"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    role: OrgRole = Field(
        sa_column=Column(SAEnum(OrgRole), nullable=False, default=OrgRole.MEMBER)
    )
    joined_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
    )
