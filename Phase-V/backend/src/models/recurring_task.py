"""Recurring Task Template SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import enum
from sqlalchemy import Enum as SQLEnum, JSON, Column
from pydantic import BaseModel, validator
from typing import Dict, Any


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurringTaskTemplate(SQLModel, table=True):
    """Recurring Task Template entity defining the pattern and parameters for recurring tasks."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the template"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="Owner of the recurring task"
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        min_length=1,
        description="Title of the recurring task"
    )
    description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Description of the recurring task"
    )
    priority: str = Field(
        default="medium",
        description="Priority level (low, medium, high)"
    )
    recurrence_pattern: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="Stores recurrence rule in RFC 5545 RRULE format"
    )
    start_date: datetime = Field(
        nullable=False,
        description="When the recurrence starts"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="When the recurrence ends (null for indefinite)"
    )
    max_occurrences: Optional[int] = Field(
        default=None,
        nullable=True,
        description="Max number of occurrences (null for indefinite)"
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        sa_column_kwargs={"server_default": "true"},
        description="Whether the recurrence is active"
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
        return f"<RecurringTaskTemplate(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class RecurringTaskTemplateCreate(BaseModel):
    """Schema for creating a recurring task template."""
    title: str
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = PriorityEnum.MEDIUM
    recurrence_pattern: Dict[str, Any]
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None


class RecurringTaskTemplateUpdate(BaseModel):
    """Schema for updating a recurring task template."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None
    is_active: Optional[bool] = None