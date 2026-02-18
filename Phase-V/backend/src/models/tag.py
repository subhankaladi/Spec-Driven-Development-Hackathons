"""Tag SQLModel entity."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Tag(SQLModel, table=True):
    """Tag entity for task categorization."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the tag"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="Owner of the tag"
    )
    name: str = Field(
        max_length=100,
        nullable=False,
        description="Name of the tag"
    )
    color: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Color code for UI display (hex format)"
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
        return f"<Tag(id={self.id}, name='{self.name}', user_id={self.user_id})>"


from pydantic import BaseModel, validator


class TagCreate(BaseModel):
    """Schema for creating a tag."""
    name: str
    color: Optional[str] = None

    @validator('color')
    def validate_color_format(cls, v):
        if v and not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex code in format #XXXXXX')
        return v


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = None
    color: Optional[str] = None

    @validator('color')
    def validate_color_format(cls, v):
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex code in format #XXXXXX')
        return v