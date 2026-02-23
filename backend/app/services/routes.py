"""
Service Catalog API routes.
All endpoints are org-scoped via verify_organization_access.
"""

import uuid

from fastapi import APIRouter, Depends

from app.auth.models.organization import Organization
from app.auth.models.membership import UserOrganization
from app.core.organization import verify_organization_access
from app.core.dependencies import get_service_service
from app.services.schemas import (
    ServiceCreate,
    ServiceListItem,
    ServiceResponse,
    ServiceUpdate,
)

router = APIRouter(prefix="/orgs/{organization_slug}/services", tags=["Services"])


@router.get("", response_model=list[ServiceListItem])
async def list_services(
    lifecycle: str | None = None,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_service_service),
):
    """List all services in the organization."""
    org, _ = org_access
    services = await svc.list_services(org.id, lifecycle=lifecycle)
    return services


@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(
    data: ServiceCreate,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_service_service),
):
    """Create a new service in the catalog."""
    org, _ = org_access
    service = await svc.create_service(org.id, data)
    return service


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_service_service),
):
    """Get a single service by ID."""
    org, _ = org_access
    return await svc.get_service(org.id, service_id)


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: uuid.UUID,
    data: ServiceUpdate,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_service_service),
):
    """Partial-update a service."""
    org, _ = org_access
    return await svc.update_service(org.id, service_id, data)


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(
        verify_organization_access
    ),
    svc: object = Depends(get_service_service),
):
    """Delete a service."""
    org, _ = org_access
    await svc.delete_service(org.id, service_id)
