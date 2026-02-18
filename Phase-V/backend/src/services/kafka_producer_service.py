"""Kafka Producer Service for publishing task-related events."""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from uuid import UUID
from pydantic import BaseModel
import time
from ..config import settings


logger = logging.getLogger(__name__)


class TaskEventPayload(BaseModel):
    """Payload for task events."""
    event_id: str
    event_type: str
    user_id: str
    task_id: Optional[str] = None
    timestamp: float
    data: Dict[str, Any]


class KafkaProducerService:
    """Kafka producer service for task-related events."""

    def __init__(self, bootstrap_servers: str = settings.kafka_bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_connected = False

    async def connect(self):
        """Connect to Kafka broker."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self.producer.start()
            self.is_connected = True
            logger.info("Connected to Kafka broker")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from Kafka broker."""
        if self.producer:
            await self.producer.stop()
            self.is_connected = False
            logger.info("Disconnected from Kafka broker")

    async def send_task_event(
        self,
        topic: str,
        event_type: str,
        user_id: str,
        task_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send a task-related event to Kafka."""
        if not self.is_connected or not self.producer:
            raise RuntimeError("Kafka producer is not connected")

        event_payload = TaskEventPayload(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            task_id=task_id,
            timestamp=time.time(),
            data=data or {}
        )

        try:
            await self.producer.send_and_wait(
                topic,
                value=event_payload.dict(),
                key=user_id  # Partition by user_id to ensure ordering for same user
            )
            logger.info(f"Sent {event_type} event to topic {topic} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send {event_type} event to topic {topic}: {str(e)}")
            raise

    async def send_task_created_event(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]):
        """Send a task created event."""
        await self.send_task_event(
            topic="task-events",
            event_type="task.created",
            user_id=str(user_id),
            task_id=str(task_id),
            data=task_data
        )

    async def send_task_updated_event(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]):
        """Send a task updated event."""
        await self.send_task_event(
            topic="task-events",
            event_type="task.updated",
            user_id=str(user_id),
            task_id=str(task_id),
            data=task_data
        )

    async def send_task_completed_event(self, user_id: UUID, task_id: UUID, task_data: Dict[str, Any]):
        """Send a task completed event."""
        await self.send_task_event(
            topic="task-events",
            event_type="task.completed",
            user_id=str(user_id),
            task_id=str(task_id),
            data=task_data
        )

    async def send_reminder_scheduled_event(self, user_id: UUID, task_id: UUID, reminder_data: Dict[str, Any]):
        """Send a reminder scheduled event."""
        await self.send_task_event(
            topic="reminder-events",
            event_type="reminder.scheduled",
            user_id=str(user_id),
            task_id=str(task_id),
            data=reminder_data
        )

    async def send_recurring_task_generated_event(self, user_id: UUID, task_id: UUID, template_id: UUID):
        """Send a recurring task generated event."""
        await self.send_task_event(
            topic="recurring-task-events",
            event_type="recurring_task.generated",
            user_id=str(user_id),
            task_id=str(task_id),
            data={"template_id": str(template_id)}
        )


# Global event producer instance
kafka_producer_service = KafkaProducerService()


async def get_kafka_producer_service() -> KafkaProducerService:
    """Get the global Kafka producer service instance."""
    if not kafka_producer_service.is_connected:
        await kafka_producer_service.connect()
    return kafka_producer_service