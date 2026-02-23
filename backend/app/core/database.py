"""
Async database connection using SQLModel + asyncpg.
Provides session factory and table initialization.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import get_settings

settings = get_settings()

# Async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)

# Async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialize database tables.
    Called on application startup.
    """
    # Import models to register them with SQLModel.metadata
    from app.auth.models.invitation import Invitation  # noqa: F401
    from app.auth.models.membership import UserOrganization  # noqa: F401
    from app.auth.models.organization import Organization  # noqa: F401
    from app.auth.models.user import User  # noqa: F401
    from app.auth.models.token import RefreshToken, MagicLinkToken  # noqa: F401
    from app.services.models import Service  # noqa: F401
    from app.incidents.models import Incident, IncidentAttachment  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.
    Automatically handles commit/rollback and cleanup.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
