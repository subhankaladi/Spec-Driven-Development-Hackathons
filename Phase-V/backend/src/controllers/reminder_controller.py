"""Reminder Controller for managing task reminders."""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from ..models.database import get_session
from ..models.reminder import Reminder
from ..schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse
)
from ..services.reminder_service import ReminderService
from ..services.event_service import EventService


class ReminderController:
    """Controller class for managing task reminders."""

    def __init__(
        self,
        reminder_service: ReminderService,
        event_service: EventService
    ):
        self.reminder_service = reminder_service
        self.event_service = event_service

    async def create_reminder(
        self,
        user_id: UUID,
        reminder_data: ReminderCreate,
        session: Session
    ) -> ReminderResponse:
        """Create a new reminder for a task."""
        try:
            # Validate that the reminder time is before the task's due date
            task = self.task_service.get_task(reminder_data.task_instance_id, user_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )
            
            if task.due_date and reminder_data.reminder_time >= task.due_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reminder time must be before the task's due date"
                )
            
            # Create the reminder
            reminder = self.reminder_service.create_reminder(
                user_id=user_id,
                reminder_data=reminder_data
            )
            
            # Log and publish the reminder creation event
            await self.event_service.log_reminder_created(
                user_id=user_id,
                reminder_id=reminder.id,
                reminder_data=reminder_data.dict()
            )
            
            # Convert to response model
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create reminder: {str(e)}"
            )

    async def get_reminder(
        self,
        reminder_id: UUID,
        user_id: UUID,
        session: Session
    ) -> ReminderResponse:
        """Get a specific reminder."""
        reminder = self.reminder_service.get_reminder(reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
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

    async def get_user_reminders(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ) -> List[ReminderResponse]:
        """Get all reminders for a user."""
        try:
            reminders = self.reminder_service.get_user_reminders(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
            
            responses = []
            for reminder in reminders:
                responses.append(ReminderResponse(
                    id=reminder.id,
                    task_instance_id=reminder.task_instance_id,
                    user_id=reminder.user_id,
                    reminder_time=reminder.reminder_time,
                    method=reminder.method,
                    is_sent=reminder.is_sent,
                    created_at=reminder.created_at,
                    updated_at=reminder.updated_at
                ))
            
            return responses
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user reminders: {str(e)}"
            )

    async def update_reminder(
        self,
        reminder_id: UUID,
        user_id: UUID,
        update_data: ReminderUpdate,
        session: Session
    ) -> ReminderResponse:
        """Update a reminder."""
        # Verify the reminder exists and belongs to the user
        existing_reminder = self.reminder_service.get_reminder(reminder_id, user_id)
        if not existing_reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        try:
            # If updating the reminder time, validate it's before the task's due date
            if update_data.reminder_time:
                task = self.task_service.get_task(existing_reminder.task_instance_id, user_id)
                if task.due_date and update_data.reminder_time >= task.due_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Reminder time must be before the task's due date"
                    )
            
            # Update the reminder
            updated_reminder = self.reminder_service.update_reminder(
                reminder_id=reminder_id,
                user_id=user_id,
                update_data=update_data
            )
            
            if not updated_reminder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reminder not found"
                )
            
            # Log and publish the reminder update event
            await self.event_service.log_reminder_updated(
                user_id=user_id,
                reminder_id=updated_reminder.id,
                update_data=update_data.dict()
            )
            
            return ReminderResponse(
                id=updated_reminder.id,
                task_instance_id=updated_reminder.task_instance_id,
                user_id=updated_reminder.user_id,
                reminder_time=updated_reminder.reminder_time,
                method=updated_reminder.method,
                is_sent=updated_reminder.is_sent,
                created_at=updated_reminder.created_at,
                updated_at=updated_reminder.updated_at
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update reminder: {str(e)}"
            )

    async def delete_reminder(
        self,
        reminder_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Delete a reminder."""
        # Verify the reminder exists and belongs to the user
        reminder = self.reminder_service.get_reminder(reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        try:
            # Delete the reminder
            success = self.reminder_service.delete_reminder(reminder_id, user_id)
            
            if success:
                # Log and publish the reminder deletion event
                await self.event_service.log_reminder_deleted(
                    user_id=user_id,
                    reminder_id=reminder_id
                )
            
            return success
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete reminder: {str(e)}"
            )

    async def mark_reminder_as_sent(
        self,
        reminder_id: UUID,
        user_id: UUID,
        session: Session
    ) -> ReminderResponse:
        """Mark a reminder as sent."""
        # Verify the reminder exists and belongs to the user
        reminder = self.reminder_service.get_reminder(reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        try:
            # Mark the reminder as sent
            updated_reminder = self.reminder_service.mark_as_sent(reminder_id)
            
            # Log and publish the reminder sent event
            await self.event_service.log_reminder_sent(
                user_id=user_id,
                reminder_id=updated_reminder.id
            )
            
            return ReminderResponse(
                id=updated_reminder.id,
                task_instance_id=updated_reminder.task_instance_id,
                user_id=updated_reminder.user_id,
                reminder_time=updated_reminder.reminder_time,
                method=updated_reminder.method,
                is_sent=updated_reminder.is_sent,
                created_at=updated_reminder.created_at,
                updated_at=updated_reminder.updated_at
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark reminder as sent: {str(e)}"
            )


def get_reminder_controller(
    reminder_service: ReminderService = Depends(),
    event_service: EventService = Depends()
) -> ReminderController:
    """Get a ReminderController instance with dependencies."""
    return ReminderController(
        reminder_service=reminder_service,
        event_service=event_service
    )