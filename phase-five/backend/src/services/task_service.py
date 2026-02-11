"""Task service with direct database CRUD operations for agent tools.

All methods ensure user isolation by filtering/scoping queries to owner_id == user_id.
Returns standardized dict responses for agent consumption.
"""
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlmodel import select
from sqlalchemy import func, and_
from datetime import datetime

from src.models.task import Task

logger = logging.getLogger(__name__)

def task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert Task model to dict for API/agent responses."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }

class TaskService:
    @staticmethod
    def create_task(
        session: Session,
        user_id: UUID,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new task for the user."""
        if not title or not title.strip():
            raise ValueError("Title is required and cannot be empty")
        title = title.strip()
        if len(title) > 255:
            raise ValueError("Title must be 255 characters or less")

        task = Task(
            user_id=user_id,
            title=title,
            description=description,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Created task {task.id} for user {user_id}")
        return task_to_dict(task)

    @staticmethod
    def get_tasks(
        session: Session,
        user_id: UUID,
        completed: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get paginated tasks for the user with optional completed filter."""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        offset = (page - 1) * page_size

        # Build base query
        base_query = select(Task).where(Task.user_id == user_id)
        count_query = select(func.count(Task.id)).where(Task.user_id == user_id)

        if completed is not None:
            base_query = base_query.where(Task.is_completed == completed)
            count_query = count_query.where(Task.is_completed == completed)

        base_query = base_query.order_by(Task.created_at.desc())

        total = session.exec(count_query).one()
        tasks = session.exec(base_query.offset(offset).limit(page_size)).all()

        task_dicts = [task_to_dict(task) for task in tasks]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return {
            "success": True,
            "tasks": task_dicts,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    @staticmethod
    def _get_user_task(session: Session, user_id: UUID, task_id: UUID) -> Task:
        """Get single task ensuring user ownership. Raises ValueError if not found/unauthorized."""
        task = session.exec(
            select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
        ).first()
        if not task:
            raise ValueError(f"Task {task_id} not found or access denied.")
        return task

    @staticmethod
    def complete_task(
        session: Session,
        user_id: UUID,
        task_id: UUID
    ) -> Dict[str, Any]:
        """Mark task as completed."""
        task = TaskService._get_user_task(session, user_id, task_id)
        if task.is_completed:
            raise ValueError(f"Task {task_id} is already completed.")
        task.is_completed = True
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        logger.info(f"Completed task {task_id} for user {user_id}")
        return {
            "success": True,
            "task_id": str(task_id),
            "message": "Task marked as completed.",
            "task": task_to_dict(task)
        }

    @staticmethod
    def update_task(
        session: Session,
        user_id: UUID,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update task fields (partial update)."""
        task = TaskService._get_user_task(session, user_id, task_id)
        updated = False

        if title is not None:
            title_stripped = title.strip()
            if not title_stripped:
                raise ValueError("Title cannot be empty.")
            if len(title_stripped) > 255:
                raise ValueError("Title must be 255 characters or less.")
            task.title = title_stripped
            updated = True

        if description is not None:
            task.description = description
            updated = True

        if is_completed is not None:
            task.is_completed = is_completed
            updated = True

        if not updated:
            raise ValueError("No valid fields provided to update.")

        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        logger.info(f"Updated task {task_id} for user {user_id}")
        return task_to_dict(task)

    @staticmethod
    def delete_task(
        session: Session,
        user_id: UUID,
        task_id: UUID
    ) -> Dict[str, Any]:
        """Delete a task."""
        task = TaskService._get_user_task(session, user_id, task_id)
        task_id_str = str(task_id)
        session.delete(task)
        session.commit()
        logger.info(f"Deleted task {task_id_str} for user {user_id}")
        return {
            "success": True,
            "task_id": task_id_str,
            "message": "Task deleted successfully."
        }
