"""Tag Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class TagCreate(BaseModel):
    """Schema for creating a tag."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the tag"
    )
    color: Optional[str] = Field(
        default=None,
        description="Color code for UI display (hex format, e.g., #FF5733)"
    )

    @validator('color')
    def validate_color_format(cls, v):
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex code in format #XXXXXX')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "work",
                "color": "#FF5733"
            }
        }
    )


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Name of the tag"
    )
    color: Optional[str] = Field(
        default=None,
        description="Color code for UI display (hex format, e.g., #FF5733)"
    )

    @validator('color')
    def validate_color_format(cls, v):
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex code in format #XXXXXX')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "business",
                "color": "#33FF57"
            }
        }
    )


class TagResponse(BaseModel):
    """Schema for tag response."""

    id: UUID = Field(..., description="Unique identifier for the tag")
    user_id: UUID = Field(..., description="Owner of the tag")
    name: str = Field(..., description="Name of the tag")
    color: Optional[str] = Field(default=None, description="Color code for UI display")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "work",
                "color": "#FF5733",
                "created_at": "2026-01-07T10:30:00Z",
                "updated_at": "2026-01-07T10:30:00Z"
            }
        }
    )


class TagListResponse(BaseModel):
    """Schema for paginated tag list response."""

    items: list[TagResponse] = Field(..., description="List of tags")
    total: int = Field(..., description="Total number of tags")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440004",
                        "user_id": "550e8400-e29b-41d4-a716-446655440001",
                        "name": "work",
                        "color": "#FF5733",
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