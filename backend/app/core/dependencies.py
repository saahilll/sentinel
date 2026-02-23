"""
FastAPI dependency injection utilities.
Provides reusable dependencies for routes.
Wires up the Repository → Service → Route chain.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import AuthenticationError
from app.core.security import decode_token

# OAuth2 scheme for Bearer token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_db() -> AsyncSession:
    """
    Database session dependency.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async for session in get_session():
        yield session


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract and validate user ID from JWT token.
    Usage: user_id: str = Depends(get_current_user_id)
    """
    payload = decode_token(token)
    if payload is None:
        raise AuthenticationError("Could not validate credentials")

    user_id: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    if user_id is None or token_type != "access":
        raise AuthenticationError("Could not validate credentials")

    return user_id


# --- Repository Providers ---

def get_user_repo(db: AsyncSession = Depends(get_db)):
    """Provide UserRepository instance."""
    from app.auth.repositories.user import UserRepository
    return UserRepository(db)


def get_token_repo(db: AsyncSession = Depends(get_db)):
    """Provide TokenRepository instance."""
    from app.auth.repositories.token import TokenRepository
    return TokenRepository(db)


def get_org_repo(db: AsyncSession = Depends(get_db)):
    """Provide OrganizationRepository instance."""
    from app.auth.repositories.organization import OrganizationRepository
    return OrganizationRepository(db)


def get_membership_repo(db: AsyncSession = Depends(get_db)):
    """Provide MembershipRepository instance."""
    from app.auth.repositories.membership import MembershipRepository
    return MembershipRepository(db)


def get_invite_repo(db: AsyncSession = Depends(get_db)):
    """Provide InvitationRepository instance."""
    from app.auth.repositories.invitation import InvitationRepository
    return InvitationRepository(db)


# --- Service Providers ---

def get_auth_service(
    user_repo=Depends(get_user_repo),
    token_repo=Depends(get_token_repo),
):
    """Provide AuthService with injected repositories."""
    from app.auth.services.auth import AuthService
    return AuthService(user_repo, token_repo)


def get_invite_service(
    invite_repo=Depends(get_invite_repo),
    org_repo=Depends(get_org_repo),
    membership_repo=Depends(get_membership_repo),
    user_repo=Depends(get_user_repo),
):
    """Provide InviteService with injected repositories."""
    from app.auth.services.invite import InviteService
    return InviteService(invite_repo, org_repo, membership_repo, user_repo)


# --- ITSM Repository Providers ---

def get_service_repo(db: AsyncSession = Depends(get_db)):
    """Provide ServiceRepository instance."""
    from app.services.repository import ServiceRepository
    return ServiceRepository(db)


def get_incident_repo(db: AsyncSession = Depends(get_db)):
    """Provide IncidentRepository instance."""
    from app.incidents.repository import IncidentRepository
    return IncidentRepository(db)


# --- ITSM Service Providers ---

def get_service_service(
    repo=Depends(get_service_repo),
):
    """Provide ServiceService with injected repository."""
    from app.services.service import ServiceService
    return ServiceService(repo)


def get_incident_service(
    repo=Depends(get_incident_repo),
):
    """Provide IncidentService with injected repository."""
    from app.incidents.service import IncidentService
    return IncidentService(repo)
