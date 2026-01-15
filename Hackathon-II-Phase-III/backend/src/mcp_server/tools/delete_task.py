"""
Delete task tool implementation.

Deletes a task owned by the authenticated user.
"""

import logging
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..auth import AuthError, validate_token
from ..database import async_engine
from ..models import Task

logger = logging.getLogger(__name__)


async def handle(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle delete_task tool call.

    Args:
        arguments: Tool arguments with task_id and JWT token

    Returns:
        Response dict with success status
    """
    # Extract arguments
    task_id_str = arguments.get("task_id", "").strip()
    token = arguments.get("_jwt_token")  # Token passed in context

    # Validate task_id
    if not task_id_str:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Task ID is required"
            }
        }

    try:
        task_id = UUID(task_id_str)
    except ValueError:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid task ID format"
            }
        }

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

    # Delete task
    try:
        async with AsyncSession(async_engine) as session:
            # Query task with ownership check
            query = select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found or access denied"
                    }
                }

            await session.delete(task)
            await session.commit()

            logger.info(f"Task deleted: {task.id} for user {user_id}")

            return {
                "success": True,
                "data": {
                    "deleted": True
                }
            }
    except Exception as e:
        logger.error(f"Error deleting task: {e}", exc_info=True)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to delete task"
            }
        }
