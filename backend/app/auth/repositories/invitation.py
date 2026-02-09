"""
Invitation repository for data access operations.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models.invitation import Invitation


class InvitationRepository:
    """Repository for Invitation entity operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, invitation: Invitation) -> Invitation:
        """Create a new invitation."""
        self.session.add(invitation)
        await self.session.flush()
        await self.session.refresh(invitation)
        return invitation

    async def get_by_token(self, token: str) -> Invitation | None:
        """Find an invitation by its token."""
        statement = select(Invitation).where(Invitation.token == token)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, invite_id: uuid.UUID) -> Invitation | None:
        """Find an invitation by ID."""
        statement = select(Invitation).where(Invitation.id == invite_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email_and_org(
        self, email: str, org_id: uuid.UUID
    ) -> Invitation | None:
        """Find pending invitation for email in org."""
        statement = select(Invitation).where(
            Invitation.email == email,
            Invitation.organization_id == org_id,
            Invitation.accepted_at.is_(None),
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_pending_by_org(self, org_id: uuid.UUID) -> list[Invitation]:
        """Get all pending invitations for an organization."""
        statement = select(Invitation).where(
            Invitation.organization_id == org_id,
            Invitation.accepted_at.is_(None),
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def mark_accepted(self, invitation: Invitation) -> Invitation:
        """Mark an invitation as accepted."""
        invitation.accepted_at = datetime.now(timezone.utc)
        self.session.add(invitation)
        await self.session.flush()
        await self.session.refresh(invitation)
        return invitation

    async def delete(self, invitation: Invitation) -> None:
        """Delete an invitation."""
        await self.session.delete(invitation)
        await self.session.flush()
