"""Reminder API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.user import User
from ..schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse
)
from ..controllers.reminder_controller import (
    get_reminder_controller,
    ReminderController
)
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Create a new reminder for a task."""
    return await controller.create_reminder(
        user_id=current_user.id,
        reminder_data=reminder_data,
        session=session
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get a specific reminder."""
    return await controller.get_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/", response_model=List[ReminderResponse])
async def get_user_reminders(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get all reminders for the user."""
    return await controller.get_user_reminders(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        session=session
    )


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    update_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Update a reminder."""
    return await controller.update_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def partially_update_reminder(
    reminder_id: UUID,
    update_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Partially update a reminder."""
    return await controller.update_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Delete a reminder."""
    success = await controller.delete_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return


@router.post("/{reminder_id}/mark-as-sent", response_model=ReminderResponse)
async def mark_reminder_as_sent(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Mark a reminder as sent."""
    return await controller.mark_reminder_as_sent(
        reminder_id=reminder_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/upcoming", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    current_user: User = Depends(get_current_user),
    hours_ahead: int = Query(24, ge=1, le=168),  # Up to 1 week ahead
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get all upcoming reminders within the specified time window."""
    return await controller.get_upcoming_reminders(
        user_id=current_user.id,
        hours_ahead=hours_ahead,
        session=session
    )


@router.get("/overdue", response_model=List[ReminderResponse])
async def get_overdue_reminders(
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get all overdue reminders that haven't been sent yet."""
    return await controller.get_overdue_reminders(
        user_id=current_user.id,
        session=session
    )


@router.get("/by-task/{task_id}", response_model=List[ReminderResponse])
async def get_reminders_by_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get all reminders for a specific task."""
    return await controller.get_reminders_by_task(
        task_instance_id=task_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/stats", response_model=dict)
async def get_reminder_stats(
    current_user: User = Depends(get_current_user),
    controller: ReminderController = Depends(get_reminder_controller),
    session: Session = Depends(get_session)
):
    """Get statistics about reminders for the user."""
    return await controller.get_reminder_stats(
        user_id=current_user.id,
        session=session
    )