"""List Tasks tool handler - User Story 2 (Priority: P1 - MVP).

Retrieves tasks for the authenticated user with optional filtering and pagination.
"""

import sys
import os
from typing import Dict, Any, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import math

# Add backend to Python path for imports
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.models.task import Task
from ..auth.jwt_validator import validate_jwt_token
from ..utils.errors import ValidationError, AuthenticationError, DatabaseError


async def list_tasks_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """Handle list_tasks tool invocation.

    Retrieves tasks for the authenticated user with optional filtering and pagination.

    Args:
        arguments: Tool input parameters
            - jwt_token (str): JWT authentication token
            - completed (bool, optional): Filter by completion status
            - page (int, optional): Page number (1-indexed, default: 1)
            - page_size (int, optional): Items per page (1-100, default: 20)

        session: Async database session

    Returns:
        Paginated task list with metadata:
            - items (list): Array of task objects
            - total (int): Total tasks matching filter
            - page (int): Current page number
            - page_size (int): Items per page
            - total_pages (int): Total number of pages

    Raises:
        AuthenticationError: Invalid/expired/missing JWT token
        ValidationError: Invalid pagination parameters
        DatabaseError: Database operation failed

    Example:
        >>> result = await list_tasks_handler(
        ...     arguments={
        ...         "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
        ...         "completed": False,
        ...         "page": 1,
        ...         "page_size": 20
        ...     },
        ...     session=async_session
        ... )
        >>> print(len(result["items"]))
        15
        >>> print(result["total"])
        15
    """
    # Step 1: Validate JWT token and extract user_id
    jwt_token = arguments.get("jwt_token")
    user_id = await validate_jwt_token(jwt_token)

    # Step 2: Validate pagination parameters
    page = arguments.get("page", 1)
    page_size = arguments.get("page_size", 20)

    if not isinstance(page, int) or page < 1:
        raise ValidationError("Page must be an integer >= 1")

    if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
        raise ValidationError("Page size must be an integer between 1 and 100")

    # Step 3: Extract optional filter
    completed_filter: Optional[bool] = arguments.get("completed")

    # Step 4: Build query with user scoping and optional filter
    try:
        from uuid import UUID

        # Base query: user-scoped
        query = select(Task).where(Task.user_id == UUID(user_id))

        # Apply completion filter if provided
        if completed_filter is not None:
            if not isinstance(completed_filter, bool):
                raise ValidationError("Completed filter must be a boolean")
            query = query.where(Task.is_completed == completed_filter)

        # Order by created_at DESC (newest first)
        query = query.order_by(Task.created_at.desc())

        # Execute count query for total
        count_query = select(Task).where(Task.user_id == UUID(user_id))
        if completed_filter is not None:
            count_query = count_query.where(Task.is_completed == completed_filter)

        result = await session.exec(count_query)
        total = len(result.all())

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute paginated query
        result = await session.exec(query)
        tasks = result.all()

    except Exception as e:
        raise DatabaseError(f"Failed to retrieve tasks: {str(e)}")

    # Step 5: Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Step 6: Convert tasks to structured response
    items = [
        {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
        for task in tasks
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
