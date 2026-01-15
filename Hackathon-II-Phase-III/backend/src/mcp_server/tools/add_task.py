"""
Add task tool implementation.

Creates a new task for the authenticated user.
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
    Handle add_task tool call.

    Args:
        arguments: Tool arguments with title, description, and JWT token

    Returns:
        Response dict with success status and task data
    """
    # Extract arguments
    title = arguments.get("title", "").strip()
    description = arguments.get("description", "").strip() if arguments.get("description") else None
    token = arguments.get("_jwt_token")  # Token passed in context

    # Validate inputs
    if not title:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Title is required and cannot be empty"
            }
        }

    if len(title) > 255:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Title cannot exceed 255 characters"
            }
        }

    if description and len(description) > 2000:
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

    # Create task
    try:
        async with AsyncSession(async_engine) as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description if description else None,
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task created: {task.id} for user {user_id}")

            return {
                "success": True,
                "data": {
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed,
                        "created_at": task.created_at.isoformat()
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Failed to create task"
            }
        }
