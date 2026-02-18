"""Task Controller for advanced task management features."""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from ..models.task import Task
from ..models.database import get_session
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..schemas.search import SearchRequest, SearchResponse
from ..services.task_service import TaskService
from ..services.search_service import SearchService
from ..services.tag_service import TagService
from ..services.event_service import EventService
from ..services.recurring_service import RecurringTaskService
from ..services.reminder_service import ReminderService


class TaskController:
    """Controller class for handling advanced task management operations."""

    def __init__(
        self,
        task_service: TaskService,
        search_service: SearchService,
        tag_service: TagService,
        event_service: EventService,
        recurring_service: RecurringTaskService,
        reminder_service: ReminderService
    ):
        self.task_service = task_service
        self.search_service = search_service
        self.tag_service = tag_service
        self.event_service = event_service
        self.recurring_service = recurring_service
        self.reminder_service = reminder_service

    async def create_task(
        self,
        user_id: UUID,
        task_data: TaskCreate,
        session: Session
    ) -> TaskResponse:
        """Create a new task with advanced features."""
        try:
            # Create the task
            task = self.task_service.create_task(user_id, task_data)
            
            # Process tags if provided
            if task_data.tags:
                for tag_name in task_data.tags:
                    # Get or create the tag
                    tag = self.tag_service.get_tag_by_name(user_id, tag_name)
                    if not tag:
                        from ..schemas.tag import TagCreate
                        tag_create = TagCreate(name=tag_name)
                        tag = self.tag_service.create_tag(user_id, tag_create)
                    
                    # Associate the tag with the task
                    self.tag_service.add_tag_to_task(task.id, tag.id, user_id)
            
            # Log and publish the task creation event
            await self.event_service.log_task_created(
                user_id=user_id,
                task_id=task.id,
                task_data=task_data.dict()
            )
            
            # Create reminder if due date is set
            if task_data.due_date:
                from ..schemas.reminder import ReminderCreate
                reminder_data = ReminderCreate(
                    task_instance_id=task.id,
                    reminder_time=task_data.due_date,
                    method="push"  # Default reminder method
                )
                reminder = self.reminder_service.create_reminder(user_id, reminder_data)
            
            # Convert to response model
            return TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                due_date=task.due_date,
                priority=task.priority,
                parent_template_id=task.parent_template_id,
                tags=task_data.tags or [],
                created_at=task.created_at,
                updated_at=task.updated_at
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create task: {str(e)}"
            )

    async def get_task(
        self,
        task_id: UUID,
        user_id: UUID,
        session: Session
    ) -> TaskResponse:
        """Get a specific task with all its details."""
        task = self.task_service.get_task(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Get associated tags
        tags = self.tag_service.get_task_tags(task_id, user_id)
        tag_names = [tag.name for tag in tags]
        
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            due_date=task.due_date,
            priority=task.priority,
            parent_template_id=task.parent_template_id,
            tags=tag_names,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    async def update_task(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: TaskUpdate,
        session: Session
    ) -> TaskResponse:
        """Update a task with advanced features."""
        task = self.task_service.get_task(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        try:
            # Update the task
            updated_task = self.task_service.update_task(task_id, user_id, task_data)
            
            # Update tags if provided
            if task_data.tags is not None:
                # Remove all existing tags
                existing_tags = self.tag_service.get_task_tags(task_id, user_id)
                for tag in existing_tags:
                    self.tag_service.remove_tag_from_task(task_id, tag.id, user_id)
                
                # Add new tags
                if task_data.tags:
                    for tag_name in task_data.tags:
                        # Get or create the tag
                        tag = self.tag_service.get_tag_by_name(user_id, tag_name)
                        if not tag:
                            from ..schemas.tag import TagCreate
                            tag_create = TagCreate(name=tag_name)
                            tag = self.tag_service.create_tag(user_id, tag_create)
                        
                        # Associate the tag with the task
                        self.tag_service.add_tag_to_task(updated_task.id, tag.id, user_id)
            
            # Log and publish the task update event
            await self.event_service.log_task_updated(
                user_id=user_id,
                task_id=updated_task.id,
                task_data=task_data.dict()
            )
            
            # Update reminder if due date changed
            if task_data.due_date:
                # Check if a reminder already exists for this task
                existing_reminders = self.reminder_service.get_user_reminders(user_id)
                task_reminder = next((r for r in existing_reminders if r.task_instance_id == updated_task.id), None)
                
                if task_reminder:
                    # Update existing reminder
                    from ..schemas.reminder import ReminderUpdate
                    reminder_update = ReminderUpdate(
                        reminder_time=task_data.due_date
                    )
                    self.reminder_service.update_reminder(task_reminder.id, user_id, reminder_update)
                else:
                    # Create new reminder
                    from ..schemas.reminder import ReminderCreate
                    reminder_data = ReminderCreate(
                        task_instance_id=updated_task.id,
                        reminder_time=task_data.due_date,
                        method="push"  # Default reminder method
                    )
                    self.reminder_service.create_reminder(user_id, reminder_data)
            
            # Convert to response model
            tags = self.tag_service.get_task_tags(updated_task.id, user_id)
            tag_names = [tag.name for tag in tags]
            
            return TaskResponse(
                id=updated_task.id,
                user_id=updated_task.user_id,
                title=updated_task.title,
                description=updated_task.description,
                is_completed=updated_task.is_completed,
                due_date=updated_task.due_date,
                priority=updated_task.priority,
                parent_template_id=updated_task.parent_template_id,
                tags=tag_names,
                created_at=updated_task.created_at,
                updated_at=updated_task.updated_at
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update task: {str(e)}"
            )

    async def delete_task(
        self,
        task_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Delete a task and its associations."""
        # Get the task to verify it exists and belongs to the user
        task = self.task_service.get_task(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        try:
            # Remove all tag associations
            tags = self.tag_service.get_task_tags(task_id, user_id)
            for tag in tags:
                self.tag_service.remove_tag_from_task(task_id, tag.id, user_id)
            
            # Delete any associated reminders
            reminders = self.reminder_service.get_user_reminders(user_id)
            for reminder in reminders:
                if reminder.task_instance_id == task_id:
                    self.reminder_service.delete_reminder(reminder.id, user_id)
            
            # Delete the task
            success = self.task_service.delete_task(task_id, user_id)
            
            if success:
                # Log and publish the task deletion event
                await self.event_service.log_task_deleted(
                    user_id=user_id,
                    task_id=task_id,
                    task_data={"deleted_at": datetime.utcnow()}
                )
            
            return success
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete task: {str(e)}"
            )

    async def search_tasks(
        self,
        user_id: UUID,
        search_request: SearchRequest,
        session: Session
    ) -> SearchResponse:
        """Search tasks with advanced filters, sorting, and pagination."""
        try:
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(search_request.page - 1) * search_request.page_size,
                limit=search_request.page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + search_request.page_size - 1) // search_request.page_size if total > 0 else 1
            
            return SearchResponse(
                items=items,
                total=total,
                page=search_request.page,
                page_size=search_request.page_size,
                total_pages=total_pages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Search failed: {str(e)}"
            )

    async def get_user_tasks(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        priority: Optional[str] = None,
        due_after: Optional[datetime] = None,
        due_before: Optional[datetime] = None,
        completed: Optional[bool] = None,
        session: Session = Depends(get_session)
    ) -> List[TaskResponse]:
        """Get all tasks for a user with optional filters."""
        try:
            # Get tasks from service with filters
            tasks = self.task_service.get_tasks(
                user_id=user_id,
                skip=skip,
                limit=limit,
                priority=priority,
                due_after=due_after,
                due_before=due_before,
                completed=completed
            )
            
            # Convert to response models
            responses = []
            for task in tasks:
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                responses.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            return responses
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user tasks: {str(e)}"
            )


def get_task_controller(
    task_service: TaskService = Depends(),
    search_service: SearchService = Depends(),
    tag_service: TagService = Depends(),
    event_service: EventService = Depends(),
    recurring_service: RecurringTaskService = Depends(),
    reminder_service: ReminderService = Depends()
) -> TaskController:
    """Get a TaskController instance with dependencies."""
    return TaskController(
        task_service=task_service,
        search_service=search_service,
        tag_service=tag_service,
        event_service=event_service,
        recurring_service=recurring_service,
        reminder_service=reminder_service
    )