"""
Incident Management business logic.
Handles status transitions (state machine), priority computation, and numbering.
"""

import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, ValidationError
from app.incidents.models import (
    Incident,
    IncidentAttachment,
    IncidentImpact,
    IncidentPriority,
    IncidentStatus,
    IncidentUrgency,
    compute_priority,
)
from app.incidents.repository import IncidentRepository
from app.incidents.schemas import IncidentCreate, IncidentUpdate


# Valid status transitions (state machine)
VALID_TRANSITIONS: dict[IncidentStatus, set[IncidentStatus]] = {
    IncidentStatus.OPEN: {IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING, IncidentStatus.RESOLVED, IncidentStatus.CLOSED},
    IncidentStatus.ACKNOWLEDGED: {IncidentStatus.INVESTIGATING, IncidentStatus.RESOLVED, IncidentStatus.CLOSED},
    IncidentStatus.INVESTIGATING: {IncidentStatus.RESOLVED, IncidentStatus.CLOSED},
    IncidentStatus.RESOLVED: {IncidentStatus.CLOSED, IncidentStatus.OPEN},  # Reopen allowed
    IncidentStatus.CLOSED: {IncidentStatus.OPEN},  # Reopen allowed
}


class IncidentService:
    """Business logic for incident management."""

    def __init__(self, repo: IncidentRepository):
        self.repo = repo

    # ── Queries ────────────────────────────────────────────────────

    async def list_incidents(
        self,
        org_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
        service_id: uuid.UUID | None = None,
        assigned_to: uuid.UUID | None = None,
    ) -> list[Incident]:
        """List incidents with optional filters."""
        s = IncidentStatus(status) if status else None
        p = IncidentPriority(priority) if priority else None
        return await self.repo.list_by_org(
            org_id, status=s, priority=p,
            service_id=service_id, assigned_to=assigned_to,
        )

    async def get_incident(
        self, org_id: uuid.UUID, incident_id: uuid.UUID
    ) -> Incident:
        """Get an incident or raise NotFoundError."""
        incident = await self.repo.get_by_id(org_id, incident_id)
        if incident is None:
            raise NotFoundError("Incident")
        return incident

    async def get_incident_with_attachments(
        self, org_id: uuid.UUID, incident_id: uuid.UUID
    ) -> tuple[Incident, list[IncidentAttachment]]:
        """Get incident + its attachments for detail view."""
        incident = await self.get_incident(org_id, incident_id)
        attachments = await self.repo.list_attachments(incident_id)
        return incident, attachments

    # ── Commands ───────────────────────────────────────────────────

    async def create_incident(
        self,
        org_id: uuid.UUID,
        reported_by: uuid.UUID,
        data: IncidentCreate,
    ) -> Incident:
        """Create a new incident with auto-numbering and priority computation."""
        incident_number = await self.repo.get_next_number(org_id)
        priority = compute_priority(data.impact, data.urgency)

        incident = Incident(
            organization_id=org_id,
            incident_number=incident_number,
            title=data.title,
            description=data.description,
            status=IncidentStatus.OPEN,
            impact=data.impact,
            urgency=data.urgency,
            priority=priority,
            category=data.category,
            subcategory=data.subcategory,
            source=data.source,
            service_id=data.service_id,
            assigned_to=data.assigned_to,
            reported_by=reported_by,
        )
        return await self.repo.create(incident)

    async def update_incident(
        self,
        org_id: uuid.UUID,
        incident_id: uuid.UUID,
        data: IncidentUpdate,
    ) -> Incident:
        """Partial-update with status transition validation and priority recomputation."""
        incident = await self.get_incident(org_id, incident_id)
        update_data = data.model_dump(exclude_unset=True)
        now = datetime.now(timezone.utc)

        # Validate status transition
        if "status" in update_data:
            new_status = IncidentStatus(update_data["status"])
            self._validate_transition(incident.status, new_status)
            self._apply_status_timestamps(incident, new_status, now)

        # Recompute priority if impact or urgency changed
        new_impact = update_data.get("impact", incident.impact)
        new_urgency = update_data.get("urgency", incident.urgency)
        if "impact" in update_data or "urgency" in update_data:
            if isinstance(new_impact, str):
                new_impact = IncidentImpact(new_impact)
            if isinstance(new_urgency, str):
                new_urgency = IncidentUrgency(new_urgency)
            update_data["priority"] = compute_priority(new_impact, new_urgency)

        for field, value in update_data.items():
            setattr(incident, field, value)

        return await self.repo.update(incident)

    # ── Attachments ────────────────────────────────────────────────

    async def add_attachment(
        self,
        org_id: uuid.UUID,
        incident_id: uuid.UUID,
        *,
        filename: str,
        content_type: str,
        size_bytes: int,
        storage_path: str,
        uploaded_by: uuid.UUID,
    ) -> IncidentAttachment:
        """Add an attachment to an incident."""
        # Verify incident exists
        await self.get_incident(org_id, incident_id)

        attachment = IncidentAttachment(
            incident_id=incident_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_path=storage_path,
            uploaded_by=uploaded_by,
        )
        return await self.repo.add_attachment(attachment)

    async def delete_attachment(
        self,
        org_id: uuid.UUID,
        incident_id: uuid.UUID,
        attachment_id: uuid.UUID,
    ) -> None:
        """Delete an attachment from an incident."""
        await self.get_incident(org_id, incident_id)
        attachment = await self.repo.get_attachment(attachment_id)
        if attachment is None or attachment.incident_id != incident_id:
            raise NotFoundError("Attachment")
        await self.repo.delete_attachment(attachment)

    # ── Dashboard Stats ────────────────────────────────────────────

    async def get_stats(self, org_id: uuid.UUID) -> dict:
        """Get dashboard statistics."""
        by_status = await self.repo.count_by_status(org_id)
        by_priority = await self.repo.count_by_priority(org_id)
        return {
            "by_status": by_status,
            "by_priority": by_priority,
            "total_open": sum(
                v for k, v in by_status.items()
                if k not in ("resolved", "closed")
            ),
        }

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _validate_transition(
        current: IncidentStatus, target: IncidentStatus
    ) -> None:
        """Enforce the status state machine."""
        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ValidationError(
                f"Cannot transition from '{current.value}' to '{target.value}'"
            )

    @staticmethod
    def _apply_status_timestamps(
        incident: Incident,
        new_status: IncidentStatus,
        now: datetime,
    ) -> None:
        """Set lifecycle timestamps when status changes."""
        if new_status == IncidentStatus.ACKNOWLEDGED and incident.acknowledged_at is None:
            incident.acknowledged_at = now
        elif new_status == IncidentStatus.RESOLVED:
            incident.resolved_at = now
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = now
        elif new_status == IncidentStatus.OPEN:
            # Reopen: clear resolution timestamps
            incident.resolved_at = None
            incident.closed_at = None
