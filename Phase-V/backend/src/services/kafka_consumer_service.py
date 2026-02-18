"""Kafka Consumer Service for processing task-related events."""
import asyncio
import json
import logging
from typing import Dict, Callable, Any, Awaitable, Optional
from aiokafka import AIOKafkaConsumer
from uuid import UUID
from ..config import settings


logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Kafka consumer service for task-related events."""

    def __init__(self, bootstrap_servers: str = settings.kafka_bootstrap_servers, group_id: str = settings.kafka_consumer_group):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_connected = False
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}

    async def connect(self):
        """Connect to Kafka broker."""
        try:
            self.consumer = AIOKafkaConsumer(
                'task-events',
                'reminder-events',
                'recurring-task-events',  # Subscribe to all relevant topics
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')) if v else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            await self.consumer.start()
            self.is_connected = True
            logger.info("Connected to Kafka broker as consumer")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka as consumer: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from Kafka broker."""
        if self.consumer:
            await self.consumer.stop()
            self.is_connected = False
            logger.info("Disconnected from Kafka broker as consumer")

    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register a handler for a specific event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    async def start_consuming(self):
        """Start consuming events from Kafka."""
        if not self.is_connected or not self.consumer:
            raise RuntimeError("Kafka consumer is not connected")

        try:
            async for msg in self.consumer:
                try:
                    # Parse the event payload
                    event_payload = msg.value
                    
                    # Get the appropriate handler for the event type
                    event_type = event_payload.get('event_type')
                    if not event_type:
                        logger.error(f"Event missing event_type: {event_payload}")
                        continue
                    
                    handler = self.handlers.get(event_type)
                    
                    if handler:
                        # Process the event
                        await handler(event_payload)
                        logger.info(f"Processed {event_type} event: {event_payload.get('event_id')}")
                    else:
                        logger.warning(f"No handler found for event type: {event_type}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # In a real implementation, we might want to send to a dead letter queue
                    # or implement retry logic here
        except Exception as e:
            logger.error(f"Error consuming events: {str(e)}")
            raise


# Global event consumer instance
kafka_consumer_service = KafkaConsumerService()


async def get_kafka_consumer_service() -> KafkaConsumerService:
    """Get the global Kafka consumer service instance."""
    if not kafka_consumer_service.is_connected:
        await kafka_consumer_service.connect()
    return kafka_consumer_service


# Example handlers for different event types
async def handle_task_created(data: Dict[str, Any]):
    """Handle task created event."""
    logger.info(f"Handling task created event for user {data['user_id']}, task {data['task_id']}")
    # In a real implementation, this might trigger notifications, analytics, etc.


async def handle_task_updated(data: Dict[str, Any]):
    """Handle task updated event."""
    logger.info(f"Handling task updated event for user {data['user_id']}, task {data['task_id']}")
    # In a real implementation, this might trigger notifications, analytics, etc.


async def handle_task_completed(data: Dict[str, Any]):
    """Handle task completed event."""
    logger.info(f"Handling task completed event for user {data['user_id']}, task {data['task_id']}")
    # In a real implementation, this might trigger notifications, analytics, etc.


async def handle_reminder_scheduled(data: Dict[str, Any]):
    """Handle reminder scheduled event."""
    logger.info(f"Handling reminder scheduled event for user {data['user_id']}, task {data['task_id']}")
    # In a real implementation, this might trigger the reminder scheduler


async def handle_recurring_task_generated(data: Dict[str, Any]):
    """Handle recurring task generated event."""
    logger.info(f"Handling recurring task generated event for user {data['user_id']}, task {data['task_id']}")
    # In a real implementation, this might trigger notifications or other actions


# Register the default handlers
async def register_default_handlers(consumer_service: KafkaConsumerService):
    """Register default event handlers."""
    consumer_service.register_handler("task.created", handle_task_created)
    consumer_service.register_handler("task.updated", handle_task_updated)
    consumer_service.register_handler("task.completed", handle_task_completed)
    consumer_service.register_handler("reminder.scheduled", handle_reminder_scheduled)
    consumer_service.register_handler("recurring_task.generated", handle_recurring_task_generated)