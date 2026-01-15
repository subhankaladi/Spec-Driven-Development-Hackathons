from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlmodel import Session, select, func
from typing import List, Optional
import logging
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskListResponse
from src.database.session import get_session
from src.auth.dependencies import get_current_user_id

# Configure logging for security events
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """Create a new task for the authenticated user."""
    # Validate title is not empty or whitespace-only
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    try:
        db_task = Task(
            title=task.title.strip(),
            description=task.description.strip() if task.description else None,
            is_completed=task.is_completed,
            owner_id=request_user_id  # Associate task with authenticated user
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=TaskListResponse)
def read_tasks(
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    is_completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip")
) -> TaskListResponse:
    """Get all tasks for the authenticated user with optional filtering and pagination."""
    # Base query filtered by owner
    base_query = select(Task).where(Task.owner_id == request_user_id)

    # Apply completion status filter if provided
    if is_completed is not None:
        base_query = base_query.where(Task.is_completed == is_completed)

    # Get total count for pagination metadata
    count_query = select(func.count()).select_from(Task).where(Task.owner_id == request_user_id)
    if is_completed is not None:
        count_query = count_query.where(Task.is_completed == is_completed)
    total = session.exec(count_query).one()

    # Apply pagination
    paginated_query = base_query.offset(offset).limit(limit)
    tasks = session.exec(paginated_query).all()

    return TaskListResponse(
        items=tasks,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """Get a specific task by ID, ensuring it belongs to the authenticated user."""
    task = session.get(Task, task_id)
    z

    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task: TaskUpdate,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """Update a specific task by ID, ensuring it belongs to the authenticated user."""
    from datetime import datetime

    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task belongs to the authenticated user
    if db_task.owner_id != request_user_id:
        logger.warning(f"Security: User {request_user_id} attempted to update task {task_id} owned by {db_task.owner_id}")
        raise HTTPException(status_code=403, detail="Access denied: task does not belong to user")

    # Update fields that were provided
    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.is_completed is not None:
        db_task.is_completed = task.is_completed

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    task: TaskUpdate,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """Partially update a task by ID, ideal for toggling completion status."""
    from datetime import datetime

    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task belongs to the authenticated user
    if db_task.owner_id != request_user_id:
        logger.warning(f"Security: User {request_user_id} attempted to patch task {task_id} owned by {db_task.owner_id}")
        raise HTTPException(status_code=403, detail="Access denied: task does not belong to user")

    # Update only the fields that were provided
    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.is_completed is not None:
        db_task.is_completed = task.is_completed

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    request_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Delete a specific task by ID, ensuring it belongs to the authenticated user."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the task belongs to the authenticated user
    if task.owner_id != request_user_id:
        logger.warning(f"Security: User {request_user_id} attempted to delete task {task_id} owned by {task.owner_id}")
        raise HTTPException(status_code=403, detail="Access denied: task does not belong to user")

    logger.info(f"User {request_user_id} deleted task {task_id}")
    session.delete(task)
    session.commit()
    return