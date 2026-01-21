"""Task SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Task(SQLModel, table=True):
    """Task entity representing a todo item."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="Owning user identifier (UUID)"
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        min_length=1,
        description="Task title (required, 1-255 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Optional task description"
    )
    is_completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status"
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

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.is_completed})>"
