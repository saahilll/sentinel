"""
Authentication service containing business logic.
Handles user registration, login, and token management.
"""

import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.auth.models.invitation import Invitation
from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization
from app.auth.models.user import User
from app.auth.repositories.invitation import InvitationRepository
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas import (
    LoginResponse,
    OrganizationBrief,
    TokenResponse,
    UserCreate,
    UserCreateInvite,
    UserLogin,
)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:100]


class AuthService:
    """
    Service class for authentication operations.
    Contains business logic, uses repository for data access.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)
        self.invite_repo = InvitationRepository(session)

    async def register(self, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user, create organization, and send invites.
        """
        # Check if email already exists
        if await self.user_repo.exists_by_email(user_data.email):
            raise ConflictError("Email already registered")

        # Generate unique slug for organization
        base_slug = slugify(user_data.organization_name)
        slug = base_slug
        counter = 1
        while await self.org_repo.exists_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create organization
        organization = Organization(
            name=user_data.organization_name,
            slug=slug,
        )
        organization = await self.org_repo.create(organization)

        # Create user with hashed password
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        user = await self.user_repo.create(user)

        # Create membership (user is owner of their org)
        membership = UserOrganization(
            user_id=user.id,
            organization_id=organization.id,
            role=OrgRole.OWNER,
        )
        await self.membership_repo.create(membership)

        # Create invitations for team members
        for invite_data in user_data.invites:
            invitation = Invitation(
                organization_id=organization.id,
                email=invite_data.email,
                role=invite_data.role,
                invited_by=user.id,
            )
            await self.invite_repo.create(invitation)

        # Generate tokens
        return self._create_tokens(str(user.id))

    async def register_with_invite(
        self, user_data: UserCreateInvite, invite_token: str
    ) -> LoginResponse:
        """
        Register a user using an invitation token.
        """
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

    async def login(self, credentials: UserLogin) -> LoginResponse:
        """
        Authenticate a user and return tokens with organization list.
        """
        user = await self.user_repo.get_by_email(credentials.email)

        if user is None:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(credentials.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        # Get user's organizations
        org_memberships = await self.membership_repo.get_user_organizations(user.id)
        organizations = [
            OrganizationBrief(
                id=org.id,
                name=org.name,
                slug=org.slug,
                role=role.value,
            )
            for org, role in org_memberships
        ]

        tokens = self._create_tokens(str(user.id))
        return LoginResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            organizations=organizations,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using a valid refresh token."""
        payload = decode_token(refresh_token)

        if payload is None:
            raise AuthenticationError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")

        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        return self._create_tokens(user_id)

    async def get_current_user(self, user_id: str) -> User:
        """Get the currently authenticated user."""
        user = await self.user_repo.get_by_id(uuid.UUID(user_id))

        if user is None:
            raise NotFoundError("User")

        return user

    async def validate_invite(self, token: str) -> dict:
        """Validate an invitation token and return details."""
        invitation = await self.invite_repo.get_by_token(token)

        if invitation is None:
            return {"is_valid": False, "error": "Invitation not found"}

        if invitation.is_expired:
            return {"is_valid": False, "error": "Invitation expired"}

        if invitation.is_accepted:
            return {"is_valid": False, "error": "Invitation already used"}

        organization = await self.org_repo.get_by_id(invitation.organization_id)

        return {
            "is_valid": True,
            "email": invitation.email,
            "organization_name": organization.name if organization else "",
            "role": invitation.role.value,
        }

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

        # Verify email matches (or allow different - depends on your policy)
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

    def _create_tokens(self, user_id: str) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

