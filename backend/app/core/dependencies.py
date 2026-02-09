"""
FastAPI dependency injection utilities.
Provides reusable dependencies for routes.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import credentials_exception
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
        raise credentials_exception()

    user_id: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    if user_id is None or token_type != "access":
        raise credentials_exception()

    return user_id
