"""Recurring Task Service for managing recurring task templates and generating task instances."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from ..models.recurring_task import RecurringTaskTemplate
from ..models.task import Task
from ..api.schemas.recurring import RecurringTaskTemplateCreate, RecurringTaskTemplateUpdate


class RecurringTaskService:
    """Service class for managing recurring task templates and generating task instances."""

    def __init__(self, session: Session):
        self.session = session

    def create_template(self, user_id: UUID, template_data: RecurringTaskTemplateCreate) -> RecurringTaskTemplate:
        """Create a new recurring task template."""
        # Validate recurrence pattern
        self._validate_recurrence_pattern(template_data.recurrence_pattern)
        
        # Create the template
        template = RecurringTaskTemplate(
            user_id=user_id,
            title=template_data.title,
            description=template_data.description,
            priority=template_data.priority,
            recurrence_pattern=template_data.recurrence_pattern,
            start_date=template_data.start_date,
            end_date=template_data.end_date,
            max_occurrences=template_data.max_occurrences,
            is_active=True
        )
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return template

    def get_template(self, template_id: UUID, user_id: UUID) -> Optional[RecurringTaskTemplate]:
        """Get a specific recurring task template."""
        statement = select(RecurringTaskTemplate).where(
            RecurringTaskTemplate.id == template_id,
            RecurringTaskTemplate.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_user_templates(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[RecurringTaskTemplate]:
        """Get all recurring task templates for a user."""
        statement = select(RecurringTaskTemplate).where(
            RecurringTaskTemplate.user_id == user_id,
            RecurringTaskTemplate.is_active == True
        ).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update_template(self, template_id: UUID, user_id: UUID, update_data: RecurringTaskTemplateUpdate) -> Optional[RecurringTaskTemplate]:
        """Update a recurring task template."""
        template = self.get_template(template_id, user_id)
        if not template:
            return None

        # Update fields if provided
        if update_data.title is not None:
            template.title = update_data.title
        if update_data.description is not None:
            template.description = update_data.description
        if update_data.priority is not None:
            template.priority = update_data.priority
        if update_data.recurrence_pattern is not None:
            self._validate_recurrence_pattern(update_data.recurrence_pattern)
            template.recurrence_pattern = update_data.recurrence_pattern
        if update_data.start_date is not None:
            template.start_date = update_data.start_date
        if update_data.end_date is not None:
            template.end_date = update_data.end_date
        if update_data.max_occurrences is not None:
            template.max_occurrences = update_data.max_occurrences
        if update_data.is_active is not None:
            template.is_active = update_data.is_active

        template.updated_at = datetime.utcnow()
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return template

    def delete_template(self, template_id: UUID, user_id: UUID) -> bool:
        """Delete (deactivate) a recurring task template."""
        template = self.get_template(template_id, user_id)
        if not template:
            return False

        template.is_active = False
        template.updated_at = datetime.utcnow()
        
        self.session.add(template)
        self.session.commit()
        
        return True

    def generate_task_instances(self) -> int:
        """Generate new task instances based on active recurring task templates."""
        # Get all active recurring task templates
        active_templates = self.session.exec(
            select(RecurringTaskTemplate).where(RecurringTaskTemplate.is_active == True)
        ).all()
        
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
                    due_date=instance_data['due_date'],  # Use the calculated due date
                    parent_template_id=template.id  # Link to the template
                )
                
                self.session.add(new_task)
                generated_count += 1
        
        if generated_count > 0:
            self.session.commit()
        
        return generated_count

    def _calculate_upcoming_instances(self, template: RecurringTaskTemplate) -> List[dict]:
        """Calculate upcoming task instances based on the recurrence pattern."""
        # This is a simplified implementation - in a real system, you'd use a 
        # proper recurrence library like python-dateutil.rrule
        instances = []
        
        # Calculate the next occurrence based on the recurrence pattern
        # This is a simplified approach - a real implementation would parse the RRULE properly
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
            existing_count = self.session.exec(
                select(Task).where(Task.parent_template_id == template.id)
            ).all()
            if len(existing_count) >= template.max_occurrences:
                return []  # Reached max occurrences
        
        # Add the new instance
        instances.append({'due_date': next_occurrence})
        
        return instances

    def _validate_recurrence_pattern(self, pattern: dict) -> bool:
        """Validate the recurrence pattern."""
        # Basic validation - check required fields
        if 'freq' not in pattern:
            raise ValueError("Recurrence pattern must include 'freq' field")
        
        freq = pattern['freq']
        if freq not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise ValueError(f"Invalid frequency '{freq}'. Must be one of: daily, weekly, monthly, yearly")
        
        # Validate interval if provided
        if 'interval' in pattern:
            interval = pattern['interval']
            if not isinstance(interval, int) or interval < 1:
                raise ValueError("Interval must be a positive integer")
        
        return True


def get_recurring_task_service(session: Session) -> RecurringTaskService:
    """Get a RecurringTaskService instance with the given session."""
    return RecurringTaskService(session)