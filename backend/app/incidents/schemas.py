"""
Incident schemas (DTOs) for API request/response validation.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.incidents.models import (
    IncidentImpact,
    IncidentPriority,
    IncidentSource,
    IncidentStatus,
    IncidentUrgency,
)


# === Request Schemas ===


class IncidentCreate(BaseModel):
    """Schema for creating a new incident."""

    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    impact: IncidentImpact = IncidentImpact.MEDIUM
    urgency: IncidentUrgency = IncidentUrgency.MEDIUM
    category: str | None = Field(default=None, max_length=100)
    subcategory: str | None = Field(default=None, max_length=100)
    source: IncidentSource = IncidentSource.PORTAL
    service_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None


class IncidentUpdate(BaseModel):
    """Schema for updating an incident (partial update)."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    status: IncidentStatus | None = None
    impact: IncidentImpact | None = None
    urgency: IncidentUrgency | None = None
    category: str | None = Field(default=None, max_length=100)
    subcategory: str | None = Field(default=None, max_length=100)
    service_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    diagnosis: str | None = None
    solution: str | None = None
    resolution_notes: str | None = None


# === Response Schemas ===


class AttachmentResponse(BaseModel):
    """Attachment metadata response."""

    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    uploaded_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class IncidentResponse(BaseModel):
    """Full incident detail response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    incident_number: str
    title: str
    description: str | None
    status: IncidentStatus
    impact: IncidentImpact
    urgency: IncidentUrgency
    priority: IncidentPriority
    category: str | None
    subcategory: str | None
    source: IncidentSource
    service_id: uuid.UUID | None
    assigned_to: uuid.UUID | None
    reported_by: uuid.UUID
    diagnosis: str | None
    solution: str | None
    resolution_notes: str | None
    sla_due_at: datetime | None
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentResponse] = []

    model_config = {"from_attributes": True}


class IncidentListItem(BaseModel):
    """Compact incident listing for tables."""

    id: uuid.UUID
    incident_number: str
    title: str
    status: IncidentStatus
    impact: IncidentImpact
    urgency: IncidentUrgency
    priority: IncidentPriority
    category: str | None
    source: IncidentSource
    service_id: uuid.UUID | None
    assigned_to: uuid.UUID | None
    reported_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
