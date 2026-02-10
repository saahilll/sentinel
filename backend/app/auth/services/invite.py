"""
Invite service for managing organization invitations.
Handles all invitation lifecycle: create, validate, accept, list, revoke.
"""

import uuid

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.auth.models.invitation import Invitation
from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization
from app.auth.models.user import User
from app.auth.repositories.invitation import InvitationRepository
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas import (
    InviteRequest,
    InviteValidation,
    LoginResponse,
    OrganizationBrief,
    TokenResponse,
    UserCreateInvite,
)
from app.core.security import create_access_token, create_refresh_token


class InviteService:
    """
    Service for invitation operations.
    Receives repositories via dependency injection.
    """

    def __init__(
        self,
        invite_repo: InvitationRepository,
        org_repo: OrganizationRepository,
        membership_repo: MembershipRepository,
        user_repo: UserRepository,
    ):
        self.invite_repo = invite_repo
        self.org_repo = org_repo
        self.membership_repo = membership_repo
        self.user_repo = user_repo

    async def create_invite(
        self,
        org_id: uuid.UUID,
        invite_data: InviteRequest,
        inviter_id: uuid.UUID,
    ) -> Invitation:
        """
        Create an invitation for a user to join an organization.

        Authorization is handled by the route layer via Depends().
        This method only handles business logic.
        """
        # Check if user is already a member
        existing_user = await self.user_repo.get_by_email(invite_data.email)
        if existing_user:
            existing_membership = await self.membership_repo.get_membership(
                existing_user.id, org_id
            )
            if existing_membership:
                raise ConflictError("User is already a member")

        # Check for existing pending invite
        existing_invite = await self.invite_repo.get_by_email_and_org(
            invite_data.email, org_id
        )
        if existing_invite:
            raise ConflictError("Invitation already sent to this email")

        # Create invitation
        invitation = Invitation(
            organization_id=org_id,
            email=invite_data.email,
            role=invite_data.role,
            invited_by=inviter_id,
        )
        invitation = await self.invite_repo.create(invitation)

        return invitation

    async def create_invites_for_registration(
        self, org_id: uuid.UUID, invites: list[InviteRequest], inviter_id: uuid.UUID
    ) -> None:
        """Create invitations during organization registration."""
        for invite_data in invites:
            invitation = Invitation(
                organization_id=org_id,
                email=invite_data.email,
                role=invite_data.role,
                invited_by=inviter_id,
            )
            await self.invite_repo.create(invitation)

    async def validate_invite(self, token: str) -> InviteValidation:
        """Validate an invitation token and return typed details."""
        invitation = await self.invite_repo.get_by_token(token)

        if invitation is None:
            return InviteValidation(
                is_valid=False, email="", organization_name="", role=""
            )

        if invitation.is_expired:
            return InviteValidation(
                is_valid=False, email=invitation.email, organization_name="", role=""
            )

        if invitation.is_accepted:
            return InviteValidation(
                is_valid=False, email=invitation.email, organization_name="", role=""
            )

        organization = await self.org_repo.get_by_id(invitation.organization_id)

        return InviteValidation(
            is_valid=True,
            email=invitation.email,
            organization_name=organization.name if organization else "",
            role=invitation.role.value,
        )

    async def register_with_invite(
        self, user_data: UserCreateInvite, invite_token: str
    ) -> LoginResponse:
        """Register a new user using an invitation token."""
        # Validate invitation
        invitation = await self.invite_repo.get_by_token(invite_token)

        if invitation is None:
            raise NotFoundError("Invitation")

        if invitation.is_expired:
            raise AuthenticationError("Invitation has expired")

        if invitation.is_accepted:
            raise ConflictError("Invitation already used")

        if invitation.email.lower() != user_data.email.lower():
            raise AuthenticationError("Email does not match invitation")

        # Check if email already exists
        if await self.user_repo.exists_by_email(user_data.email):
            raise ConflictError("Email already registered")

        # Get organization
        organization = await self.org_repo.get_by_id(invitation.organization_id)
        if organization is None:
            raise NotFoundError("Organization")

        # Create user
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        user = await self.user_repo.create(user)

        # Create membership with invited role
        membership = UserOrganization(
            user_id=user.id,
            organization_id=organization.id,
            role=invitation.role,
        )
        await self.membership_repo.create(membership)

        # Mark invitation as accepted
        await self.invite_repo.mark_accepted(invitation)

        # Generate tokens and return with org info
        tokens = self._create_tokens(str(user.id))
        return LoginResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            organizations=[
                OrganizationBrief(
                    id=organization.id,
                    name=organization.name,
                    slug=organization.slug,
                    role=invitation.role.value,
                )
            ],
        )

    async def accept_invite(self, user_id: str, invite_token: str) -> OrganizationBrief:
        """
        Accept an invitation for an existing authenticated user.
        Adds user to the organization without re-registering.
        """
        # Validate invitation
        invitation = await self.invite_repo.get_by_token(invite_token)

        if invitation is None:
            raise NotFoundError("Invitation")

        if invitation.is_expired:
            raise AuthenticationError("Invitation has expired")

        if invitation.is_accepted:
            raise ConflictError("Invitation already used")

        # Get user
        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise NotFoundError("User")

        # Verify email matches
        if invitation.email.lower() != user.email.lower():
            raise AuthenticationError("Invitation was sent to a different email")

        # Get organization
        organization = await self.org_repo.get_by_id(invitation.organization_id)
        if organization is None:
            raise NotFoundError("Organization")

        # Check if already a member
        existing = await self.membership_repo.get_membership(user.id, organization.id)
        if existing:
            raise ConflictError("Already a member of this organization")

        # Create membership
        membership = UserOrganization(
            user_id=user.id,
            organization_id=organization.id,
            role=invitation.role,
        )
        await self.membership_repo.create(membership)

        # Mark invitation as accepted
        await self.invite_repo.mark_accepted(invitation)

        return OrganizationBrief(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            role=invitation.role.value,
        )

    async def list_pending_invites(self, org_id: uuid.UUID) -> list[Invitation]:
        """List all pending invitations for an organization."""
        return await self.invite_repo.get_pending_by_org(org_id)

    async def revoke_invite(
        self, org_id: uuid.UUID, invite_id: uuid.UUID
    ) -> None:
        """Revoke (delete) an invitation."""
        invitation = await self.invite_repo.get_by_id(invite_id)
        if invitation is None or invitation.organization_id != org_id:
            raise NotFoundError("Invitation")

        await self.invite_repo.delete(invitation)

    def _create_tokens(self, user_id: str) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
