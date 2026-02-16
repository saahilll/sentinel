import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel, Relationship

class RefreshToken(SQLModel, table=True):
    __tablename__ = "auth_refresh_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    token_family: uuid.UUID = Field(default_factory=uuid.uuid4, index=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), index=True))
    is_revoked: bool = Field(default=False)
    device_info: str = Field(default="", max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    location: str = Field(default="", max_length=100)
    last_used_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True))
    )

class MagicLinkToken(SQLModel, table=True):
    __tablename__ = "auth_magic_link_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, max_length=255)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    is_used: bool = Field(default=False)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True))
    )
