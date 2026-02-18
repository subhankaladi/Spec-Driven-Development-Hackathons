"""Message database model for AI chat agent."""
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Message(SQLModel, table=True):
    """Message entity for chat messages.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation identifier (UUID, foreign key, indexed)
        role: Message sender role ('user' or 'agent')
        content: Message text content (max 5000 characters)
        created_at: Timestamp of message creation
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="conversation.id",
        description="Parent conversation identifier (UUID)"
    )
    role: str = Field(
        nullable=False,
        max_length=10,
        description="Message sender role ('user' or 'agent')"
    )
    content: str = Field(
        nullable=False,
        max_length=5000,
        description="Message text content (max 5000 characters)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} conversation_id={self.conversation_id} role='{self.role}'>"
