"""Add Task tool handler - User Story 1 (Priority: P1 - MVP).

Creates a new task for the authenticated user with JWT validation and
structured error handling.
"""

import sys
import os
from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession

# Add backend to Python path for imports
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.models.task import Task
from ..auth.jwt_validator import validate_jwt_token
from ..utils.errors import ValidationError, AuthenticationError, DatabaseError


async def add_task_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """Handle add_task tool invocation.

    Creates a new task in the database for the authenticated user.

    Args:
        arguments: Tool input parameters
            - jwt_token (str): JWT authentication token
            - title (str): Task title (1-255 characters)
            - description (str, optional): Task description

        session: Async database session

    Returns:
        Task object as dictionary with fields:
            - id (str): Task UUID
            - user_id (str): Owner UUID
            - title (str): Task title
            - description (str | null): Task description
            - is_completed (bool): Always false for new tasks
            - created_at (str): ISO 8601 timestamp
            - updated_at (str): ISO 8601 timestamp

    Raises:
        AuthenticationError: Invalid/expired/missing JWT token
        ValidationError: Invalid input parameters
        DatabaseError: Database operation failed

    Example:
        >>> result = await add_task_handler(
        ...     arguments={
        ...         "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
        ...         "title": "Buy groceries",
        ...         "description": "Milk, eggs, bread"
        ...     },
        ...     session=async_session
        ... )
        >>> print(result["title"])
        'Buy groceries'
    """
    # Step 1: Validate JWT token and extract user_id
    jwt_token = arguments.get("jwt_token")
    user_id = await validate_jwt_token(jwt_token)

    # Step 2: Validate input parameters
    title = arguments.get("title", "").strip() if arguments.get("title") else ""

    if not title:
        raise ValidationError("Title is required and cannot be empty")

    if len(title) > 255:
        raise ValidationError("Title must be 255 characters or less")

    if len(title) < 1:
        raise ValidationError("Title must be at least 1 character")

    description = arguments.get("description")

    # Normalize empty string to None
    if description == "":
        description = None

    # Step 3: Create new task
    try:
        from uuid import UUID

        new_task = Task(
            user_id=UUID(user_id),
            title=title,
            description=description,
            is_completed=False
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Failed to create task: {str(e)}")

    # Step 4: Return structured response
    return {
        "id": str(new_task.id),
        "user_id": str(new_task.user_id),
        "title": new_task.title,
        "description": new_task.description,
        "is_completed": new_task.is_completed,
        "created_at": new_task.created_at.isoformat(),
        "updated_at": new_task.updated_at.isoformat()
    }
