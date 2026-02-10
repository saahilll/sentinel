"""
Organization domain model using SQLModel.
Represents a tenant in the multi-tenant system.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class Organization(SQLModel, table=True):
    """
    Organization (tenant) database model.
    Maps to 'organizations' table in PostgreSQL.
    """

    __tablename__ = "organizations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    slug: str = Field(
        sa_column=Column(String(100), unique=True, index=True, nullable=False)
    )
    description: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=512)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
    )

