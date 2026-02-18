"""Task Scheduler Service for managing recurring tasks and reminders."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session
from uuid import UUID
from ..models.task import Task
from ..models.recurring_task import RecurringTaskTemplate
from ..models.reminder import Reminder
from ..models.database import get_session
from ..services.task_service import TaskService
from ..services.recurring_service import RecurringTaskService
from ..services.reminder_service import ReminderService
from ..config import settings


logger = logging.getLogger(__name__)


class TaskSchedulerService:
    """Service for scheduling recurring tasks and reminders."""

    def __init__(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        reminder_service: ReminderService
    ):
        self.task_service = task_service
        self.recurring_service = recurring_service
        self.reminder_service = reminder_service

    async def generate_recurring_task_instances(self) -> int:
        """Generate new task instances from active recurring templates."""
        try:
            # Get all active recurring task templates
            active_templates = self.recurring_service.get_active_templates()
            
            generated_count = 0
            
            for template in active_templates:
                # Calculate upcoming occurrences based on the recurrence pattern
                new_instances = self._calculate_upcoming_instances(template)
                
                for instance_data in new_instances:
                    # Create a new task instance based on the template
                    new_task = Task(
                        user_id=template.user_id,
                        title=template.title,
                        description=template.description,
                        priority=template.priority,
                        due_date=instance_data.get('due_date'),
                        parent_template_id=template.id  # Link to the template
                    )
                    
                    # Save the new task instance
                    self.task_service.create_task_from_template(new_task)
                    generated_count += 1
            
            logger.info(f"Generated {generated_count} new task instances from recurring templates")
            return generated_count
        except Exception as e:
            logger.error(f"Error generating recurring task instances: {str(e)}")
            raise

    def _calculate_upcoming_instances(self, template: RecurringTaskTemplate) -> List[Dict[str, Any]]:
        """Calculate upcoming task instances based on the recurrence pattern."""
        instances = []
        
        # This is a simplified implementation - in a real system, you'd use a proper
        # recurrence library like python-dateutil.rrule to handle complex patterns
        current_date = datetime.utcnow()
        
        # If the template hasn't started yet, use the start date
        if current_date < template.start_date:
            current_date = template.start_date
        
        # For now, just generate instances based on simple frequency
        # In a real implementation, you'd parse the recurrence_pattern properly
        freq = template.recurrence_pattern.get('freq', 'daily')
        interval = template.recurrence_pattern.get('interval', 1)
        
        # Calculate next occurrence
        next_occurrence = current_date
        if freq == 'daily':
            next_occurrence += timedelta(days=interval)
        elif freq == 'weekly':
            next_occurrence += timedelta(weeks=interval)
        elif freq == 'monthly':
            # Simple month addition (doesn't handle day overflow)
            next_month = next_occurrence.month + interval
            year = next_occurrence.year
            if next_month > 12:
                year += next_month // 12
                next_month = next_month % 12
            next_occurrence = next_occurrence.replace(year=year, month=next_month)
        elif freq == 'yearly':
            next_occurrence = next_occurrence.replace(year=next_occurrence.year + interval)
        
        # Check if we're within the template's bounds
        if template.end_date and next_occurrence > template.end_date:
            return []  # No more instances to generate
        
        # Check max occurrences
        if template.max_occurrences:
            # Count existing instances for this template
            existing_count = self.task_service.get_task_count_by_template(template.id)
            if existing_count >= template.max_occurrences:
                return []  # Reached max occurrences
        
        # Add the new instance
        instances.append({'due_date': next_occurrence})
        
        return instances

    async def process_pending_reminders(self) -> int:
        """Process pending reminders that are due."""
        try:
            # Get all pending reminders that are due
            pending_reminders = self.reminder_service.get_due_reminders()
            
            processed_count = 0
            
            for reminder in pending_reminders:
                # In a real implementation, this would send the actual notification
                # For now, we'll just mark it as sent
                success = self.reminder_service.mark_as_sent(reminder.id)
                if success:
                    processed_count += 1
            
            logger.info(f"Processed {processed_count} pending reminders")
            return processed_count
        except Exception as e:
            logger.error(f"Error processing pending reminders: {str(e)}")
            raise

    def start_background_tasks(self):
        """Start background tasks for recurring tasks and reminders."""
        # This would typically be called at application startup
        # In a real implementation, this would run continuously
        pass


# Global scheduler service instance
task_scheduler_service = TaskSchedulerService(
    task_service=TaskService(),
    recurring_service=RecurringTaskService(),
    reminder_service=ReminderService()
)


async def get_task_scheduler_service() -> TaskSchedulerService:
    """Get the task scheduler service instance."""
    return task_scheduler_service