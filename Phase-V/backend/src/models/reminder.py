"""Reminder SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import enum
from sqlalchemy import Enum as SQLEnum, Column


class ReminderMethodEnum(str, enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class Reminder(SQLModel, table=True):
    """Reminder entity for task notifications."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the reminder"
    )
    task_instance_id: UUID = Field(
        nullable=False,
        foreign_key="task.id",
        description="Associated task instance"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="Owner of the reminder"
    )
    reminder_time: datetime = Field(
        nullable=False,
        description="When the reminder should trigger"
    )
    method: ReminderMethodEnum = Field(
        sa_column=Column(SQLEnum("email", "push", "sms", name="reminder_method_enum"), nullable=False),
        description="How to deliver the reminder"
    )
    is_sent: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "false"},
        description="Whether reminder has been sent"
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
        return f"<Reminder(id={self.id}, task_id={self.task_instance_id}, time={self.reminder_time}, sent={self.is_sent})>"


from pydantic import BaseModel


class ReminderCreate(BaseModel):
    """Schema for creating a reminder."""
    task_instance_id: UUID
    reminder_time: datetime
    method: ReminderMethodEnum


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""
    reminder_time: Optional[datetime] = None
    method: Optional[ReminderMethodEnum] = None
    is_sent: Optional[bool] = None