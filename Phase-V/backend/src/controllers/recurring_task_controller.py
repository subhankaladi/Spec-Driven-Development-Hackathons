"""Recurring Task Controller for managing recurring task templates."""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from ..models.database import get_session
from ..models.recurring_task import RecurringTaskTemplate
from ..schemas.recurring import (
    RecurringTaskTemplateCreate,
    RecurringTaskTemplateUpdate,
    RecurringTaskTemplateResponse
)
from ..services.recurring_service import RecurringTaskService
from ..services.event_service import EventService


class RecurringTaskController:
    """Controller class for managing recurring task templates and generating task instances."""

    def __init__(
        self,
        recurring_service: RecurringTaskService,
        event_service: EventService
    ):
        self.recurring_service = recurring_service
        self.event_service = event_service

    async def create_recurring_task_template(
        self,
        user_id: UUID,
        template_data: RecurringTaskTemplateCreate,
        session: Session
    ) -> RecurringTaskTemplateResponse:
        """Create a new recurring task template."""
        try:
            # Validate the recurrence pattern
            self._validate_recurrence_pattern(template_data.recurrence_pattern)
            
            # Create the recurring task template
            template = self.recurring_service.create_template(
                user_id=user_id,
                template_data=template_data
            )
            
            # Log and publish the template creation event
            await self.event_service.log_recurring_task_template_created(
                user_id=user_id,
                template_id=template.id,
                template_data=template_data.dict()
            )
            
            # Convert to response model
            return RecurringTaskTemplateResponse(
                id=template.id,
                user_id=template.user_id,
                title=template.title,
                description=template.description,
                priority=template.priority,
                recurrence_pattern=template.recurrence_pattern,
                start_date=template.start_date,
                end_date=template.end_date,
                max_occurrences=template.max_occurrences,
                is_active=template.is_active,
                created_at=template.created_at,
                updated_at=template.updated_at
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
                detail=f"Failed to create recurring task template: {str(e)}"
            )

    async def get_recurring_task_template(
        self,
        template_id: UUID,
        user_id: UUID,
        session: Session
    ) -> RecurringTaskTemplateResponse:
        """Get a specific recurring task template."""
        template = self.recurring_service.get_template(template_id, user_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring task template not found"
            )
        
        # Get associated tags if needed
        tags = self.tag_service.get_template_tags(template_id, user_id)
        tag_names = [tag.name for tag in tags]
        
        return RecurringTaskTemplateResponse(
            id=template.id,
            user_id=template.user_id,
            title=template.title,
            description=template.description,
            priority=template.priority,
            recurrence_pattern=template.recurrence_pattern,
            start_date=template.start_date,
            end_date=template.end_date,
            max_occurrences=template.max_occurrences,
            is_active=template.is_active,
            tags=tag_names,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    async def get_user_recurring_task_templates(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ) -> List[RecurringTaskTemplateResponse]:
        """Get all recurring task templates for a user."""
        try:
            templates = self.recurring_service.get_user_templates(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
            
            responses = []
            for template in templates:
                # Get associated tags
                tags = self.tag_service.get_template_tags(template.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                responses.append(RecurringTaskTemplateResponse(
                    id=template.id,
                    user_id=template.user_id,
                    title=template.title,
                    description=template.description,
                    priority=template.priority,
                    recurrence_pattern=template.recurrence_pattern,
                    start_date=template.start_date,
                    end_date=template.end_date,
                    max_occurrences=template.max_occurrences,
                    is_active=template.is_active,
                    tags=tag_names,
                    created_at=template.created_at,
                    updated_at=template.updated_at
                ))
            
            return responses
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get recurring task templates: {str(e)}"
            )

    async def update_recurring_task_template(
        self,
        template_id: UUID,
        user_id: UUID,
        update_data: RecurringTaskTemplateUpdate,
        session: Session
    ) -> RecurringTaskTemplateResponse:
        """Update a recurring task template."""
        # Get the existing template to verify it exists and belongs to the user
        existing_template = self.recurring_service.get_template(template_id, user_id)
        if not existing_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring task template not found"
            )
        
        try:
            # Validate the recurrence pattern if it's being updated
            if update_data.recurrence_pattern is not None:
                self._validate_recurrence_pattern(update_data.recurrence_pattern)
            
            # Update the template
            updated_template = self.recurring_service.update_template(
                template_id=template_id,
                user_id=user_id,
                update_data=update_data
            )
            
            if not updated_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recurring task template not found"
                )
            
            # Update tags if provided
            if update_data.tags is not None:
                # Remove all existing tags
                existing_tags = self.tag_service.get_template_tags(template_id, user_id)
                for tag in existing_tags:
                    self.tag_service.remove_tag_from_template(template_id, tag.id, user_id)
                
                # Add new tags
                if update_data.tags:
                    for tag_name in update_data.tags:
                        # Get or create the tag
                        tag = self.tag_service.get_tag_by_name(user_id, tag_name)
                        if not tag:
                            from ..schemas.tag import TagCreate
                            tag_create = TagCreate(name=tag_name)
                            tag = self.tag_service.create_tag(user_id, tag_create)
                        
                        # Associate the tag with the template
                        self.tag_service.add_tag_to_template(updated_template.id, tag.id, user_id)
            
            # Log and publish the template update event
            await self.event_service.log_recurring_task_template_updated(
                user_id=user_id,
                template_id=updated_template.id,
                update_data=update_data.dict()
            )
            
            # Convert to response model
            tags = self.tag_service.get_template_tags(updated_template.id, user_id)
            tag_names = [tag.name for tag in tags]
            
            return RecurringTaskTemplateResponse(
                id=updated_template.id,
                user_id=updated_template.user_id,
                title=updated_template.title,
                description=updated_template.description,
                priority=updated_template.priority,
                recurrence_pattern=updated_template.recurrence_pattern,
                start_date=updated_template.start_date,
                end_date=updated_template.end_date,
                max_occurrences=updated_template.max_occurrences,
                is_active=updated_template.is_active,
                tags=tag_names,
                created_at=updated_template.created_at,
                updated_at=updated_template.updated_at
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
                detail=f"Failed to update recurring task template: {str(e)}"
            )

    async def delete_recurring_task_template(
        self,
        template_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Delete (deactivate) a recurring task template."""
        # Verify the template exists and belongs to the user
        template = self.recurring_service.get_template(template_id, user_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring task template not found"
            )
        
        try:
            # Delete the template (actually deactivate it)
            success = self.recurring_service.delete_template(template_id, user_id)
            
            if success:
                # Log and publish the template deletion event
                await self.event_service.log_recurring_task_template_deleted(
                    user_id=user_id,
                    template_id=template_id
                )
            
            return success
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete recurring task template: {str(e)}"
            )

    def _validate_recurrence_pattern(self, pattern: dict) -> bool:
        """Validate the recurrence pattern."""
        # Check required fields
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
        
        # Validate byweekday if provided (for weekly patterns)
        if freq == 'weekly' and 'byweekday' in pattern:
            valid_weekdays = {'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'}
            byweekday = pattern['byweekday']
            if not isinstance(byweekday, list):
                raise ValueError("'byweekday' must be a list of weekday abbreviations")
            
            for day in byweekday:
                if day not in valid_weekdays:
                    raise ValueError(f"Invalid weekday '{day}'. Must be one of: MO, TU, WE, TH, FR, SA, SU")
        
        # Validate until if provided
        if 'until' in pattern:
            try:
                datetime.fromisoformat(pattern['until'].replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("'until' must be a valid ISO 8601 date string")
        
        # Validate count if provided
        if 'count' in pattern:
            count = pattern['count']
            if not isinstance(count, int) or count < 1:
                raise ValueError("'count' must be a positive integer")
        
        return True


def get_recurring_task_controller(
    recurring_service: RecurringTaskService = Depends(),
    event_service: EventService = Depends()
) -> RecurringTaskController:
    """Get a RecurringTaskController instance with dependencies."""
    return RecurringTaskController(
        recurring_service=recurring_service,
        event_service=event_service
    )