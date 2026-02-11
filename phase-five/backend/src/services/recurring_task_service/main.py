"""Recurring Task Service - Microservice for generating recurring task occurrences.

Consumes task-completed events from Kafka and generates next recurring task occurrence
when a task with recurrence_rule is completed.

Access Pattern:
- Consumes from: task-events topic (task-completed events)
- Produces to: task-events topic (task-created events for next occurrence)
- State access: Via Dapr state store (no direct database access)
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dapr.clients import DaprClient
from dapr.ext.grpc import App
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_PUBSUB_NAME = "kafka-pubsub"
TASK_EVENTS_TOPIC = "task-events"
dapr_client = DaprClient()

# FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Generates next occurrence for recurring tasks",
    version="1.0.0"
)

# Dapr service app for subscriptions
dapr_app = App()


def calculate_next_occurrence(
    recurrence_rule: Dict[str, Any],
    completed_at: datetime = None
) -> Optional[datetime]:
    """Calculate next occurrence based on recurrence rule.

    Args:
        recurrence_rule: Dict with 'frequency' (daily/weekly/monthly) and optional 'end_date'
        completed_at: When the current task was completed

    Returns:
        Next occurrence datetime or None if recurrence ended
    """
    if not recurrence_rule or "frequency" not in recurrence_rule:
        return None

    completed_at = completed_at or datetime.utcnow()
    frequency = recurrence_rule.get("frequency", "daily")
    end_date_str = recurrence_rule.get("end_date")

    # Calculate next occurrence based on frequency
    if frequency == "daily":
        next_occurrence = completed_at + timedelta(days=1)
    elif frequency == "weekly":
        next_occurrence = completed_at + timedelta(weeks=1)
    elif frequency == "monthly":
        # Simple month increment (may need refinement for edge cases)
        month = completed_at.month + 1
        year = completed_at.year
        if month > 12:
            month = 1
            year += 1
        next_occurrence = completed_at.replace(month=month, year=year)
    else:
        logger.warning(f"Unknown recurrence frequency: {frequency}")
        return None

    # Check if next occurrence exceeds end date
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str)
            if next_occurrence > end_date:
                logger.info(f"Next occurrence {next_occurrence} exceeds end date {end_date}")
                return None
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing end_date: {e}")

    return next_occurrence


async def handle_task_completed(event: Dict[str, Any]) -> None:
    """Handle task-completed event and generate next recurring task if applicable."""
    try:
        task_id = event.get("task_id")
        user_id = event.get("user_id")
        recurrence_rule = event.get("payload", {}).get("recurrence_rule")

        if not recurrence_rule:
            logger.debug(f"Task {task_id} has no recurrence rule")
            return

        logger.info(f"Processing recurring task completion for {task_id}")

        # Query Dapr state store for task details
        try:
            task_state = await dapr_client.get_state("postgres-state", f"task-{task_id}")
            if not task_state or not task_state.data:
                logger.warning(f"Task {task_id} not found in state store")
                return

            task_data = json.loads(task_state.data)
        except Exception as e:
            logger.error(f"Error retrieving task from state store: {e}")
            return

        # Calculate next occurrence
        completed_at = datetime.fromisoformat(event.get("payload", {}).get("completed_at", datetime.utcnow().isoformat()))
        next_occurrence_at = calculate_next_occurrence(recurrence_rule, completed_at)

        if not next_occurrence_at:
            logger.info(f"No next occurrence for recurring task {task_id}")
            return

        # Generate new task ID for next occurrence
        new_task_id = str(uuid4())
        new_idempotency_key = str(uuid4())

        # Create task-created event for next occurrence
        new_event = {
            "event_type": "task-created",
            "event_id": str(uuid4()),
            "idempotency_key": new_idempotency_key,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "task_id": new_task_id,
            "source_service": "recurring-task-service",
            "version": "1.0",
            "payload": {
                "title": task_data.get("title"),
                "description": task_data.get("description"),
                "due_at": task_data.get("due_at"),
                "remind_at": task_data.get("remind_at"),
                "priority": task_data.get("priority", "medium"),
                "tags": task_data.get("tags", []),
                "recurrence_rule": recurrence_rule,
                "next_occurrence_at": next_occurrence_at.isoformat(),
                "is_completed": False,
            }
        }

        # Publish new task-created event
        await dapr_client.publish_event(
            DAPR_PUBSUB_NAME,
            TASK_EVENTS_TOPIC,
            json.dumps(new_event)
        )

        logger.info(f"Created next recurring task {new_task_id} with next occurrence at {next_occurrence_at}")

    except Exception as e:
        logger.error(f"Error processing task completion: {e}", exc_info=True)


@dapr_app.subscribe(pubsub_name=DAPR_PUBSUB_NAME, topic=TASK_EVENTS_TOPIC)
async def task_events_handler(event: Dict[str, Any]) -> None:
    """Dapr pub/sub subscription handler for task events."""
    try:
        event_type = event.get("event_type")

        if event_type == "task-completed":
            await handle_task_completed(event)
        else:
            logger.debug(f"Ignoring event type: {event_type}")

    except Exception as e:
        logger.error(f"Error in task_events_handler: {e}", exc_info=True)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check Dapr connectivity
        result = await dapr_client.invoke_method("recurring-task-service", "/health")
        return {
            "ready": True,
            "service": "recurring-task-service",
            "dapr": "connected"
        }
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "service": "recurring-task-service",
            "error": str(e)
        }, 503


@app.post("/test/emit-task-completed", tags=["testing"])
async def test_emit_task_completed(
    task_id: str,
    user_id: str,
    recurrence_rule: Optional[Dict[str, Any]] = None
):
    """Test endpoint to manually emit task-completed event (for testing)."""
    event = {
        "event_type": "task-completed",
        "event_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "task_id": task_id,
        "source_service": "test",
        "version": "1.0",
        "payload": {
            "previous_is_completed": False,
            "is_completed": True,
            "completed_at": datetime.utcnow().isoformat(),
            "recurrence_rule": recurrence_rule or {"frequency": "daily"},
        }
    }

    await dapr_client.publish_event(
        DAPR_PUBSUB_NAME,
        TASK_EVENTS_TOPIC,
        json.dumps(event)
    )

    return {"status": "event published", "event": event}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Recurring Task Service...")
    # Run with Dapr sidecar: dapr run --app-id recurring-task-service --app-port 8001 python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
