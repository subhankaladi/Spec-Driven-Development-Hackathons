"""Task API endpoints."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from datetime import datetime

from src.models.database import get_session
from src.models.task import Task
from src.services.tag_service import get_tag_service, TagService
from src.services.event_service import get_event_service, EventService
from src.api.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from src.api.schemas.errors import ValidationError, NotFoundError
from src.api.dependencies.auth import get_current_user, TokenUser


router = APIRouter()


class TaskService:
    """Service class for task operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_task(self, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task for a user."""
        # Validate title
        if not task_data.title or not task_data.title.strip():
            raise ValidationError(message="Title is required and cannot be empty")

        # Create the task with advanced features
        task = Task(
            user_id=user_id,
            title=task_data.title.strip(),
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        
        # Associate tags if provided
        if task_data.tags:
            tag_service = get_tag_service(self.session)
            for tag_name in task_data.tags:
                # Get or create the tag
                tag = tag_service.get_tag_by_name(user_id, tag_name)
                if not tag:
                    from src.models.tag import TagCreate
                    tag_data = TagCreate(name=tag_name)
                    tag = tag_service.create_tag(user_id, tag_data)
                
                # Associate the tag with the task
                tag_service.add_tag_to_task(task.id, tag.id, user_id)
        
        return task

    def get_tasks(
        self,
        user_id: UUID,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
        priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
        due_after: Optional[datetime] = Query(None, description="Filter tasks with due date after this date"),
        due_before: Optional[datetime] = Query(None, description="Filter tasks with due date before this date"),
        completed: Optional[bool] = Query(None, description="Filter by completion status"),
    ) -> TaskListResponse:
        """Get all tasks for a user with pagination and filtering."""
        # Calculate offset
        offset = (page - 1) * page_size

        # Build the query with filters
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply filters
        if priority:
            query = query.where(Task.priority == priority)
        if due_after:
            query = query.where(Task.due_date >= due_after)
        if due_before:
            query = query.where(Task.due_date <= due_before)
        if completed is not None:
            query = query.where(Task.is_completed == completed)

        # Count total for pagination
        count_query = select(Task).where(Task.user_id == user_id)
        if priority:
            count_query = count_query.where(Task.priority == priority)
        if due_after:
            count_query = count_query.where(Task.due_date >= due_after)
        if due_before:
            count_query = count_query.where(Task.due_date <= due_before)
        if completed is not None:
            count_query = count_query.where(Task.is_completed == completed)

        # Get total count
        total = len(self.session.exec(count_query).all())

        # Get paginated results, ordered by created_at desc
        task_instances = self.session.exec(
            query.offset(offset).limit(page_size).order_by(Task.created_at.desc())
        ).all()

        # Convert SQLModel instances to TaskResponse Pydantic models
        items = []
        for task in task_instances:
            # Get associated tags for the task
            tag_service = get_tag_service(self.session)
            tags = tag_service.get_task_tags(task.id, user_id)
            tag_names = [tag.name for tag in tags]
            
            # Create TaskResponse with tags
            task_response = TaskResponse(
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
            items.append(task_response)

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return TaskListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_task(self, user_id: UUID, task_id: UUID) -> Task:
        """Get a single task for a user."""
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundError(resource="Task", resource_id=str(task_id))

        return task

    def update_task(
        self, user_id: UUID, task_id: UUID, task_data: TaskUpdate
    ) -> Task:
        """Update an existing task."""
        task = self.get_task(user_id, task_id)

        # Update fields if provided
        if task_data.title is not None:
            if not task_data.title.strip():
                raise ValidationError(message="Title cannot be empty")
            task.title = task_data.title.strip()

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.is_completed is not None:
            task.is_completed = task_data.is_completed
            
        # Update advanced features if provided
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
            
        if task_data.priority is not None:
            task.priority = task_data.priority

        task.updated_at = __import__("datetime").datetime.utcnow()

        self.session.commit()
        self.session.refresh(task)
        
        # Update tags if provided
        if task_data.tags is not None:
            tag_service = get_tag_service(self.session)
            # Remove all existing tags
            existing_tags = tag_service.get_task_tags(task_id, user_id)
            for tag in existing_tags:
                tag_service.remove_tag_from_task(task_id, tag.id, user_id)
            
            # Add new tags
            for tag_name in task_data.tags:
                # Get or create the tag
                tag = tag_service.get_tag_by_name(user_id, tag_name)
                if not tag:
                    from src.models.tag import TagCreate
                    tag_data = TagCreate(name=tag_name)
                    tag = tag_service.create_tag(user_id, tag_data)
                
                # Associate the tag with the task
                tag_service.add_tag_to_task(task.id, tag.id, user_id)

        return task

    def delete_task(self, user_id: UUID, task_id: UUID) -> None:
        """Delete a task."""
        task = self.get_task(user_id, task_id)
        
        # Remove all tag associations before deleting the task
        tag_service = get_tag_service(self.session)
        existing_tags = tag_service.get_task_tags(task_id, user_id)
        for tag in existing_tags:
            tag_service.remove_tag_from_task(task_id, tag.id, user_id)
        
        self.session.delete(task)
        self.session.commit()


def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    """Dependency to get TaskService instance."""
    return TaskService(session)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Create a new task with advanced features.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot create tasks for other users",
                "details": {"requested_user_id": str(user_id)},
            },
        )
        
    # Create the task
    task = service.create_task(user_id, task_data)
    
    # Log the event
    event_service = await get_event_service(service.session)
    await event_service.log_task_created(user_id, task.id, task_data.dict())
    
    # Return the created task with tags
    tag_service = get_tag_service(service.session)
    tags = tag_service.get_task_tags(task.id, user_id)
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


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks with due date after this date"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks with due date before this date"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """List all tasks for a user with pagination and filtering.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot access other users' tasks",
                "details": {"requested_user_id": str(user_id)},
            },
        )
    return service.get_tasks(user_id, page, page_size, priority, due_after, due_before, completed)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Get a specific task.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot access other users' tasks",
                "details": {"requested_user_id": str(user_id)},
            },
        )
        
    task = service.get_task(user_id, task_id)
    
    # Get associated tags
    tag_service = get_tag_service(service.session)
    tags = tag_service.get_task_tags(task_id, user_id)
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


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Update a task (full update) with advanced features.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot modify other users' tasks",
                "details": {"requested_user_id": str(user_id)},
            },
        )
        
    task = service.update_task(user_id, task_id, task_data)
    
    # Log the event
    event_service = await get_event_service(service.session)
    await event_service.log_task_updated(user_id, task.id, task_data.dict())
    
    # Return the updated task with tags
    tag_service = get_tag_service(service.session)
    tags = tag_service.get_task_tags(task_id, user_id)
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


@router.patch("/{task_id}", response_model=TaskResponse)
async def partial_update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Update a task (partial update) with advanced features.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot modify other users' tasks",
                "details": {"requested_user_id": str(user_id)},
            },
        )
        
    task = service.update_task(user_id, task_id, task_data)
    
    # Log the event
    event_service = await get_event_service(service.session)
    await event_service.log_task_updated(user_id, task.id, task_data.dict())
    
    # Return the updated task with tags
    tag_service = get_tag_service(service.session)
    tags = tag_service.get_task_tags(task_id, user_id)
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


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Delete a task.

    Requires authentication. The authenticated user's ID must match
    the user_id in the URL path.
    """
    # Verify user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot delete other users' tasks",
                "details": {"requested_user_id": str(user_id)},
            },
        )
        
    # Get the task before deletion to log the event
    task = service.get_task(user_id, task_id)
    
    service.delete_task(user_id, task_id)
    
    # Log the event
    event_service = await get_event_service(service.session)
    await event_service.log_task_completed(user_id, task.id, {"action": "deleted"})
    
    return None
