"""
Incident Management API routes.
All endpoints are org-scoped via verify_organization_access.
"""

import uuid

from fastapi import APIRouter, Depends

from app.auth.models.membership import UserOrganization
from app.auth.models.organization import Organization
from app.core.dependencies import get_current_user_id, get_incident_service
from app.core.organization import verify_organization_access
from app.incidents.schemas import (
    AttachmentResponse,
    IncidentCreate,
    IncidentListItem,
    IncidentResponse,
    IncidentUpdate,
)

router = APIRouter(prefix="/orgs/{organization_slug}/incidents", tags=["Incidents"])


@router.get("", response_model=list[IncidentListItem])
async def list_incidents(
    status: str | None = None,
    priority: str | None = None,
    service_id: uuid.UUID | None = None,
    assigned_to: uuid.UUID | None = None,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_incident_service),
):
    """List incidents with optional filters."""
    org, _ = org_access
    return await svc.list_incidents(
        org.id,
        status=status,
        priority=priority,
        service_id=service_id,
        assigned_to=assigned_to,
    )


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    user_id: str = Depends(get_current_user_id),
    svc: object = Depends(get_incident_service),
):
    """Create a new incident."""
    org, _ = org_access
    incident = await svc.create_incident(org.id, uuid.UUID(user_id), data)
    return incident


@router.get("/stats")
async def get_incident_stats(
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_incident_service),
):
    """Get incident statistics for dashboard."""
    org, _ = org_access
    return await svc.get_stats(org.id)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_incident_service),
):
    """Get an incident with its attachments."""
    org, _ = org_access
    incident, attachments = await svc.get_incident_with_attachments(
        org.id, incident_id
    )
    response = IncidentResponse.model_validate(incident)
    response.attachments = [
        AttachmentResponse.model_validate(a) for a in attachments
    ]
    return response


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    data: IncidentUpdate,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_incident_service),
):
    """Update an incident (status transitions, assignment, diagnosis, etc.)."""
    org, _ = org_access
    return await svc.update_incident(org.id, incident_id, data)


@router.delete("/{incident_id}/attachments/{attachment_id}", status_code=204)
async def delete_attachment(
    incident_id: uuid.UUID,
    attachment_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_incident_service),
):
    """Delete an attachment from an incident."""
    org, _ = org_access
    await svc.delete_attachment(org.id, incident_id, attachment_id)
