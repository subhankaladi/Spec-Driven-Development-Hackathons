"""Task Event Log SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import JSON, Column


class TaskEventLog(SQLModel, table=True):
    """Event log for audit and event-driven processing."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the event"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="User associated with the event"
    )
    task_instance_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        foreign_key="task.id",
        description="Task associated with the event"
    )
    event_type: str = Field(
        max_length=50,
        nullable=False,
        description="Type of event (created, updated, completed, etc.)"
    )
    payload: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="Event data in JSON format"
    )
    processed_by_kafka: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "false"},
        description="Whether event was processed by Kafka"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )

    def __repr__(self):
        return f"<TaskEventLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id}, processed={self.processed_by_kafka})>"


from pydantic import BaseModel


class TaskEventLogCreate(BaseModel):
    """Schema for creating a task event log entry."""
    user_id: UUID
    task_instance_id: Optional[UUID] = None
    event_type: str
    payload: Dict[str, Any]
    processed_by_kafka: Optional[bool] = False