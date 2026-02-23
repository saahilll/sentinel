"""
Incident repository — database operations for incidents and attachments.
"""

import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.incidents.models import (
    Incident,
    IncidentAttachment,
    IncidentImpact,
    IncidentPriority,
    IncidentSource,
    IncidentStatus,
    IncidentUrgency,
)


class IncidentRepository:
    """Repository for Incident CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Incident Queries ──────────────────────────────────────────

    async def list_by_org(
        self,
        org_id: uuid.UUID,
        *,
        status: IncidentStatus | None = None,
        priority: IncidentPriority | None = None,
        service_id: uuid.UUID | None = None,
        assigned_to: uuid.UUID | None = None,
    ) -> list[Incident]:
        """List incidents for an organization with optional filters."""
        statement = (
            select(Incident)
            .where(Incident.organization_id == org_id)
            .order_by(Incident.created_at.desc())
        )
        if status is not None:
            statement = statement.where(Incident.status == status)
        if priority is not None:
            statement = statement.where(Incident.priority == priority)
        if service_id is not None:
            statement = statement.where(Incident.service_id == service_id)
        if assigned_to is not None:
            statement = statement.where(Incident.assigned_to == assigned_to)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id(
        self, org_id: uuid.UUID, incident_id: uuid.UUID
    ) -> Incident | None:
        """Get a single incident by ID within an organization."""
        statement = select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id == org_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, incident: Incident) -> Incident:
        """Insert a new incident."""
        self.session.add(incident)
        await self.session.flush()
        await self.session.refresh(incident)
        return incident

    async def update(self, incident: Incident) -> Incident:
        """Persist changes to an existing incident."""
        self.session.add(incident)
        await self.session.flush()
        await self.session.refresh(incident)
        return incident

    async def get_next_number(self, org_id: uuid.UUID) -> str:
        """Generate next incident number for an org (INC-001, INC-002, ...)."""
        statement = (
            select(func.count())
            .select_from(Incident)
            .where(Incident.organization_id == org_id)
        )
        result = await self.session.execute(statement)
        count = (result.scalar() or 0) + 1
        return f"INC-{count:03d}"

    # ── Attachment Queries ────────────────────────────────────────

    async def list_attachments(
        self, incident_id: uuid.UUID
    ) -> list[IncidentAttachment]:
        """List all attachments for an incident."""
        statement = (
            select(IncidentAttachment)
            .where(IncidentAttachment.incident_id == incident_id)
            .order_by(IncidentAttachment.created_at)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add_attachment(
        self, attachment: IncidentAttachment
    ) -> IncidentAttachment:
        """Save attachment metadata."""
        self.session.add(attachment)
        await self.session.flush()
        await self.session.refresh(attachment)
        return attachment

    async def get_attachment(
        self, attachment_id: uuid.UUID
    ) -> IncidentAttachment | None:
        """Get attachment by ID."""
        statement = select(IncidentAttachment).where(
            IncidentAttachment.id == attachment_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete_attachment(self, attachment: IncidentAttachment) -> None:
        """Delete attachment metadata."""
        await self.session.delete(attachment)
        await self.session.flush()

    # ── Stats ─────────────────────────────────────────────────────

    async def count_by_status(
        self, org_id: uuid.UUID
    ) -> dict[str, int]:
        """Count incidents grouped by status (for dashboard)."""
        statement = (
            select(Incident.status, func.count())
            .where(Incident.organization_id == org_id)
            .group_by(Incident.status)
        )
        result = await self.session.execute(statement)
        return {row[0].value: row[1] for row in result.all()}

    async def count_by_priority(
        self, org_id: uuid.UUID
    ) -> dict[str, int]:
        """Count incidents grouped by priority (for dashboard)."""
        statement = (
            select(Incident.priority, func.count())
            .where(Incident.organization_id == org_id)
            .where(Incident.status.notin_([IncidentStatus.CLOSED, IncidentStatus.RESOLVED]))
            .group_by(Incident.priority)
        )
        result = await self.session.execute(statement)
        return {row[0].value: row[1] for row in result.all()}
