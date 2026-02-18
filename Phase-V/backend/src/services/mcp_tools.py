"""MCP tools for AI agent to interact with task management system.

These tools follow the Model Context Protocol specification, providing
stateless, validated task operations that enforce user isolation.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
import logging

from ..models.task import Task
from ..api.schemas.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


def create_task(
    title: str,
    description: Optional[str],
    user_id: UUID,
    session: Session
) -> Dict[str, Any]:
    """Create a new task for the authenticated user.

    This MCP tool validates input, creates a task in the database, and returns
    a structured response. It enforces user isolation by requiring user_id.

    Args:
        title: Task title (required, 1-255 characters)
        description: Optional task description
        user_id: UUID of the authenticated user (from JWT token)
        session: Database session for transaction management

    Returns:
        dict: Created task data with keys:
            - id: str (UUID as string)
            - title: str
            - description: Optional[str]
            - is_completed: bool (always False for new tasks)
            - created_at: str (ISO 8601 datetime)

    Raises:
        ValidationError: If title is empty or exceeds 255 characters
        ValueError: If user_id is invalid
    """
    # Log tool invocation
    logger.info(
        f"MCP Tool: create_task invoked by user_id={user_id}, "
        f"title='{title[:50]}{'...' if len(title) > 50 else ''}'"
    )

    # Validate title
    if not title or not title.strip():
        logger.error(f"create_task failed: Title is empty for user_id={user_id}")
        raise ValidationError(message="Title is required and cannot be empty")

    if len(title.strip()) > 255:
        logger.error(
            f"create_task failed: Title too long ({len(title.strip())} chars) "
            f"for user_id={user_id}"
        )
        raise ValidationError(
            message="Title must be 1-255 characters",
            details={"title_length": len(title.strip())}
        )

    # Validate user_id
    if not isinstance(user_id, UUID):
        logger.error(f"create_task failed: Invalid user_id type {type(user_id)}")
        raise ValueError(f"Invalid user_id: must be UUID, got {type(user_id)}")

    # Create task
    task = Task(
        user_id=user_id,
        title=title.strip(),
        description=description,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"create_task succeeded: Created task_id={task.id} for user_id={user_id}")

    # Return structured response matching MCP output schema
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat()
    }


def list_tasks(
    user_id: UUID,
    session: Session,
    is_completed: Optional[bool] = None,
    limit: int = 10
) -> list[Dict[str, Any]]:
    """List tasks for the authenticated user with optional filtering.

    This MCP tool retrieves tasks from the database with user isolation
    and optional completion status filtering.

    Args:
        user_id: UUID of the authenticated user (from JWT token)
        session: Database session for query execution
        is_completed: Optional filter by completion status (None = all tasks)
        limit: Maximum number of tasks to return (1-100, default 10)

    Returns:
        list[dict]: Array of task dictionaries, each with:
            - id: str (UUID as string)
            - title: str
            - description: Optional[str]
            - is_completed: bool
            - created_at: str (ISO 8601 datetime)
            - updated_at: str (ISO 8601 datetime)

    Raises:
        ValueError: If user_id is invalid or limit is out of range
    """
    # Log tool invocation
    logger.info(
        f"MCP Tool: list_tasks invoked by user_id={user_id}, "
        f"is_completed={is_completed}, limit={limit}"
    )

    # Validate user_id
    if not isinstance(user_id, UUID):
        logger.error(f"list_tasks failed: Invalid user_id type {type(user_id)}")
        raise ValueError(f"Invalid user_id: must be UUID, got {type(user_id)}")

    # Validate limit
    if not (1 <= limit <= 100):
        logger.error(f"list_tasks failed: Invalid limit {limit} for user_id={user_id}")
        raise ValueError(f"Limit must be between 1 and 100, got {limit}")

    # Build query with user isolation
    query = select(Task).where(Task.user_id == user_id)

    # Apply completion status filter if provided
    if is_completed is not None:
        query = query.where(Task.is_completed == is_completed)

    # Order by created_at descending (most recent first)
    query = query.order_by(Task.created_at.desc()).limit(limit)

    # Execute query
    tasks = session.exec(query).all()

    logger.info(f"list_tasks succeeded: Retrieved {len(tasks)} tasks for user_id={user_id}")

    # Convert to MCP output schema format
    return [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
        for task in tasks
    ]


def update_task(
    task_id: UUID,
    user_id: UUID,
    session: Session,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> Dict[str, Any]:
    """Update an existing task for the authenticated user.

    This MCP tool updates task fields with validation and user isolation.
    Only provided fields are updated (partial update supported).

    Args:
        task_id: UUID of the task to update
        user_id: UUID of the authenticated user (from JWT token)
        session: Database session for transaction management
        title: Optional new task title (1-255 characters)
        description: Optional new task description
        is_completed: Optional new completion status

    Returns:
        dict: Updated task data with keys:
            - id: str (UUID as string)
            - title: str
            - description: Optional[str]
            - is_completed: bool
            - updated_at: str (ISO 8601 datetime)

    Raises:
        NotFoundError: If task does not exist or does not belong to user
        ValidationError: If title is empty or exceeds 255 characters
        ValueError: If user_id or task_id is invalid
    """
    # Log tool invocation
    logger.info(
        f"MCP Tool: update_task invoked by user_id={user_id}, task_id={task_id}, "
        f"title={'SET' if title else 'UNCHANGED'}, "
        f"description={'SET' if description is not None else 'UNCHANGED'}, "
        f"is_completed={'SET' if is_completed is not None else 'UNCHANGED'}"
    )

    # Validate UUIDs
    if not isinstance(user_id, UUID):
        logger.error(f"update_task failed: Invalid user_id type {type(user_id)}")
        raise ValueError(f"Invalid user_id: must be UUID, got {type(user_id)}")
    if not isinstance(task_id, UUID):
        logger.error(f"update_task failed: Invalid task_id type {type(task_id)}")
        raise ValueError(f"Invalid task_id: must be UUID, got {type(task_id)}")

    # Retrieve task with user isolation
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        logger.error(
            f"update_task failed: Task {task_id} not found or not owned by user_id={user_id}"
        )
        raise NotFoundError(
            resource="Task",
            resource_id=str(task_id),
            message="Task does not exist or does not belong to user"
        )

    # Update title if provided
    if title is not None:
        if not title.strip():
            logger.error(f"update_task failed: Empty title for task_id={task_id}")
            raise ValidationError(message="Title cannot be empty")
        if len(title.strip()) > 255:
            logger.error(
                f"update_task failed: Title too long ({len(title.strip())} chars) "
                f"for task_id={task_id}"
            )
            raise ValidationError(
                message="Title must be 1-255 characters",
                details={"title_length": len(title.strip())}
            )
        task.title = title.strip()

    # Update description if provided
    if description is not None:
        task.description = description

    # Update completion status if provided
    if is_completed is not None:
        task.is_completed = is_completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"update_task succeeded: Updated task_id={task_id} for user_id={user_id}")

    # Return structured response matching MCP output schema
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "updated_at": task.updated_at.isoformat()
    }


def delete_task(
    task_id: UUID,
    user_id: UUID,
    session: Session
) -> Dict[str, Any]:
    """Delete a task for the authenticated user.

    This MCP tool deletes a task with user isolation enforcement.

    Args:
        task_id: UUID of the task to delete
        user_id: UUID of the authenticated user (from JWT token)
        session: Database session for transaction management

    Returns:
        dict: Deletion confirmation with keys:
            - success: bool (always True if no exception raised)
            - deleted_task_id: str (UUID as string)

    Raises:
        NotFoundError: If task does not exist or does not belong to user
        ValueError: If user_id or task_id is invalid
    """
    # Log tool invocation
    logger.info(f"MCP Tool: delete_task invoked by user_id={user_id}, task_id={task_id}")

    # Validate UUIDs
    if not isinstance(user_id, UUID):
        logger.error(f"delete_task failed: Invalid user_id type {type(user_id)}")
        raise ValueError(f"Invalid user_id: must be UUID, got {type(user_id)}")
    if not isinstance(task_id, UUID):
        logger.error(f"delete_task failed: Invalid task_id type {type(task_id)}")
        raise ValueError(f"Invalid task_id: must be UUID, got {type(task_id)}")

    # Retrieve task with user isolation
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        logger.error(
            f"delete_task failed: Task {task_id} not found or not owned by user_id={user_id}"
        )
        raise NotFoundError(
            resource="Task",
            resource_id=str(task_id),
            message="Task does not exist or does not belong to user"
        )

    # Delete task
    session.delete(task)
    session.commit()

    logger.info(f"delete_task succeeded: Deleted task_id={task_id} for user_id={user_id}")

    # Return structured response matching MCP output schema
    return {
        "success": True,
        "deleted_task_id": str(task_id)
    }
