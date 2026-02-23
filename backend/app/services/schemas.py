"""
Service Catalog schemas (DTOs) for API request/response validation.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.models import ServiceLifecycle, ServiceStatus, ServiceTier


# === Request Schemas ===


class ServiceCreate(BaseModel):
    """Schema for creating a new service."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    tier: ServiceTier = ServiceTier.MEDIUM
    lifecycle: ServiceLifecycle = ServiceLifecycle.ACTIVE
    category: str | None = Field(default=None, max_length=100)
    owner_id: uuid.UUID | None = None
    support_hours: str | None = Field(default=None, max_length=50)
    sla_tier: str | None = Field(default=None, max_length=50)
    documentation_url: str | None = Field(default=None, max_length=512)


class ServiceUpdate(BaseModel):
    """Schema for updating an existing service (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ServiceStatus | None = None
    tier: ServiceTier | None = None
    lifecycle: ServiceLifecycle | None = None
    category: str | None = Field(default=None, max_length=100)
    owner_id: uuid.UUID | None = None
    support_hours: str | None = Field(default=None, max_length=50)
    sla_tier: str | None = Field(default=None, max_length=50)
    documentation_url: str | None = Field(default=None, max_length=512)


# === Response Schemas ===


class ServiceResponse(BaseModel):
    """Full service detail response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    status: ServiceStatus
    tier: ServiceTier
    lifecycle: ServiceLifecycle
    category: str | None
    owner_id: uuid.UUID | None
    support_hours: str | None
    sla_tier: str | None
    documentation_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceListItem(BaseModel):
    """Compact service listing for tables/cards."""

    id: uuid.UUID
    name: str
    slug: str
    status: ServiceStatus
    tier: ServiceTier
    lifecycle: ServiceLifecycle
    category: str | None
    owner_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
