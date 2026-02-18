"""Conversation database model for AI chat agent."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    """Conversation entity for chat sessions.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner user identifier (UUID, foreign key, indexed)
        title: Optional conversation title
        created_at: Timestamp of conversation creation
        updated_at: Timestamp of last update
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="user.id",
        description="Owning user identifier (UUID)"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Optional conversation title (max 255 characters)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} user_id={self.user_id} title='{self.title}'>"
