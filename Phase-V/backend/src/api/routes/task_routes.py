"""Task API routes with advanced features."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.user import User
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from ..schemas.search import SearchRequest, SearchResponse
from ..controllers.task_controller import get_task_controller, TaskController
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Create a new task with advanced features."""
    return await controller.create_task(
        user_id=current_user.id,
        task_data=task_data,
        session=session
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get a specific task."""
    return await controller.get_task(
        task_id=task_id,
        user_id=current_user.id,
        session=session
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Update a task with advanced features."""
    return await controller.update_task(
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data,
        session=session
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Delete a task and its associations."""
    success = await controller.delete_task(
        task_id=task_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    priority: str = Query(None),
    due_after: datetime = Query(None),
    due_before: datetime = Query(None),
    completed: bool = Query(None),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get all tasks for a user with optional filters."""
    return await controller.get_user_tasks(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        priority=priority,
        due_after=due_after,
        due_before=due_before,
        completed=completed,
        session=session
    )


@router.post("/search", response_model=SearchResponse)
async def search_tasks(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Search tasks with advanced filters, sorting, and pagination."""
    return await controller.search_tasks(
        user_id=current_user.id,
        search_request=search_request,
        session=session
    )


# Additional routes for advanced features

@router.get("/{task_id}/tags", response_model=List[TagResponse])
async def get_task_tags(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get all tags associated with a task."""
    return await controller.get_task_tags(
        task_instance_id=task_id,
        user_id=current_user.id,
        session=session
    )


@router.post("/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_task(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Associate a tag with a task."""
    success = await controller.add_tag_to_task(
        task_instance_id=task_id,
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or tag not found"
        )
    
    return


@router.delete("/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_task(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Remove a tag association from a task."""
    success = await controller.remove_tag_from_task(
        task_instance_id=task_id,
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or tag not found, or association doesn't exist"
        )
    
    return


@router.get("/stats", response_model=dict)
async def get_task_stats(
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get task statistics for the user."""
    return await controller.get_user_task_stats(
        user_id=current_user.id,
        session=session
    )


@router.get("/upcoming", response_model=List[TaskResponse])
async def get_upcoming_tasks(
    current_user: User = Depends(get_current_user),
    hours_ahead: int = Query(24, ge=1),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get tasks due in the next specified number of hours."""
    return await controller.get_upcoming_tasks(
        user_id=current_user.id,
        hours_ahead=hours_ahead,
        session=session
    )


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
    session: Session = Depends(get_session)
):
    """Get all overdue tasks for the user."""
    return await controller.get_overdue_tasks(
        user_id=current_user.id,
        session=session
    )