"""Event Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class TaskEventCreate(BaseModel):
    """Schema for creating a task event log entry."""

    user_id: UUID = Field(..., description="User associated with the event")
    task_instance_id: Optional[UUID] = Field(default=None, description="Task associated with the event")
    event_type: str = Field(..., description="Type of event (created, updated, completed, etc.)")
    payload: Dict[str, Any] = Field(default={}, description="Event data in JSON format")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
                "event_type": "task.created",
                "payload": {
                    "title": "New task",
                    "description": "A new task was created"
                }
            }
        }
    )


class TaskEventUpdate(BaseModel):
    """Schema for updating a task event log entry."""

    processed_by_kafka: Optional[bool] = Field(default=None, description="Whether event was processed by Kafka")


class TaskEventResponse(BaseModel):
    """Schema for task event log response."""

    id: UUID = Field(..., description="Unique identifier for the event")
    user_id: UUID = Field(..., description="User associated with the event")
    task_instance_id: Optional[UUID] = Field(default=None, description="Task associated with the event")
    event_type: str = Field(..., description="Type of event")
    payload: Dict[str, Any] = Field(..., description="Event data in JSON format")
    processed_by_kafka: bool = Field(..., description="Whether event was processed by Kafka")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
                "event_type": "task.created",
                "payload": {
                    "title": "New task",
                    "description": "A new task was created"
                },
                "processed_by_kafka": False,
                "created_at": "2026-01-07T10:30:00Z"
            }
        }
    )


class TaskEventListResponse(BaseModel):
    """Schema for paginated task event list response."""

    items: list[TaskEventResponse] = Field(..., description="List of task events")
    total: int = Field(..., description="Total number of events")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
                        "event_type": "task.created",
                        "payload": {
                            "title": "New task",
                            "description": "A new task was created"
                        },
                        "processed_by_kafka": False,
                        "created_at": "2026-01-07T10:30:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1
            }
        }
    )