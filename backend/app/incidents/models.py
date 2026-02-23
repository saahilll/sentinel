"""
Incident Management domain models.
ITIL-aligned incident record with Impact × Urgency → Priority matrix.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class IncidentStatus(str, Enum):
    """ITIL incident lifecycle states."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentImpact(str, Enum):
    """Breadth of business impact (how many users / services affected)."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentUrgency(str, Enum):
    """How quickly the incident needs resolution."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentPriority(str, Enum):
    """Computed from Impact × Urgency (ServiceNow / ITIL matrix)."""

    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low


class IncidentSource(str, Enum):
    """How the incident was reported."""

    PORTAL = "portal"
    EMAIL = "email"
    MONITORING = "monitoring"
    API = "api"
    PHONE = "phone"


# ── Priority Matrix ──────────────────────────────────────────────

PRIORITY_MATRIX: dict[tuple[IncidentImpact, IncidentUrgency], IncidentPriority] = {
    (IncidentImpact.HIGH, IncidentUrgency.HIGH): IncidentPriority.P1,
    (IncidentImpact.HIGH, IncidentUrgency.MEDIUM): IncidentPriority.P2,
    (IncidentImpact.HIGH, IncidentUrgency.LOW): IncidentPriority.P3,
    (IncidentImpact.MEDIUM, IncidentUrgency.HIGH): IncidentPriority.P2,
    (IncidentImpact.MEDIUM, IncidentUrgency.MEDIUM): IncidentPriority.P3,
    (IncidentImpact.MEDIUM, IncidentUrgency.LOW): IncidentPriority.P4,
    (IncidentImpact.LOW, IncidentUrgency.HIGH): IncidentPriority.P3,
    (IncidentImpact.LOW, IncidentUrgency.MEDIUM): IncidentPriority.P4,
    (IncidentImpact.LOW, IncidentUrgency.LOW): IncidentPriority.P4,
}


def compute_priority(
    impact: IncidentImpact, urgency: IncidentUrgency
) -> IncidentPriority:
    """Derive priority from the ITIL Impact × Urgency matrix."""
    return PRIORITY_MATRIX[(impact, urgency)]


# ── Incident Model ───────────────────────────────────────────────


class Incident(SQLModel, table=True):
    """
    ITSM Incident record.
    Maps to 'incidents' table in PostgreSQL.
    """

    __tablename__ = "incidents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    incident_number: str = Field(
        sa_column=Column(String(20), nullable=False, index=True)
    )

    # Core fields
    title: str = Field(max_length=500)
    description: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    # ITIL classification
    status: IncidentStatus = Field(
        sa_column=Column(
            SAEnum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN
        )
    )
    impact: IncidentImpact = Field(
        sa_column=Column(
            SAEnum(IncidentImpact), nullable=False, default=IncidentImpact.MEDIUM
        )
    )
    urgency: IncidentUrgency = Field(
        sa_column=Column(
            SAEnum(IncidentUrgency), nullable=False, default=IncidentUrgency.MEDIUM
        )
    )
    priority: IncidentPriority = Field(
        sa_column=Column(
            SAEnum(IncidentPriority), nullable=False, default=IncidentPriority.P3
        )
    )
    category: str | None = Field(default=None, max_length=100)
    subcategory: str | None = Field(default=None, max_length=100)
    source: IncidentSource = Field(
        sa_column=Column(
            SAEnum(IncidentSource), nullable=False, default=IncidentSource.PORTAL
        )
    )

    # Relationships
    service_id: uuid.UUID | None = Field(
        sa_column=Column(
            ForeignKey("services.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    assigned_to: uuid.UUID | None = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    reported_by: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    # Resolution fields
    diagnosis: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    solution: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    resolution_notes: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    # SLA & timestamps
    sla_due_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    acknowledged_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    resolved_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    closed_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
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


# ── Attachment Model ─────────────────────────────────────────────


class IncidentAttachment(SQLModel, table=True):
    """
    File attachment linked to an incident.
    Stores metadata; actual files live in object storage.
    """

    __tablename__ = "incident_attachments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    incident_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("incidents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    size_bytes: int = Field(sa_column=Column(Integer, nullable=False))
    storage_path: str = Field(
        max_length=512,
        description="Path or key in object storage (S3, local, etc.)",
    )
    uploaded_by: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
        )
    )
