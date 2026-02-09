"""
Organization repository for data access operations.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models.organization import Organization


class OrganizationRepository:
    """Repository for Organization entity CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, org: Organization) -> Organization:
        """Persist a new organization to the database."""
        self.session.add(org)
        await self.session.flush()
        await self.session.refresh(org)
        return org

    async def get_by_id(self, org_id: uuid.UUID) -> Organization | None:
        """Find an organization by ID."""
        statement = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        """Find an organization by its URL slug."""
        statement = select(Organization).where(Organization.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def exists_by_slug(self, slug: str) -> bool:
        """Check if an organization with the given slug exists."""
        org = await self.get_by_slug(slug)
        return org is not None
