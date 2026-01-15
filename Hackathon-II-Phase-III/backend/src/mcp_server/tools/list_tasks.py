"""
List tasks tool implementation.

Lists all tasks for the authenticated user, optionally filtered by completion status.
"""

import logging
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..auth import AuthError, validate_token
from ..database import async_engine
from ..models import Task

logger = logging.getLogger(__name__)


async def handle(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle list_tasks tool call.

    Args:
        arguments: Tool arguments with optional filter_completed and JWT token

    Returns:
        Response dict with success status and task list
    """
    # Extract arguments
    filter_completed: Optional[bool] = arguments.get("filter_completed")
    token = arguments.get("_jwt_token")  # Token passed in context

    # Validate JWT and extract user_id
    try:
        user_id = validate_token(token)
    except AuthError as e:
        return {
            "success": False,
            "error": {
                "code": "AUTH_ERROR",
                "message": str(e)
            }
        }

    # Query tasks
    try:
        async with AsyncSession(async_engine) as session:
            query = select(Task).where(Task.user_id == user_id)

            # Apply filter if specified
            if filter_completed is not None:
                query = query.where(Task.is_completed == filter_completed)

            # Order by created_at descending
            query = query.order_by(Task.created_at.desc())

            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Listed {len(tasks)} tasks for user {user_id}")

            return {
                "success": True,
                "data": {
                    "tasks": [
                        {
                            "id": str(task.id),
                            "title": task.title,
                            "description": task.description,
                            "is_completed": task.is_completed,
                            "created_at": task.created_at.isoformat()
                        }
                        for task in tasks
                    ]
                }
            }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to list tasks"
            }
        }
