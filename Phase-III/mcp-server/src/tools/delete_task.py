"""Delete Task tool handler - User Story 5 (Priority: P3).

Permanently removes a task from the database for the authenticated user.
"""

import sys
import os
from typing import Dict, Any
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


async def delete_task_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """Handle delete_task tool invocation.

    Permanently removes a task from the database for the authenticated user.
    NOT idempotent - calling on non-existent task returns NOT_FOUND error.

    Args:
        arguments: Tool input parameters
            - jwt_token (str): JWT authentication token
            - task_id (str): Task UUID to delete

        session: Async database session

    Returns:
        Deletion confirmation:
            - deleted (bool): Always true on success
            - task_id (str): ID of deleted task

    Raises:
        AuthenticationError: Invalid/expired/missing JWT token
        ValidationError: Invalid task_id format
        NotFoundError: Task not found or already deleted
        AuthorizationError: Task belongs to different user
        DatabaseError: Database operation failed

    Example:
        >>> result = await delete_task_handler(
        ...     arguments={
        ...         "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
        ...         "task_id": "123e4567-e89b-12d3-a456-426614174000"
        ...     },
        ...     session=async_session
        ... )
        >>> print(result["deleted"])
        True
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

    # Step 3: Query task with user_id check
    try:
        query = select(Task).where(Task.id == task_uuid)
        result = await session.exec(query)
        task = result.first()

        # Check if task exists
        if not task:
            raise NotFoundError(f"Task not found or already deleted: {task_id_str}")

        # Check authorization (task must belong to user)
        if task.user_id != user_uuid:
            raise AuthorizationError("Task belongs to different user")

        # Step 4: Delete task (hard delete - permanent removal)
        await session.delete(task)
        await session.commit()

    except (NotFoundError, AuthorizationError, ValidationError):
        # Re-raise application errors
        raise

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Failed to delete task: {str(e)}")

    # Step 5: Return deletion confirmation
    return {
        "deleted": True,
        "task_id": task_id_str
    }
