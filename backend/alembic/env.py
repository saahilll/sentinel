"""
Alembic environment configuration for async SQLModel migrations.
Reads DATABASE_URL from .env and uses SQLModel metadata for autogenerate.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context

# Import all models so they register with SQLModel.metadata
from app.auth.models.user import User  # noqa: F401
from app.auth.models.organization import Organization  # noqa: F401
from app.auth.models.membership import UserOrganization  # noqa: F401
from app.auth.models.invitation import Invitation  # noqa: F401
from app.services.models import Service  # noqa: F401
from app.incidents.models import Incident, IncidentAttachment  # noqa: F401

# Alembic Config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load DATABASE_URL from .env if not already set in alembic.ini
if not config.get_main_option("sqlalchemy.url"):
    from app.core.config import get_settings

    settings = get_settings()
    config.set_main_option("sqlalchemy.url", settings.database_url)

# SQLModel metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
