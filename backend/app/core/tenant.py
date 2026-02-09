"""
Tenant isolation and access control utilities.
Ensures users can only access their own organization data.
"""

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, get_db
from app.auth.models.membership import OrgRole, UserOrganization
from app.auth.models.organization import Organization
from app.auth.repositories.membership import MembershipRepository
from app.auth.repositories.organization import OrganizationRepository


async def verify_tenant_access(
    tenant: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> tuple[Organization, UserOrganization]:
    """
    Verify user has access to the specified tenant.

    Args:
        tenant: Organization slug from URL path
        user_id: Authenticated user ID from JWT
        db: Database session

    Returns:
        Tuple of (Organization, UserOrganization) for further role checks

    Raises:
        HTTPException 404: Organization not found
        HTTPException 403: User not a member
    """
    org_repo = OrganizationRepository(db)
    membership_repo = MembershipRepository(db)

    # Get organization by slug
    organization = await org_repo.get_by_slug(tenant)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Verify user is a member
    membership = await membership_repo.get_membership(
        uuid.UUID(user_id), organization.id
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not a member of this organization",
        )

    return organization, membership


async def require_admin_or_owner(
    org_access: tuple[Organization, UserOrganization] = Depends(verify_tenant_access),
) -> tuple[Organization, UserOrganization]:
    """
    Require user to be admin or owner of the organization.

    Use after verify_tenant_access for protected operations.
    """
    organization, membership = org_access

    if membership.role not in [OrgRole.OWNER, OrgRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or owner access required",
        )

    return organization, membership


async def require_owner(
    org_access: tuple[Organization, UserOrganization] = Depends(verify_tenant_access),
) -> tuple[Organization, UserOrganization]:
    """
    Require user to be owner of the organization.

    Use for destructive operations like org deletion.
    """
    organization, membership = org_access

    if membership.role != OrgRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )

    return organization, membership
