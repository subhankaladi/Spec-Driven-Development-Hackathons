"""Task API schemas (Pydantic models) for Phase V extended features."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class RecurrenceRuleSchema(BaseModel):
    """Recurrence rule for recurring tasks."""
    frequency: str = Field(..., description="daily, weekly, or monthly")
    end_date: Optional[str] = Field(None, description="Optional end date for recurrence")


class TaskCreateRequest(BaseModel):
    """Request body for creating a task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")
    due_at: Optional[datetime] = Field(None, description="Optional due date/time")
    remind_at: Optional[datetime] = Field(None, description="Optional reminder time")
    priority: str = Field("medium", description="Task priority: low, medium, high")
    tags: Optional[List[str]] = Field([], description="Optional tags")
    recurrence_rule: Optional[RecurrenceRuleSchema] = Field(None, description="Optional recurrence configuration")


class TaskUpdateRequest(BaseModel):
    """Request body for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    recurrence_rule: Optional[RecurrenceRuleSchema] = None


class TaskResponse(BaseModel):
    """Complete task response with all Phase V fields."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    due_at: Optional[datetime]
    remind_at: Optional[datetime]
    priority: str
    tags: List[str]
    recurrence_rule: Optional[Dict[str, Any]]
    next_occurrence_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""
    items: List[TaskResponse]
    total: int
    limit: int
    offset: int
