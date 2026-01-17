"""Task API endpoints."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from src.models.database import get_session
from src.models.task import Task
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

        task = Task(
            user_id=user_id,
            title=task_data.title.strip(),
            description=task_data.description,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_tasks(
        self,
        user_id: UUID,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    ) -> TaskListResponse:
        """Get all tasks for a user with pagination."""
        # Calculate offset
        offset = (page - 1) * page_size

        # Query tasks scoped to user
        query = select(Task).where(Task.user_id == user_id)
        count_query = select(Task).where(Task.user_id == user_id)

        # Get total count
        total = len(self.session.exec(count_query).all())

        # Get paginated results, ordered by created_at desc
        task_instances = self.session.exec(
            query.offset(offset).limit(page_size).order_by(Task.created_at.desc())
        ).all()

        # Convert SQLModel instances to TaskResponse Pydantic models
        items = [TaskResponse.model_validate(task) for task in task_instances]

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

        task.updated_at = __import__("datetime").datetime.utcnow()

        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, user_id: UUID, task_id: UUID) -> None:
        """Delete a task."""
        task = self.get_task(user_id, task_id)
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
    """Create a new task.

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
    return service.create_task(user_id, task_data)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """List all tasks for a user with pagination.

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
    return service.get_tasks(user_id, page, page_size)


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
    return service.get_task(user_id, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Update a task (full update).

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
    return service.update_task(user_id, task_id, task_data)


@router.patch("/{task_id}", response_model=TaskResponse)
async def partial_update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Update a task (partial update).

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
    return service.update_task(user_id, task_id, task_data)


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
    service.delete_task(user_id, task_id)
    return None
