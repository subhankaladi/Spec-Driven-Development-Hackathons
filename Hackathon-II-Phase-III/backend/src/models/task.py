from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: str = Field()  # User ID who owns this task
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    owner_id: str
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskListResponse(SQLModel):
    """Paginated response model for task lists."""
    items: list[TaskRead] = Field(default_factory=list)
    total: int = Field(default=0)
    limit: int = Field(default=100)
    offset: int = Field(default=0)


class ErrorResponse(SQLModel):
    """Standardized error response model."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)