"""Search Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import enum


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SearchFilters(BaseModel):
    """Schema for search filters."""
    
    priority: Optional[List[PriorityEnum]] = Field(
        default=None,
        description="Filter by priority levels"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by tag names"
    )
    due_after: Optional[datetime] = Field(
        default=None,
        description="Filter tasks with due date after this date"
    )
    due_before: Optional[datetime] = Field(
        default=None,
        description="Filter tasks with due date before this date"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Filter by completion status"
    )
    title_contains: Optional[str] = Field(
        default=None,
        description="Filter tasks with title containing this text"
    )
    description_contains: Optional[str] = Field(
        default=None,
        description="Filter tasks with description containing this text"
    )


class SearchRequest(BaseModel):
    """Schema for search request."""
    
    filters: Optional[SearchFilters] = Field(
        default=None,
        description="Search filters"
    )
    sort_by: Optional[str] = Field(
        default="created_at",
        description="Field to sort by (created_at, due_date, priority, title)"
    )
    sort_order: Optional[str] = Field(
        default="asc",
        description="Sort order (asc, desc)"
    )
    page: Optional[int] = Field(
        default=1,
        description="Page number for pagination"
    )
    page_size: Optional[int] = Field(
        default=20,
        description="Number of items per page (max 100)"
    )

    @classmethod
    def validate_sort_params(cls, sort_by: str, sort_order: str):
        """Validate sort parameters."""
        valid_sort_fields = ["created_at", "due_date", "priority", "title"]
        valid_sort_orders = ["asc", "desc"]
        
        if sort_by not in valid_sort_fields:
            raise ValueError(f"sort_by must be one of {valid_sort_fields}")
        if sort_order not in valid_sort_orders:
            raise ValueError(f"sort_order must be one of {valid_sort_orders}")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filters": {
                    "priority": ["high", "medium"],
                    "due_before": "2026-01-31T23:59:59Z",
                    "tags": ["urgent", "work"]
                },
                "sort_by": "due_date",
                "sort_order": "asc",
                "page": 1,
                "page_size": 20
            }
        }
    )


class SearchResponse(BaseModel):
    """Schema for search response."""
    
    items: List = Field(..., description="List of search results")
    total: int = Field(..., description="Total number of matching items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Submit quarterly report",
                        "description": "Prepare and submit Q1 financial report",
                        "is_completed": False,
                        "due_date": "2026-04-01T23:59:59Z",
                        "priority": "high",
                        "parent_template_id": None,
                        "tags": ["report", "finance", "urgent"],
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