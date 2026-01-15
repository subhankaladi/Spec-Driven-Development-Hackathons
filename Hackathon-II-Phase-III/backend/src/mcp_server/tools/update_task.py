"""
Update task tool implementation.

Updates the title or description of a task owned by the authenticated user.
"""

import logging
from datetime import datetime
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
    Handle update_task tool call.

    Args:
        arguments: Tool arguments with task_id, title, description, and JWT token

    Returns:
        Response dict with success status and updated task data
    """
    # Extract arguments
    task_id_str = arguments.get("task_id", "").strip()
    title = arguments.get("title", "").strip() if arguments.get("title") else None
    description = arguments.get("description", "").strip() if arguments.get("description") else None
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

    # Validate inputs
    if title is not None and len(title) > 255:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Title cannot exceed 255 characters"
            }
        }

    if description is not None and len(description) > 2000:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Description cannot exceed 2000 characters"
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

    # Update task
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

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description if description else None

            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task updated: {task.id} for user {user_id}")

            return {
                "success": True,
                "data": {
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed,
                        "updated_at": task.updated_at.isoformat()
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error updating task: {e}", exc_info=True)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to update task"
            }
        }
