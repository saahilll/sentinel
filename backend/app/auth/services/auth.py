"""
Authentication service containing core auth business logic.
Handles user registration, login, and token management.
"""

import uuid

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.utils import slugify
from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization
from app.auth.models.user import User
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas import (
    LoginResponse,
    OrganizationBrief,
    OrganizationCreate,
    OrganizationResponse,
    RegisterResult,
    TokenResponse,
    UserCreate,
    UserLogin,
)


class AuthService:
    """
    Service class for core authentication operations.
    Receives repositories via dependency injection.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        membership_repo: MembershipRepository,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.membership_repo = membership_repo

    async def register(self, user_data: UserCreate) -> RegisterResult:
        """Register a new user and create their organization."""
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

        # Generate tokens with org/user context for invite creation
        tokens = self._create_tokens(str(user.id))
        return RegisterResult(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user_id=user.id,
            organization_id=organization.id,
        )

    async def create_organization(
        self, user_id: str, org_data: OrganizationCreate
    ) -> OrganizationResponse:
        """
        Create a new organization for an existing authenticated user.
        The user becomes the owner of the new organization.
        """
        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise NotFoundError("User")

        # Generate unique slug
        base_slug = slugify(org_data.name)
        slug = base_slug
        counter = 1
        while await self.org_repo.exists_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create organization
        organization = Organization(
            name=org_data.name,
            slug=slug,
        )
        organization = await self.org_repo.create(organization)

        # Create membership (user is owner)
        membership = UserOrganization(
            user_id=user.id,
            organization_id=organization.id,
            role=OrgRole.OWNER,
        )
        await self.membership_repo.create(membership)

        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            role=OrgRole.OWNER.value,
            created_at=organization.created_at,
        )

    async def login(self, credentials: UserLogin) -> LoginResponse:
        """Authenticate a user and return tokens with organization list."""
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

    def _create_tokens(self, user_id: str) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
