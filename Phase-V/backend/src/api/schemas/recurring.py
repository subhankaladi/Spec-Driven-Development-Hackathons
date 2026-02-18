"""Recurring Task Template Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
import enum


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurringTaskTemplateCreate(BaseModel):
    """Schema for creating a recurring task template."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Title of the recurring task"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the recurring task"
    )
    priority: Optional[PriorityEnum] = Field(
        default=PriorityEnum.MEDIUM,
        description="Priority level (low, medium, high)"
    )
    recurrence_pattern: Dict[str, Any] = Field(
        ...,
        description="Recurrence rule in RFC 5545 RRULE format"
    )
    start_date: datetime = Field(
        ...,
        description="When the recurrence starts"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="When the recurrence ends (null for indefinite)"
    )
    max_occurrences: Optional[int] = Field(
        default=None,
        description="Max number of occurrences (null for indefinite)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Weekly team meeting",
                "description": "Team sync meeting every Monday",
                "priority": "high",
                "recurrence_pattern": {
                    "freq": "weekly",
                    "interval": 1,
                    "byweekday": ["MO"],
                    "until": "2024-12-31T23:59:59Z"
                },
                "start_date": "2024-01-01T09:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "max_occurrences": 52
            }
        }
    )


class RecurringTaskTemplateUpdate(BaseModel):
    """Schema for updating a recurring task template."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Title of the recurring task"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the recurring task"
    )
    priority: Optional[PriorityEnum] = Field(
        default=None,
        description="Priority level (low, medium, high)"
    )
    recurrence_pattern: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Recurrence rule in RFC 5545 RRULE format"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="When the recurrence starts"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="When the recurrence ends (null for indefinite)"
    )
    max_occurrences: Optional[int] = Field(
        default=None,
        description="Max number of occurrences (null for indefinite)"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the recurrence is active"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Weekly team meeting - Updated",
                "priority": "medium",
                "is_active": False
            }
        }
    )


class RecurringTaskTemplateResponse(BaseModel):
    """Schema for recurring task template response."""

    id: UUID = Field(..., description="Unique identifier for the template")
    user_id: UUID = Field(..., description="Owner of the recurring task")
    title: str = Field(..., description="Title of the recurring task")
    description: Optional[str] = Field(default=None, description="Description of the recurring task")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM, description="Priority level")
    recurrence_pattern: Dict[str, Any] = Field(..., description="Recurrence rule in RFC 5545 RRULE format")
    start_date: datetime = Field(..., description="When the recurrence starts")
    end_date: Optional[datetime] = Field(default=None, description="When the recurrence ends (null for indefinite)")
    max_occurrences: Optional[int] = Field(default=None, description="Max number of occurrences (null for indefinite)")
    is_active: bool = Field(..., description="Whether the recurrence is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Weekly team meeting",
                "description": "Team sync meeting every Monday",
                "priority": "high",
                "recurrence_pattern": {
                    "freq": "weekly",
                    "interval": 1,
                    "byweekday": ["MO"],
                    "until": "2024-12-31T23:59:59Z"
                },
                "start_date": "2024-01-01T09:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "max_occurrences": 52,
                "is_active": True,
                "created_at": "2026-01-07T10:30:00Z",
                "updated_at": "2026-01-07T10:30:00Z"
            }
        }
    )


class RecurringTaskTemplateListResponse(BaseModel):
    """Schema for paginated recurring task template list response."""

    items: list[RecurringTaskTemplateResponse] = Field(..., description="List of recurring task templates")
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "user_id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Weekly team meeting",
                        "description": "Team sync meeting every Monday",
                        "priority": "high",
                        "recurrence_pattern": {
                            "freq": "weekly",
                            "interval": 1,
                            "byweekday": ["MO"],
                            "until": "2024-12-31T23:59:59Z"
                        },
                        "start_date": "2024-01-01T09:00:00Z",
                        "end_date": "2024-12-31T23:59:59Z",
                        "max_occurrences": 52,
                        "is_active": True,
                        "created_at": "2026-01-07T10:30:00Z",
                        "updated_at": "2026-01-07T10:30:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1
            }
        }
    )