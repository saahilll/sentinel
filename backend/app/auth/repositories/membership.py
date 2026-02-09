"""
Membership repository for user-organization relationships.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization


class MembershipRepository:
    """Repository for UserOrganization join table operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, membership: UserOrganization) -> UserOrganization:
        """Create a new user-organization membership."""
        self.session.add(membership)
        await self.session.flush()
        await self.session.refresh(membership)
        return membership

    async def get_user_organizations(
        self, user_id: uuid.UUID
    ) -> list[tuple[Organization, OrgRole]]:
        """Get all organizations a user belongs to with their role."""
        statement = (
            select(Organization, UserOrganization.role)
            .join(UserOrganization, Organization.id == UserOrganization.organization_id)
            .where(UserOrganization.user_id == user_id)
            .where(Organization.is_active == True)  # noqa: E712
        )
        result = await self.session.execute(statement)
        return list(result.all())

    async def get_membership(
        self, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> UserOrganization | None:
        """Get a specific user-organization membership."""
        statement = select(UserOrganization).where(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == org_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_member(self, user_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        """Check if a user is a member of an organization."""
        membership = await self.get_membership(user_id, org_id)
        return membership is not None
