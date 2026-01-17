"""User database model for authentication."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User entity for authentication.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, indexed)
        password_hash: Bcrypt hashed password
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
