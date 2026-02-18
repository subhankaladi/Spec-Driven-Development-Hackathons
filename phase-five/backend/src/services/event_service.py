"""Event publishing service for Dapr-based event streaming.

All inter-service communication happens via Kafka topics through Dapr Pub/Sub.
No direct service-to-service calls allowed.
"""
import logging
import json
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from dapr.clients import DaprClient
from dapr.ext.grpc import App

logger = logging.getLogger(__name__)

# Dapr component name for Kafka pub/sub
DAPR_PUBSUB_NAME = "kafka-pubsub"

# Kafka topics
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"
TASK_UPDATES_TOPIC = "task-updates"


class EventService:
    """Service for publishing events to Kafka via Dapr Pub/Sub."""

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        """Initialize event service with optional Dapr client."""
        self.dapr_client = dapr_client or DaprClient()

    async def publish_task_created(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str,
        description: Optional[str],
        due_at: Optional[datetime] = None,
        remind_at: Optional[datetime] = None,
        priority: str = "medium",
        tags: Optional[list] = None,
        recurrence_rule: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Publish task-created event."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "task-created",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "title": title,
                "description": description,
                "due_at": due_at.isoformat() if due_at else None,
                "remind_at": remind_at.isoformat() if remind_at else None,
                "priority": priority,
                "tags": tags or [],
                "recurrence_rule": recurrence_rule,
                "is_completed": False,
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_EVENTS_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published task-created event for task {task_id}")
        return idempotency_key

    async def publish_task_updated(
        self,
        task_id: UUID,
        user_id: UUID,
        previous_values: Dict[str, Any],
        updated_values: Dict[str, Any],
        all_fields: Dict[str, Any],
    ) -> str:
        """Publish task-updated event."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "task-updated",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "previous_values": previous_values,
                "updated_values": updated_values,
                "all_fields": all_fields,
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_EVENTS_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published task-updated event for task {task_id}")
        return idempotency_key

    async def publish_task_completed(
        self,
        task_id: UUID,
        user_id: UUID,
        recurrence_rule: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Publish task-completed event."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "task-completed",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "previous_is_completed": False,
                "is_completed": True,
                "completed_at": datetime.utcnow().isoformat(),
                "recurrence_rule": recurrence_rule,
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_EVENTS_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published task-completed event for task {task_id}")
        return idempotency_key

    async def publish_task_deleted(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str,
        reason: str = "user_deleted",
    ) -> str:
        """Publish task-deleted event."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "task-deleted",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "title": title,
                "reason": reason,
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_EVENTS_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published task-deleted event for task {task_id}")
        return idempotency_key

    async def publish_task_updates(
        self,
        task_id: UUID,
        user_id: UUID,
        operation: str,
        changed_fields: Optional[list] = None,
        updated_values: Optional[Dict[str, Any]] = None,
        full_task: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Publish real-time task-updates event for WebSocket sync."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "task-state-changed",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "operation": operation,  # create, update, delete
                "changed_fields": changed_fields or [],
                "updated_values": updated_values or {},
                "full_task": full_task or {},
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_UPDATES_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published task-updates event for task {task_id}")
        return idempotency_key

    async def publish_reminder_scheduled(
        self,
        reminder_id: UUID,
        task_id: UUID,
        user_id: UUID,
        remind_at: datetime,
        title: str,
        notification_method: str = "default",
    ) -> str:
        """Publish reminder-scheduled event."""
        idempotency_key = str(uuid4())

        event = {
            "event_type": "reminder-scheduled",
            "event_id": str(uuid4()),
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": str(task_id),
            "source_service": "core-todo-service",
            "version": "1.0",
            "payload": {
                "reminder_id": str(reminder_id),
                "remind_at": remind_at.isoformat(),
                "title": title,
                "notification_method": notification_method,
            }
        }

        await self.dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            REMINDERS_TOPIC,
            json.dumps(event)
        )

        logger.info(f"Published reminder-scheduled event for reminder {reminder_id}")
        return idempotency_key


# Global event service instance
event_service = EventService()
