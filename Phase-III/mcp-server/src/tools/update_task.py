"""Update Task tool handler - User Story 4 (Priority: P2).

Modifies task title, description, or completion status for the authenticated user.
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Add backend to Python path for imports
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.models.task import Task
from ..auth.jwt_validator import validate_jwt_token
from ..utils.errors import (
    ValidationError,
    AuthenticationError,
    NotFoundError,
    AuthorizationError,
    DatabaseError
)


async def update_task_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """Handle update_task tool invocation.

    Updates task fields (title, description, is_completed) for the authenticated user.
    Only provided fields are updated (partial update).

    Args:
        arguments: Tool input parameters
            - jwt_token (str): JWT authentication token
            - task_id (str): Task UUID to update
            - title (str, optional): New title (1-255 characters)
            - description (str, optional): New description
            - is_completed (bool, optional): New completion status

        session: Async database session

    Returns:
        Updated task object as dictionary

    Raises:
        AuthenticationError: Invalid/expired/missing JWT token
        ValidationError: Invalid task_id format or title validation failed
        NotFoundError: Task not found
        AuthorizationError: Task belongs to different user
        DatabaseError: Database operation failed

    Example:
        >>> result = await update_task_handler(
        ...     arguments={
        ...         "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
        ...         "task_id": "123e4567-e89b-12d3-a456-426614174000",
        ...         "title": "Updated title"
        ...     },
        ...     session=async_session
        ... )
        >>> print(result["title"])
        'Updated title'
    """
    # Step 1: Validate JWT token and extract user_id
    jwt_token = arguments.get("jwt_token")
    user_id = await validate_jwt_token(jwt_token)

    # Step 2: Validate task_id parameter
    task_id_str = arguments.get("task_id")

    if not task_id_str or not isinstance(task_id_str, str):
        raise ValidationError("Task ID is required and must be a string")

    try:
        from uuid import UUID

        task_uuid = UUID(task_id_str)
        user_uuid = UUID(user_id)

    except ValueError:
        raise ValidationError("Invalid task ID format (must be UUID)")

    # Step 3: Extract optional update fields
    new_title: Optional[str] = arguments.get("title")
    new_description: Optional[str] = arguments.get("description")
    new_is_completed: Optional[bool] = arguments.get("is_completed")

    # Validate title if provided
    if new_title is not None:
        new_title = new_title.strip()

        if not new_title:
            raise ValidationError("Title cannot be empty")

        if len(new_title) > 255:
            raise ValidationError("Title must be 255 characters or less")

        if len(new_title) < 1:
            raise ValidationError("Title must be at least 1 character")

    # Validate is_completed if provided
    if new_is_completed is not None and not isinstance(new_is_completed, bool):
        raise ValidationError("is_completed must be a boolean")

    # Normalize empty description to None
    if new_description == "":
        new_description = None

    # Step 4: Query task with user_id check
    try:
        query = select(Task).where(Task.id == task_uuid)
        result = await session.exec(query)
        task = result.first()

        # Check if task exists
        if not task:
            raise NotFoundError(f"Task not found: {task_id_str}")

        # Check authorization (task must belong to user)
        if task.user_id != user_uuid:
            raise AuthorizationError("Task belongs to different user")

        # Step 5: Apply updates (partial update - only update provided fields)
        updated = False

        if new_title is not None:
            task.title = new_title
            updated = True

        if new_description is not None:
            task.description = new_description
            updated = True

        if new_is_completed is not None:
            task.is_completed = new_is_completed
            updated = True

        # Always refresh updated_at if any field changed
        if updated:
            task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

    except (NotFoundError, AuthorizationError, ValidationError):
        # Re-raise application errors
        raise

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Failed to update task: {str(e)}")

    # Step 6: Return updated task
    return {
        "id": str(task.id),
        "user_id": str(task.user_id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }
