"""Integration layer for Core Todo Service event publishing and Dapr communication.

This module integrates event publishing with task operations and handles
Dapr-based reminder scheduling.
"""
import logging
import asyncio
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel import Session

from src.models.task import Task
from src.services.event_service import event_service
from src.services.recurrence_service import RecurrenceService

logger = logging.getLogger(__name__)


class TaskEventsIntegration:
    """Integration between task operations and event publishing."""

    @staticmethod
    async def handle_task_created(
        task: Task,
        session: Session
    ) -> None:
        """Handle task creation and publish event.

        Args:
            task: Created task
            session: Database session
        """
        try:
            # Publish task-created event
            await event_service.publish_task_created(
                task_id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                due_at=task.due_at,
                remind_at=task.remind_at,
                priority=task.priority,
                tags=task.tags,
                recurrence_rule=task.recurrence_rule,
            )

            # Schedule reminder if remind_at is set
            if task.remind_at:
                await TaskEventsIntegration.schedule_reminder(
                    task_id=task.id,
                    user_id=task.user_id,
                    remind_at=task.remind_at,
                    title=task.title,
                    session=session,
                )

            # Publish real-time sync event
            await event_service.publish_task_updates(
                task_id=task.id,
                user_id=task.user_id,
                operation="create",
                full_task=TaskEventsIntegration._task_to_dict(task),
            )

            logger.info(f"Task {task.id} creation handled and events published")

        except Exception as e:
            logger.error(f"Error handling task creation: {e}", exc_info=True)
            # Don't re-raise - task was already created

    @staticmethod
    async def handle_task_updated(
        task: Task,
        previous_values: Dict[str, Any],
        changed_fields: list,
        session: Session
    ) -> None:
        """Handle task update and publish events.

        Args:
            task: Updated task
            previous_values: Previous field values
            changed_fields: List of changed field names
            session: Database session
        """
        try:
            # Get current values for changed fields
            updated_values = {
                field: getattr(task, field, None)
                for field in changed_fields
            }

            # Publish task-updated event
            await event_service.publish_task_updated(
                task_id=task.id,
                user_id=task.user_id,
                previous_values=previous_values,
                updated_values=updated_values,
                all_fields=TaskEventsIntegration._task_to_dict(task),
            )

            # Handle reminder changes
            if "remind_at" in changed_fields:
                if task.remind_at and task.remind_at != previous_values.get("remind_at"):
                    # Schedule new reminder
                    await TaskEventsIntegration.schedule_reminder(
                        task_id=task.id,
                        user_id=task.user_id,
                        remind_at=task.remind_at,
                        title=task.title,
                        session=session,
                    )
                elif not task.remind_at:
                    # Reminder removed - would need to cancel in Dapr Jobs
                    logger.info(f"Reminder removed for task {task.id}")

            # Publish real-time sync event
            await event_service.publish_task_updates(
                task_id=task.id,
                user_id=task.user_id,
                operation="update",
                changed_fields=changed_fields,
                updated_values=updated_values,
                full_task=TaskEventsIntegration._task_to_dict(task),
            )

            logger.info(f"Task {task.id} update handled and events published")

        except Exception as e:
            logger.error(f"Error handling task update: {e}", exc_info=True)

    @staticmethod
    async def handle_task_completed(
        task: Task,
        session: Session
    ) -> None:
        """Handle task completion and publish events.

        Args:
            task: Completed task
            session: Database session
        """
        try:
            # Get recurrence rule for next generation
            recurrence_rule = task.recurrence_rule

            # Publish task-completed event
            await event_service.publish_task_completed(
                task_id=task.id,
                user_id=task.user_id,
                recurrence_rule=recurrence_rule,
            )

            # Publish real-time sync event
            await event_service.publish_task_updates(
                task_id=task.id,
                user_id=task.user_id,
                operation="update",
                changed_fields=["is_completed"],
                updated_values={"is_completed": True},
                full_task=TaskEventsIntegration._task_to_dict(task),
            )

            logger.info(f"Task {task.id} completion handled and events published")

        except Exception as e:
            logger.error(f"Error handling task completion: {e}", exc_info=True)

    @staticmethod
    async def handle_task_deleted(
        task_id: UUID,
        user_id: UUID,
        title: str,
        session: Session
    ) -> None:
        """Handle task deletion and publish events.

        Args:
            task_id: Deleted task ID
            user_id: User who owns the task
            title: Task title
            session: Database session
        """
        try:
            # Publish task-deleted event
            await event_service.publish_task_deleted(
                task_id=task_id,
                user_id=user_id,
                title=title,
                reason="user_deleted",
            )

            logger.info(f"Task {task_id} deletion handled and events published")

        except Exception as e:
            logger.error(f"Error handling task deletion: {e}", exc_info=True)

    @staticmethod
    async def schedule_reminder(
        task_id: UUID,
        user_id: UUID,
        remind_at: datetime,
        title: str,
        session: Session,
    ) -> None:
        """Schedule a reminder for a task using Dapr Jobs API.

        Args:
            task_id: Task ID
            user_id: User ID
            remind_at: When to trigger reminder
            title: Task title
            session: Database session
        """
        try:
            from src.models.reminder import Reminder

            # Create reminder record
            reminder = Reminder(
                task_id=task_id,
                user_id=user_id,
                remind_at=remind_at,
                notification_method="default",
                status="scheduled",
            )

            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            # Publish reminder-scheduled event
            await event_service.publish_reminder_scheduled(
                reminder_id=reminder.id,
                task_id=task_id,
                user_id=user_id,
                remind_at=remind_at,
                title=title,
                notification_method="default",
            )

            # TODO: Schedule job via Dapr Jobs API
            # This would call Dapr to schedule a callback at remind_at time
            logger.info(f"Reminder {reminder.id} scheduled for task {task_id} at {remind_at}")

        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}", exc_info=True)

    @staticmethod
    def _task_to_dict(task: Task) -> Dict[str, Any]:
        """Convert task to dictionary for event publishing."""
        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "remind_at": task.remind_at.isoformat() if task.remind_at else None,
            "priority": task.priority,
            "tags": task.tags or [],
            "recurrence_rule": task.recurrence_rule,
            "next_occurrence_at": task.next_occurrence_at.isoformat() if task.next_occurrence_at else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
