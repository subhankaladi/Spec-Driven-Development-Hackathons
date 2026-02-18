"""Conversation and Message database models.

This module defines the SQLModel entities for chat conversations and messages
in the AI Agent Chat API system.
"""
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4


class MessageRole(str, Enum):
    """Message role enumeration for user vs assistant messages."""

    USER = "user"
    ASSISTANT = "assistant"


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session.

    A conversation is owned by a single user and contains multiple messages.
    Tracks creation and update timestamps for sorting and filtering.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Foreign key to owning user
        title: Optional conversation title (max 255 chars)
        created_at: Timestamp of conversation creation
        updated_at: Timestamp of last update (message added)
        messages: Related messages in this conversation
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
        description="Owning user identifier (foreign key to user.id)"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional conversation title"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title='{self.title}')>"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation.

    Each message has a role (user or assistant), content, and optional tool calls.
    Messages are ordered by created_at within a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to parent conversation
        user_id: Foreign key to owning user (for authorization)
        role: Message role (user or assistant)
        content: Message content text (1-50000 chars)
        tool_calls: Optional JSON of MCP tool invocations
        created_at: Message creation timestamp
        conversation: Related conversation entity
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
        description="Parent conversation identifier (foreign key to conversation.id)"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="user.id",
        description="Owning user identifier (foreign key to user.id)"
    )
    role: MessageRole = Field(
        nullable=False,
        description="Message role (user or assistant)"
    )
    content: str = Field(
        nullable=False,
        min_length=1,
        max_length=50000,
        description="Message content text (non-empty, max 50000 chars)"
    )
    tool_calls: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="JSON of MCP tool invocations (optional)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Message creation timestamp"
    )
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
