"""
Organization access control utilities.
Ensures users can only access their own organization data.
"""

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, get_db
from app.core.exceptions import AuthorizationError, NotFoundError
from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository


async def verify_organization_access(
    organization_slug: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> tuple[Organization, UserOrganization]:
    """
    Verify user has access to the specified organization.

    Args:
        organization_slug: Organization slug from URL path
        user_id: Authenticated user ID from JWT
        db: Database session

    Returns:
        Tuple of (Organization, UserOrganization) for further role checks

    Raises:
        NotFoundError: Organization not found
        AuthorizationError: User not a member
    """
    org_repo = OrganizationRepository(db)
    membership_repo = MembershipRepository(db)

    # Get organization by slug
    organization = await org_repo.get_by_slug(organization_slug)
    if organization is None:
        raise NotFoundError("Organization")

    # Verify user is a member
    membership = await membership_repo.get_membership(
        uuid.UUID(user_id), organization.id
    )
    if membership is None:
        raise AuthorizationError("Access denied: not a member of this organization")

    return organization, membership


async def require_admin_or_owner(
    org_access: tuple[Organization, UserOrganization] = Depends(verify_organization_access),
) -> tuple[Organization, UserOrganization]:
    """
    Require user to be admin or owner of the organization.

    Use after verify_organization_access for protected operations.
    """
    organization, membership = org_access

    if membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
        raise AuthorizationError("Admin or owner access required")

    return organization, membership


async def require_owner(
    org_access: tuple[Organization, UserOrganization] = Depends(verify_organization_access),
) -> tuple[Organization, UserOrganization]:
    """
    Require user to be owner of the organization.

    Use for destructive operations like org deletion.
    """
    organization, membership = org_access

    if membership.role != OrgRole.OWNER:
        raise AuthorizationError("Owner access required")

    return organization, membership
