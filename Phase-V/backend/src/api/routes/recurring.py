"""Recurring task API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from ...models.database import get_session
from ...models.recurring_task import RecurringTaskTemplate
from ...services.recurring_service import get_recurring_task_service, RecurringTaskService
from ...api.schemas.recurring import (
    RecurringTaskTemplateCreate,
    RecurringTaskTemplateUpdate,
    RecurringTaskTemplateResponse,
    RecurringTaskTemplateListResponse
)
from ...api.dependencies import get_current_user
from ...models.user import User
from sqlalchemy import func


router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


@router.get("/", response_model=RecurringTaskTemplateListResponse)
async def list_recurring_tasks(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all recurring task templates for the current user."""
    service = get_recurring_task_service(session)
    recurring_tasks = service.get_user_recurring_tasks(current_user.id, skip=skip, limit=limit)
    
    # Count total for pagination
    total_statement = select(func.count()).select_from(select(RecurringTaskTemplate).where(RecurringTaskTemplate.user_id == current_user.id).subquery())
    total = len(recurring_tasks)  # Simplified for this example
    
    # Calculate pagination details
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    # Convert SQLModel objects to Pydantic response models
    items = []
    for rt in recurring_tasks:
        items.append(RecurringTaskTemplateResponse(
            id=rt.id,
            user_id=rt.user_id,
            title=rt.title,
            description=rt.description,
            priority=rt.priority,
            recurrence_pattern=rt.recurrence_pattern,
            start_date=rt.start_date,
            end_date=rt.end_date,
            max_occurrences=rt.max_occurrences,
            is_active=rt.is_active,
            created_at=rt.created_at,
            updated_at=rt.updated_at
        ))
    
    return RecurringTaskTemplateListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("/", response_model=RecurringTaskTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task(
    recurring_task_data: RecurringTaskTemplateCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new recurring task template."""
    service = get_recurring_task_service(session)
    try:
        recurring_task = service.create_recurring_task(
            user_id=current_user.id,
            recurring_task_data=recurring_task_data
        )
        # Convert SQLModel object to Pydantic response model
        return RecurringTaskTemplateResponse(
            id=recurring_task.id,
            user_id=recurring_task.user_id,
            title=recurring_task.title,
            description=recurring_task.description,
            priority=recurring_task.priority,
            recurrence_pattern=recurring_task.recurrence_pattern,
            start_date=recurring_task.start_date,
            end_date=recurring_task.end_date,
            max_occurrences=recurring_task.max_occurrences,
            is_active=recurring_task.is_active,
            created_at=recurring_task.created_at,
            updated_at=recurring_task.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def get_recurring_task(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific recurring task template."""
    service = get_recurring_task_service(session)
    recurring_task = service.get_recurring_task(template_id, current_user.id)
    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring task template not found")
    
    # Convert SQLModel object to Pydantic response model
    return RecurringTaskTemplateResponse(
        id=recurring_task.id,
        user_id=recurring_task.user_id,
        title=recurring_task.title,
        description=recurring_task.description,
        priority=recurring_task.priority,
        recurrence_pattern=recurring_task.recurrence_pattern,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        is_active=recurring_task.is_active,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.put("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def update_recurring_task(
    template_id: UUID,
    update_data: RecurringTaskTemplateUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a recurring task template."""
    service = get_recurring_task_service(session)
    recurring_task = service.update_recurring_task(template_id, current_user.id, update_data)
    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring task template not found")
    
    # Convert SQLModel object to Pydantic response model
    return RecurringTaskTemplateResponse(
        id=recurring_task.id,
        user_id=recurring_task.user_id,
        title=recurring_task.title,
        description=recurring_task.description,
        priority=recurring_task.priority,
        recurrence_pattern=recurring_task.recurrence_pattern,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        is_active=recurring_task.is_active,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.patch("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def partially_update_recurring_task(
    template_id: UUID,
    update_data: RecurringTaskTemplateUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Partially update a recurring task template."""
    service = get_recurring_task_service(session)
    recurring_task = service.update_recurring_task(template_id, current_user.id, update_data)
    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring task template not found")
    
    # Convert SQLModel object to Pydantic response model
    return RecurringTaskTemplateResponse(
        id=recurring_task.id,
        user_id=recurring_task.user_id,
        title=recurring_task.title,
        description=recurring_task.description,
        priority=recurring_task.priority,
        recurrence_pattern=recurring_task.recurrence_pattern,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        is_active=recurring_task.is_active,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a recurring task template."""
    service = get_recurring_task_service(session)
    success = service.delete_recurring_task(template_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurring task template not found")
    return