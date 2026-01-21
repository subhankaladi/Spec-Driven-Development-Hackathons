"""Task Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Task title (optional)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )
    is_completed: Optional[bool] = Field(
        default=None,
        description="Completion status"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries and supplies",
                "description": "Milk, eggs, bread, butter",
                "is_completed": True
            }
        }
    )


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: UUID = Field(..., description="Unique task identifier")
    user_id: UUID = Field(..., description="Owning user identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    is_completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_completed": False,
                "created_at": "2026-01-07T10:30:00Z",
                "updated_at": "2026-01-07T10:30:00Z"
            }
        }
    )


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    items: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_completed": False,
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
