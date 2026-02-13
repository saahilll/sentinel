"""
Organization invite endpoints.
Organization-scoped routes for managing invitations.
"""

import uuid

from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.dependencies import get_invite_service
from app.core.organization import require_admin_or_owner, verify_organization_access
from app.auth.models.membership import UserOrganization
from app.auth.models.organization import Organization
from app.auth.schemas import InviteRequest, InviteResponse, MessageResponse
from app.auth.services.invite import InviteService

router = APIRouter(tags=["Invitations"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/{organization_slug}/invites",
    response_model=InviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to organization",
)
@limiter.limit("10/minute")
async def create_invite(
    request: Request,
    organization_slug: str,
    invite_data: InviteRequest,
    org_access: tuple[Organization, UserOrganization] = Depends(require_admin_or_owner),
    invite_service: InviteService = Depends(get_invite_service),
) -> InviteResponse:
    """Invite a user to join the organization. Requires admin or owner role."""
    organization, membership = org_access
    invitation = await invite_service.create_invite(
        org_id=organization.id,
        invite_data=invite_data,
        inviter_id=membership.user_id,
    )
    return InviteResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role.value,
        token=invitation.token,
        expires_at=invitation.expires_at,
    )


@router.get(
    "/{organization_slug}/invites",
    response_model=list[InviteResponse],
    summary="List pending invites",
)
async def list_invites(
    organization_slug: str,
    org_access: tuple[Organization, UserOrganization] = Depends(verify_organization_access),
    invite_service: InviteService = Depends(get_invite_service),
) -> list[InviteResponse]:
    """List all pending invitations for the organization."""
    organization, membership = org_access
    invitations = await invite_service.list_pending_invites(org_id=organization.id)
    return [
        InviteResponse(
            id=inv.id,
            email=inv.email,
            role=inv.role.value,
            token=inv.token,
            expires_at=inv.expires_at,
        )
        for inv in invitations
    ]


@router.delete(
    "/{organization_slug}/invites/{invite_id}",
    response_model=MessageResponse,
    summary="Revoke invitation",
)
async def revoke_invite(
    organization_slug: str,
    invite_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(require_admin_or_owner),
    invite_service: InviteService = Depends(get_invite_service),
) -> MessageResponse:
    """Revoke a pending invitation. Requires admin or owner role."""
    organization, membership = org_access
    await invite_service.revoke_invite(
        org_id=organization.id,
        invite_id=invite_id,
    )
    return MessageResponse(message="Invitation revoked")
