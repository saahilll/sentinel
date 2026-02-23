"""
Service Catalog domain model.
Represents IT services in the ITSM service catalog.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class ServiceStatus(str, Enum):
    """Current operational status of a service."""

    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"


class ServiceTier(str, Enum):
    """Business criticality tier (drives SLA expectations)."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ServiceLifecycle(str, Enum):
    """ITIL service portfolio lifecycle stage."""

    PIPELINE = "pipeline"   # Planned / under development
    ACTIVE = "active"       # Live in the service catalog
    RETIRED = "retired"     # Decommissioned


class Service(SQLModel, table=True):
    """
    IT Service in the service catalog.
    Maps to 'services' table in PostgreSQL.
    """

    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_org_service_slug"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    name: str = Field(max_length=255)
    slug: str = Field(max_length=100)
    description: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    status: ServiceStatus = Field(
        sa_column=Column(
            SAEnum(ServiceStatus), nullable=False, default=ServiceStatus.OPERATIONAL
        )
    )
    tier: ServiceTier = Field(
        sa_column=Column(
            SAEnum(ServiceTier), nullable=False, default=ServiceTier.MEDIUM
        )
    )
    lifecycle: ServiceLifecycle = Field(
        sa_column=Column(
            SAEnum(ServiceLifecycle), nullable=False, default=ServiceLifecycle.ACTIVE
        )
    )
    category: str | None = Field(default=None, max_length=100)
    owner_id: uuid.UUID | None = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    support_hours: str | None = Field(default=None, max_length=50)
    sla_tier: str | None = Field(default=None, max_length=50)
    documentation_url: str | None = Field(default=None, max_length=512)
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
