"""
User repository for data access operations.
Implements the Repository Pattern for data layer abstraction.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models.user import User


class UserRepository:
    """
    Repository for User entity CRUD operations.
    Abstracts database operations from business logic.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Persist a new user to the database."""
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Find a user by their ID."""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by their email address."""
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update an existing user."""
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete a user from the database."""
        await self.session.delete(user)
        await self.session.flush()

    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists."""
        user = await self.get_by_email(email)
        return user is not None
