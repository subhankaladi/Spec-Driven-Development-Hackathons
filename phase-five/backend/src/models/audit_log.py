"""AuditLog SQLModel entity for tracking task changes."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class AuditLog(SQLModel, table=True):
    """AuditLog entity for tracking all task lifecycle events."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique audit log identifier"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="User ID associated with the action"
    )
    action: str = Field(
        nullable=False,
        description="Action type: created, updated, deleted, completed"
    )
    task_id: UUID = Field(
        nullable=False,
        index=True,
        description="Task ID affected by this action"
    )
    change_data: Optional[Dict[str, Any]] = Field(
        default=None,
        nullable=True,
        description="JSON data of what changed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When the action occurred"
    )
    service_name: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Which service recorded this event"
    )

    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action='{self.action}', task_id={self.task_id}, timestamp={self.timestamp})>"
