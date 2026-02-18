"""Reminder SQLModel entity for task reminders and scheduling."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Reminder(SQLModel, table=True):
    """Reminder entity for scheduled task reminders via Dapr Jobs API."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique reminder identifier"
    )
    task_id: UUID = Field(
        nullable=False,
        index=True,
        description="Task ID to remind about"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="User ID who owns the task"
    )
    remind_at: datetime = Field(
        nullable=False,
        index=True,
        description="When to trigger the reminder"
    )
    notification_method: Optional[str] = Field(
        default="default",
        nullable=True,
        description="How to notify (email, sms, push, default)"
    )
    status: str = Field(
        default="scheduled",
        nullable=False,
        description="Reminder status: scheduled, triggered, cancelled"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When reminder was created"
    )
    triggered_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="When reminder was triggered"
    )

    def __repr__(self):
        return f"<Reminder(task_id={self.task_id}, remind_at={self.remind_at}, status='{self.status}')>"
