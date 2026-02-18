"""Reminder Service for managing task reminders and scheduling notifications."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from ..models.reminder import Reminder
from ..models.task import Task
from ..api.schemas.reminder import ReminderCreate, ReminderUpdate


class ReminderService:
    """Service class for managing task reminders and scheduling notifications."""

    def __init__(self, session: Session):
        self.session = session

    def create_reminder(self, user_id: UUID, reminder_data: ReminderCreate) -> Reminder:
        """Create a new reminder for a task."""
        # Verify that the task belongs to the user
        task = self.session.exec(
            select(Task).where(Task.id == reminder_data.task_instance_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            raise ValueError(f"Task {reminder_data.task_instance_id} not found or does not belong to user {user_id}")
        
        # Validate that reminder time is before due date if due date exists
        if task.due_date and reminder_data.reminder_time >= task.due_date:
            raise ValueError("Reminder time must be before the task's due date")
        
        # Create the reminder
        reminder = Reminder(
            task_instance_id=reminder_data.task_instance_id,
            user_id=user_id,
            reminder_time=reminder_data.reminder_time,
            method=reminder_data.method,
            is_sent=False
        )
        
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        
        return reminder

    def get_reminder(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        """Get a specific reminder."""
        statement = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_user_reminders(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Get all reminders for a user."""
        statement = select(Reminder).where(
            Reminder.user_id == user_id
        ).order_by(Reminder.reminder_time.asc()).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def get_pending_reminders(self, before_time: Optional[datetime] = None) -> List[Reminder]:
        """Get all pending reminders that need to be sent."""
        query = select(Reminder).where(
            Reminder.is_sent == False,
            Reminder.reminder_time <= (before_time or datetime.utcnow())
        ).order_by(Reminder.reminder_time.asc())
        return self.session.exec(query).all()

    def update_reminder(self, reminder_id: UUID, user_id: UUID, update_data: ReminderUpdate) -> Optional[Reminder]:
        """Update a reminder."""
        reminder = self.get_reminder(reminder_id, user_id)
        if not reminder:
            return None

        # Get the associated task to validate reminder time
        task = self.session.exec(
            select(Task).where(Task.id == reminder.task_instance_id)
        ).first()
        
        # Update fields if provided
        if update_data.reminder_time is not None:
            # Validate that reminder time is before due date if due date exists
            if task and task.due_date and update_data.reminder_time >= task.due_date:
                raise ValueError("Reminder time must be before the task's due date")
            reminder.reminder_time = update_data.reminder_time
        
        if update_data.method is not None:
            reminder.method = update_data.method
        
        if update_data.is_sent is not None:
            reminder.is_sent = update_data.is_sent
        
        # Update the timestamp
        reminder.updated_at = datetime.utcnow()
        
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        
        return reminder

    def delete_reminder(self, reminder_id: UUID, user_id: UUID) -> bool:
        """Delete a reminder."""
        reminder = self.get_reminder(reminder_id, user_id)
        if not reminder:
            return False
        
        self.session.delete(reminder)
        self.session.commit()
        
        return True

    def mark_reminder_as_sent(self, reminder_id: UUID) -> bool:
        """Mark a reminder as sent."""
        reminder = self.session.get(Reminder, reminder_id)
        if not reminder:
            return False
        
        reminder.is_sent = True
        reminder.updated_at = datetime.utcnow()
        
        self.session.add(reminder)
        self.session.commit()
        
        return True

    def process_pending_reminders(self) -> int:
        """Process all pending reminders that are due."""
        pending_reminders = self.get_pending_reminders()
        processed_count = 0
        
        for reminder in pending_reminders:
            # In a real implementation, this would send the actual notification
            # For now, we'll just mark it as sent
            success = self._send_notification(reminder)
            if success:
                self.mark_reminder_as_sent(reminder.id)
                processed_count += 1
        
        return processed_count

    def _send_notification(self, reminder: Reminder) -> bool:
        """Send the actual notification based on the reminder method."""
        # In a real implementation, this would integrate with email/SMS/push notification services
        # For now, we'll just log the notification
        
        # Get the task details for the notification
        task = self.session.exec(
            select(Task).where(Task.id == reminder.task_instance_id)
        ).first()
        
        print(f"Sending {reminder.method.value} notification for task '{task.title}' "
              f"to user {reminder.user_id} at {reminder.reminder_time}")
        
        # Simulate sending notification
        # In real implementation, would call appropriate service based on reminder.method
        return True


def get_reminder_service(session: Session) -> ReminderService:
    """Get a ReminderService instance with the given session."""
    return ReminderService(session)