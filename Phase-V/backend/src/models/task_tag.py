"""TaskTag junction table SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class TaskTag(SQLModel, table=True):
    """Junction table for many-to-many relationship between Task and Tag."""

    task_instance_id: UUID = Field(
        primary_key=True,
        foreign_key="task.id",
        description="Associated task instance"
    )
    tag_id: UUID = Field(
        primary_key=True,
        foreign_key="tag.id",
        description="Associated tag"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )

    def __repr__(self):
        return f"<TaskTag(task_id={self.task_instance_id}, tag_id={self.tag_id})>"


from pydantic import BaseModel


class TaskTagCreate(BaseModel):
    """Schema for creating a task-tag association."""
    task_instance_id: UUID
    tag_id: UUID