"""Event Service for publishing task-related events to Kafka."""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from uuid import UUID
from ..models.event_log import TaskEventLog
from ..models.task import Task
from ..api.schemas.event import TaskEventCreate
from ..events.producers.task_producer import get_event_producer
import logging


logger = logging.getLogger(__name__)


class EventService:
    """Service class for managing task-related events and publishing to Kafka."""

    def __init__(self, session: Session):
        self.session = session

    async def log_and_publish_task_event(
        self,
        user_id: UUID,
        event_type: str,
        task_instance_id: Optional[UUID] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> TaskEventLog:
        """Log an event and publish it to Kafka."""
        # Create the event log entry
        event_log = TaskEventLog(
            user_id=user_id,
            task_instance_id=task_instance_id,
            event_type=event_type,
            payload=payload or {},
            processed_by_kafka=False  # Will be updated after Kafka processing
        )
        
        self.session.add(event_log)
        self.session.commit()
        self.session.refresh(event_log)
        
        # Publish to Kafka
        try:
            producer = await get_event_producer()
            
            # Determine the appropriate topic based on event type
            if event_type.startswith('reminder'):
                topic = 'reminder-events'
            elif event_type.startswith('recurring'):
                topic = 'recurring-task-events'
            else:
                topic = 'task-events'
            
            # Send the event to Kafka
            await producer.send_task_event(
                topic=topic,
                event_type=event_type,
                user_id=str(user_id),
                task_id=str(task_instance_id) if task_instance_id else None,
                data=payload or {}
            )
            
            # Update the event log to mark as processed
            event_log.processed_by_kafka = True
            self.session.add(event_log)
            self.session.commit()
            
            logger.info(f"Logged and published event {event_type} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type} to Kafka: {str(e)}")
            # Don't re-raise, as we still have the event in the database
        
        return event_log

    async def log_task_created(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]) -> TaskEventLog:
        """Log and publish a task created event."""
        return await self.log_and_publish_task_event(
            user_id=user_id,
            event_type="task.created",
            task_instance_id=task_id,
            payload=task_data
        )

    async def log_task_updated(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]) -> TaskEventLog:
        """Log and publish a task updated event."""
        return await self.log_and_publish_task_event(
            user_id=user_id,
            event_type="task.updated",
            task_instance_id=task_id,
            payload=task_data
        )

    async def log_task_completed(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]) -> TaskEventLog:
        """Log and publish a task completed event."""
        return await self.log_and_publish_task_event(
            user_id=user_id,
            event_type="task.completed",
            task_instance_id=task_id,
            payload=task_data
        )

    async def log_reminder_scheduled(self, user_id: UUID, task_id: UUID, reminder_data: Dict[str, Any]) -> TaskEventLog:
        """Log and publish a reminder scheduled event."""
        return await self.log_and_publish_task_event(
            user_id=user_id,
            event_type="reminder.scheduled",
            task_instance_id=task_id,
            payload=reminder_data
        )

    async def log_recurring_task_generated(self, user_id: UUID, task_id: UUID, template_id: UUID) -> TaskEventLog:
        """Log and publish a recurring task generated event."""
        return await self.log_and_publish_task_event(
            user_id=user_id,
            event_type="recurring_task.generated",
            task_instance_id=task_id,
            payload={"template_id": str(template_id)}
        )

    def get_user_events(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[TaskEventLog]:
        """Get all events for a user."""
        statement = select(TaskEventLog).where(
            TaskEventLog.user_id == user_id
        ).order_by(TaskEventLog.created_at.desc()).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def get_unprocessed_events(self) -> list[TaskEventLog]:
        """Get all events that haven't been processed by Kafka."""
        statement = select(TaskEventLog).where(
            TaskEventLog.processed_by_kafka == False
        ).order_by(TaskEventLog.created_at.asc())
        return self.session.exec(statement).all()

    def mark_event_as_processed(self, event_id: UUID) -> bool:
        """Mark an event as processed by Kafka."""
        event_log = self.session.get(TaskEventLog, event_id)
        if not event_log:
            return False
        
        event_log.processed_by_kafka = True
        self.session.add(event_log)
        self.session.commit()
        
        logger.info(f"Marked event {event_id} as processed")
        return True

    async def retry_failed_events(self) -> int:
        """Retry publishing events that failed to be sent to Kafka."""
        unprocessed_events = self.get_unprocessed_events()
        retry_count = 0
        
        for event in unprocessed_events:
            try:
                producer = await get_event_producer()
                
                # Determine the appropriate topic based on event type
                if event.event_type.startswith('reminder'):
                    topic = 'reminder-events'
                elif event.event_type.startswith('recurring'):
                    topic = 'recurring-task-events'
                else:
                    topic = 'task-events'
                
                # Retry sending the event to Kafka
                await producer.send_task_event(
                    topic=topic,
                    event_type=event.event_type,
                    user_id=str(event.user_id),
                    task_id=str(event.task_instance_id) if event.task_instance_id else None,
                    data=event.payload
                )
                
                # Mark as processed
                event.processed_by_kafka = True
                self.session.add(event)
                self.session.commit()
                
                retry_count += 1
                logger.info(f"Retried and published event {event.id}")
            except Exception as e:
                logger.error(f"Failed to retry event {event.id}: {str(e)}")
        
        logger.info(f"Retried {retry_count} failed events")
        return retry_count


async def get_event_service(session: Session) -> EventService:
    """Get an EventService instance with the given session."""
    return EventService(session)