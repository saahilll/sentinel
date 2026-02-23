"""
Service Catalog business logic.
Handles slug generation, validation, and orchestration.
"""

import re
import uuid

from app.core.exceptions import ConflictError, NotFoundError
from app.services.models import Service
from app.services.repository import ServiceRepository
from app.services.schemas import ServiceCreate, ServiceUpdate


class ServiceService:
    """Business logic for the service catalog."""

    def __init__(self, repo: ServiceRepository):
        self.repo = repo

    # ── Queries ────────────────────────────────────────────────────

    async def list_services(
        self,
        org_id: uuid.UUID,
        lifecycle: str | None = None,
    ) -> list[Service]:
        """List services for an organization."""
        from app.services.models import ServiceLifecycle

        lc = ServiceLifecycle(lifecycle) if lifecycle else None
        return await self.repo.list_by_org(org_id, lifecycle=lc)

    async def get_service(
        self, org_id: uuid.UUID, service_id: uuid.UUID
    ) -> Service:
        """Get a single service or raise NotFoundError."""
        service = await self.repo.get_by_id(org_id, service_id)
        if service is None:
            raise NotFoundError("Service")
        return service

    # ── Commands ───────────────────────────────────────────────────

    async def create_service(
        self, org_id: uuid.UUID, data: ServiceCreate
    ) -> Service:
        """Create a new service with an auto-generated slug."""
        slug = self._slugify(data.name)
        slug = await self._ensure_unique_slug(org_id, slug)

        service = Service(
            organization_id=org_id,
            name=data.name,
            slug=slug,
            description=data.description,
            tier=data.tier,
            lifecycle=data.lifecycle,
            category=data.category,
            owner_id=data.owner_id,
            support_hours=data.support_hours,
            sla_tier=data.sla_tier,
            documentation_url=data.documentation_url,
        )
        return await self.repo.create(service)

    async def update_service(
        self,
        org_id: uuid.UUID,
        service_id: uuid.UUID,
        data: ServiceUpdate,
    ) -> Service:
        """Partial-update an existing service."""
        service = await self.get_service(org_id, service_id)

        update_data = data.model_dump(exclude_unset=True)

        # If name changed, regenerate slug
        if "name" in update_data and update_data["name"] != service.name:
            new_slug = self._slugify(update_data["name"])
            new_slug = await self._ensure_unique_slug(org_id, new_slug)
            service.slug = new_slug

        for field, value in update_data.items():
            setattr(service, field, value)

        return await self.repo.update(service)

    async def delete_service(
        self, org_id: uuid.UUID, service_id: uuid.UUID
    ) -> None:
        """Delete a service."""
        service = await self.get_service(org_id, service_id)
        await self.repo.delete(service)

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to a URL-safe slug."""
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:100]

    async def _ensure_unique_slug(
        self, org_id: uuid.UUID, base_slug: str
    ) -> str:
        """Append a numeric suffix if the slug already exists in this org."""
        slug = base_slug
        counter = 1
        while await self.repo.slug_exists(org_id, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
