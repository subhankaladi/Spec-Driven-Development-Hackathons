"""Reminder API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from ...models.database import get_session
from ...models.reminder import Reminder
from ...services.reminder_service import get_reminder_service, ReminderService
from ...api.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)
from ...api.dependencies import get_current_user
from ...models.user import User
from sqlalchemy import func


router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/", response_model=ReminderListResponse)
async def list_reminders(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all reminders for the current user."""
    service = get_reminder_service(session)
    reminders = service.get_user_reminders(current_user.id, skip=skip, limit=limit)
    
    # Count total for pagination
    total = len(reminders)  # Simplified for this example
    
    # Calculate pagination details
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    # Convert SQLModel objects to Pydantic response models
    items = []
    for reminder in reminders:
        items.append(ReminderResponse(
            id=reminder.id,
            task_instance_id=reminder.task_instance_id,
            user_id=reminder.user_id,
            reminder_time=reminder.reminder_time,
            method=reminder.method,
            is_sent=reminder.is_sent,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        ))
    
    return ReminderListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new reminder."""
    service = get_reminder_service(session)
    try:
        reminder = service.create_reminder(
            user_id=current_user.id,
            reminder_data=reminder_data
        )
        # Convert SQLModel object to Pydantic response model
        return ReminderResponse(
            id=reminder.id,
            task_instance_id=reminder.task_instance_id,
            user_id=reminder.user_id,
            reminder_time=reminder.reminder_time,
            method=reminder.method,
            is_sent=reminder.is_sent,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific reminder."""
    service = get_reminder_service(session)
    reminder = service.get_reminder(reminder_id, current_user.id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Convert SQLModel object to Pydantic response model
    return ReminderResponse(
        id=reminder.id,
        task_instance_id=reminder.task_instance_id,
        user_id=reminder.user_id,
        reminder_time=reminder.reminder_time,
        method=reminder.method,
        is_sent=reminder.is_sent,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    update_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a reminder."""
    service = get_reminder_service(session)
    reminder = service.update_reminder(reminder_id, current_user.id, update_data)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Convert SQLModel object to Pydantic response model
    return ReminderResponse(
        id=reminder.id,
        task_instance_id=reminder.task_instance_id,
        user_id=reminder.user_id,
        reminder_time=reminder.reminder_time,
        method=reminder.method,
        is_sent=reminder.is_sent,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def partially_update_reminder(
    reminder_id: UUID,
    update_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Partially update a reminder."""
    service = get_reminder_service(session)
    reminder = service.update_reminder(reminder_id, current_user.id, update_data)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Convert SQLModel object to Pydantic response model
    return ReminderResponse(
        id=reminder.id,
        task_instance_id=reminder.task_instance_id,
        user_id=reminder.user_id,
        reminder_time=reminder.reminder_time,
        method=reminder.method,
        is_sent=reminder.is_sent,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a reminder."""
    service = get_reminder_service(session)
    success = service.delete_reminder(reminder_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return