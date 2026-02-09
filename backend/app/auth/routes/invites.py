"""
Organization invite endpoints.
Tenant-scoped routes for managing invitations.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.core.tenant import require_admin_or_owner, verify_tenant_access
from app.auth.models.membership import UserOrganization
from app.auth.models.organization import Organization
from app.auth.schemas import InviteRequest, InviteResponse, MessageResponse
from app.auth.services.invite import InviteService

router = APIRouter(tags=["Invitations"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/{tenant}/invites",
    response_model=InviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to organization",
)
@limiter.limit("10/minute")
async def create_invite(
    request: Request,
    tenant: str,
    invite_data: InviteRequest,
    org_access: tuple[Organization, UserOrganization] = Depends(require_admin_or_owner),
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    """Invite a user to join the organization. Requires admin or owner role."""
    organization, membership = org_access
    invite_service = InviteService(db)

    try:
        invitation = await invite_service.create_invite(
            org_slug=tenant,
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
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.message),
        )


@router.get(
    "/{tenant}/invites",
    response_model=list[InviteResponse],
    summary="List pending invites",
)
async def list_invites(
    tenant: str,
    org_access: tuple[Organization, UserOrganization] = Depends(verify_tenant_access),
    db: AsyncSession = Depends(get_db),
) -> list[InviteResponse]:
    """List all pending invitations for the organization."""
    organization, membership = org_access
    invite_service = InviteService(db)

    try:
        invitations = await invite_service.list_pending_invites(
            org_slug=tenant,
            user_id=membership.user_id,
        )
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
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )


@router.delete(
    "/{tenant}/invites/{invite_id}",
    response_model=MessageResponse,
    summary="Revoke invitation",
)
async def revoke_invite(
    tenant: str,
    invite_id: uuid.UUID,
    org_access: tuple[Organization, UserOrganization] = Depends(require_admin_or_owner),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke a pending invitation. Requires admin or owner role."""
    organization, membership = org_access
    invite_service = InviteService(db)

    try:
        await invite_service.revoke_invite(
            org_slug=tenant,
            invite_id=invite_id,
            user_id=membership.user_id,
        )
        return MessageResponse(message="Invitation revoked")
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
