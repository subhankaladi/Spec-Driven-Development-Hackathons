"""Reminder Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
import enum


class ReminderMethodEnum(str, enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class ReminderCreate(BaseModel):
    """Schema for creating a reminder."""

    task_instance_id: UUID = Field(
        ...,
        description="Associated task instance"
    )
    reminder_time: datetime = Field(
        ...,
        description="When the reminder should trigger"
    )
    method: ReminderMethodEnum = Field(
        ...,
        description="How to deliver the reminder"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_instance_id": "550e8400-e29b-41d4-a716-446655440000",
                "reminder_time": "2026-01-08T09:00:00Z",
                "method": "email"
            }
        }
    )


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""

    reminder_time: Optional[datetime] = Field(
        default=None,
        description="When the reminder should trigger"
    )
    method: Optional[ReminderMethodEnum] = Field(
        default=None,
        description="How to deliver the reminder"
    )
    is_sent: Optional[bool] = Field(
        default=None,
        description="Whether reminder has been sent"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reminder_time": "2026-01-08T10:00:00Z",
                "method": "push",
                "is_sent": False
            }
        }
    )


class ReminderResponse(BaseModel):
    """Schema for reminder response."""

    id: UUID = Field(..., description="Unique identifier for the reminder")
    task_instance_id: UUID = Field(..., description="Associated task instance")
    user_id: UUID = Field(..., description="Owner of the reminder")
    reminder_time: datetime = Field(..., description="When the reminder should trigger")
    method: ReminderMethodEnum = Field(..., description="How to deliver the reminder")
    is_sent: bool = Field(..., description="Whether reminder has been sent")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "task_instance_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "reminder_time": "2026-01-08T09:00:00Z",
                "method": "email",
                "is_sent": False,
                "created_at": "2026-01-07T10:30:00Z",
                "updated_at": "2026-01-07T10:30:00Z"
            }
        }
    )


class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list response."""

    items: list[ReminderResponse] = Field(..., description="List of reminders")
    total: int = Field(..., description="Total number of reminders")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "task_instance_id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440001",
                        "reminder_time": "2026-01-08T09:00:00Z",
                        "method": "email",
                        "is_sent": False,
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