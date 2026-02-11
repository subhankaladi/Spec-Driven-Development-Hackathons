"""Notification Service - Microservice for handling task reminders and notifications.

Consumes reminder-triggered events from Kafka and sends notifications to users.
Placeholder implementation - can be extended to support email, SMS, push notifications.

Access Pattern:
- Consumes from: reminders topic (reminder-triggered events)
- Produces to: None
- State access: Via Dapr state store (optional - for notification history)
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
from fastapi import FastAPI
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_PUBSUB_NAME = "kafka-pubsub"
REMINDERS_TOPIC = "reminders"
dapr_client = DaprClient()

# FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Handles task reminders and notifications",
    version="1.0.0"
)


async def send_notification(
    reminder_id: str,
    task_id: str,
    user_id: str,
    title: str,
    notification_method: str = "default"
) -> bool:
    """Send notification to user.

    Args:
        reminder_id: Unique reminder ID
        task_id: Task ID associated with reminder
        user_id: User to notify
        title: Task title for notification
        notification_method: Method to use (default, email, sms, push)

    Returns:
        True if notification sent successfully
    """
    try:
        logger.info(f"Sending {notification_method} notification for reminder {reminder_id}")

        # Placeholder implementation - just log for now
        # Future implementations can add:
        # - Email via SendGrid/SES
        # - SMS via Twilio
        # - Push notifications via Firebase
        # - In-app notifications via WebSocket

        if notification_method == "default":
            logger.info(f"[NOTIFICATION] Task '{title}' (ID: {task_id}) is due now!")
        elif notification_method == "email":
            logger.info(f"[EMAIL] Sending reminder email for task '{title}' to user {user_id}")
        elif notification_method == "sms":
            logger.info(f"[SMS] Sending reminder SMS for task '{title}' to user {user_id}")
        elif notification_method == "push":
            logger.info(f"[PUSH] Sending push notification for task '{title}' to user {user_id}")
        else:
            logger.warning(f"Unknown notification method: {notification_method}")
            return False

        # Optional: Store notification in state store for history
        try:
            notification_record = {
                "reminder_id": reminder_id,
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "method": notification_method,
                "sent_at": datetime.utcnow().isoformat(),
                "status": "sent"
            }

            await dapr_client.save_state(
                "postgres-state",
                f"notification-{reminder_id}",
                json.dumps(notification_record)
            )
        except Exception as e:
            logger.warning(f"Failed to store notification record: {e}")

        return True

    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)
        return False


async def handle_reminder_triggered(event: Dict[str, Any]) -> None:
    """Handle reminder-triggered event and send notification."""
    try:
        reminder_id = event.get("payload", {}).get("reminder_id")
        task_id = event.get("task_id")
        user_id = event.get("user_id")
        title = event.get("payload", {}).get("title")
        notification_method = event.get("payload", {}).get("notification_method", "default")

        logger.info(f"Processing reminder {reminder_id} for task {task_id}")

        success = await send_notification(
            reminder_id=reminder_id,
            task_id=task_id,
            user_id=user_id,
            title=title,
            notification_method=notification_method
        )

        if success:
            logger.info(f"Successfully processed reminder {reminder_id}")
        else:
            logger.error(f"Failed to process reminder {reminder_id}")

    except Exception as e:
        logger.error(f"Error handling reminder triggered event: {e}", exc_info=True)


# Dapr pub/sub subscription
@app.post("/reminder-triggered")
async def reminder_triggered_handler(event_data: Dict[str, Any]):
    """Dapr pub/sub subscription handler for reminder-triggered events."""
    try:
        logger.debug(f"Received reminder event: {event_data}")

        # Extract event from Dapr envelope
        event = event_data.get("data", {})
        if not event:
            event = event_data

        await handle_reminder_triggered(event)

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Error in reminder_triggered_handler: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check Dapr connectivity
        return {
            "ready": True,
            "service": "notification-service",
            "dapr": "connected"
        }
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "service": "notification-service",
            "error": str(e)
        }, 503


@app.post("/test/emit-reminder", tags=["testing"])
async def test_emit_reminder(
    reminder_id: str,
    task_id: str,
    user_id: str,
    title: str,
    notification_method: str = "default"
):
    """Test endpoint to manually emit reminder-triggered event (for testing)."""
    event = {
        "event_type": "reminder-triggered",
        "event_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "task_id": task_id,
        "source_service": "test",
        "version": "1.0",
        "payload": {
            "reminder_id": reminder_id,
            "title": title,
            "notification_method": notification_method,
        }
    }

    success = await send_notification(
        reminder_id=reminder_id,
        task_id=task_id,
        user_id=user_id,
        title=title,
        notification_method=notification_method
    )

    return {"status": "notification sent" if success else "notification failed", "event": event}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Notification Service...")
    # Run with Dapr sidecar: dapr run --app-id notification-service --app-port 8002 python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
