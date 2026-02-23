"""
Service Catalog repository — database operations for services.
"""

import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.services.models import Service, ServiceLifecycle


class ServiceRepository:
    """Repository for Service CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_org(
        self,
        org_id: uuid.UUID,
        lifecycle: ServiceLifecycle | None = None,
    ) -> list[Service]:
        """List all services for an organization, optionally filtered by lifecycle."""
        statement = (
            select(Service)
            .where(Service.organization_id == org_id)
            .order_by(Service.name)
        )
        if lifecycle is not None:
            statement = statement.where(Service.lifecycle == lifecycle)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id(
        self, org_id: uuid.UUID, service_id: uuid.UUID
    ) -> Service | None:
        """Get a service by ID within an organization."""
        statement = select(Service).where(
            Service.id == service_id,
            Service.organization_id == org_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_slug(
        self, org_id: uuid.UUID, slug: str
    ) -> Service | None:
        """Get a service by slug within an organization."""
        statement = select(Service).where(
            Service.organization_id == org_id,
            Service.slug == slug,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, service: Service) -> Service:
        """Insert a new service."""
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def update(self, service: Service) -> Service:
        """Persist changes to an existing service."""
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def delete(self, service: Service) -> None:
        """Hard-delete a service."""
        await self.session.delete(service)
        await self.session.flush()

    async def slug_exists(self, org_id: uuid.UUID, slug: str) -> bool:
        """Check if a slug is already taken within an organization."""
        statement = select(func.count()).where(
            Service.organization_id == org_id,
            Service.slug == slug,
        )
        result = await self.session.execute(statement)
        return (result.scalar() or 0) > 0
