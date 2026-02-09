"""
Invite service for managing organization invitations.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.auth.models.invitation import Invitation
from app.auth.models.membership import OrgRole
from app.auth.repositories.invitation import InvitationRepository
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas import InviteRequest


class InviteService:
    """Service for invitation operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.invite_repo = InvitationRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)
        self.user_repo = UserRepository(session)

    async def create_invite(
        self,
        org_slug: str,
        invite_data: InviteRequest,
        inviter_id: uuid.UUID,
    ) -> Invitation:
        """
        Create an invitation for a user to join an organization.

        Only admins and owners can create invites.
        """
        # Get organization
        organization = await self.org_repo.get_by_slug(org_slug)
        if organization is None:
            raise NotFoundError("Organization")

        # Verify inviter has permission (admin or owner)
        membership = await self.membership_repo.get_membership(
            inviter_id, organization.id
        )
        if membership is None:
            raise AuthenticationError("Not a member of this organization")

        if membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise AuthenticationError("Only admins and owners can invite")

        # Check if user is already a member
        existing_user = await self.user_repo.get_by_email(invite_data.email)
        if existing_user:
            existing_membership = await self.membership_repo.get_membership(
                existing_user.id, organization.id
            )
            if existing_membership:
                raise ConflictError("User is already a member")

        # Check for existing pending invite
        existing_invite = await self.invite_repo.get_by_email_and_org(
            invite_data.email, organization.id
        )
        if existing_invite:
            raise ConflictError("Invitation already sent to this email")

        # Create invitation
        invitation = Invitation(
            organization_id=organization.id,
            email=invite_data.email,
            role=invite_data.role,
            invited_by=inviter_id,
        )
        invitation = await self.invite_repo.create(invitation)

        return invitation

    async def list_pending_invites(
        self, org_slug: str, user_id: uuid.UUID
    ) -> list[Invitation]:
        """List all pending invitations for an organization."""
        organization = await self.org_repo.get_by_slug(org_slug)
        if organization is None:
            raise NotFoundError("Organization")

        # Verify user is a member
        membership = await self.membership_repo.get_membership(
            user_id, organization.id
        )
        if membership is None:
            raise AuthenticationError("Not a member of this organization")

        return await self.invite_repo.get_pending_by_org(organization.id)

    async def revoke_invite(
        self, org_slug: str, invite_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Revoke (delete) an invitation."""
        organization = await self.org_repo.get_by_slug(org_slug)
        if organization is None:
            raise NotFoundError("Organization")

        # Verify user has permission
        membership = await self.membership_repo.get_membership(
            user_id, organization.id
        )
        if membership is None or membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
            raise AuthenticationError("Permission denied")

        invitation = await self.invite_repo.get_by_id(invite_id)
        if invitation is None or invitation.organization_id != organization.id:
            raise NotFoundError("Invitation")

        await self.invite_repo.delete(invitation)
