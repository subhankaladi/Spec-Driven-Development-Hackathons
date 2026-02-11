"""Task SQLModel entity with Phase V enhancements."""
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class Task(SQLModel, table=True):
    """Task entity representing a todo item with recurring, reminder, and priority support."""

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

    # Phase V fields
    due_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Optional due date and time"
    )
    remind_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Optional reminder time"
    )
    priority: str = Field(
        default="medium",
        nullable=False,
        index=True,
        description="Task priority: low, medium, high"
    )
    tags: Optional[List[str]] = Field(
        default=[],
        nullable=True,
        sa_column_kwargs={"type_": JSON},
        description="List of tags for categorization"
    )
    recurrence_rule: Optional[Dict[str, Any]] = Field(
        default=None,
        nullable=True,
        sa_column_kwargs={"type_": JSON},
        description="Recurrence rule: {frequency: 'daily|weekly|monthly', end_date: optional}"
    )
    next_occurrence_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="For recurring tasks, when next occurrence is scheduled"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', priority='{self.priority}', completed={self.is_completed})>"
