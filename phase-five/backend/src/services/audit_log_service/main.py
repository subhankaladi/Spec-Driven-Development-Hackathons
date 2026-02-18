"""Audit Log Service - Microservice for maintaining comprehensive audit trail.

Consumes all task events from Kafka and records them in audit log table.
Provides complete history of all task changes for compliance and debugging.

Access Pattern:
- Consumes from: task-events topic (all task lifecycle events)
- Produces to: None
- State access: Direct database write (audit log table)
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from fastapi import FastAPI
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager
import os

# Import models
import sys
sys.path.insert(0, '/app/src')
from models.audit_log import AuditLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://todouser:todopass@postgres:5432/tododb"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

def get_session():
    """Get database session."""
    with Session(engine) as session:
        return session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Audit Log Service...")
    yield
    logger.info("Shutting down Audit Log Service...")


# FastAPI app
app = FastAPI(
    title="Audit Log Service",
    description="Maintains audit trail of all task changes",
    version="1.0.0",
    lifespan=lifespan
)


async def record_audit_log(
    user_id: UUID,
    action: str,
    task_id: UUID,
    change_data: Optional[Dict[str, Any]] = None,
    service_name: str = "audit-log-service"
) -> bool:
    """Record event in audit log table.

    Args:
        user_id: User who performed the action
        action: Action type (created, updated, deleted, completed)
        task_id: Task ID affected
        change_data: Details of what changed
        service_name: Service recording the event

    Returns:
        True if recorded successfully
    """
    try:
        session = get_session()

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            task_id=task_id,
            change_data=change_data,
            timestamp=datetime.utcnow(),
            service_name=service_name,
        )

        session.add(audit_log)
        session.commit()
        session.close()

        logger.info(f"Recorded audit log: user={user_id}, action={action}, task={task_id}")
        return True

    except Exception as e:
        logger.error(f"Error recording audit log: {e}", exc_info=True)
        return False


async def handle_task_created(event: Dict[str, Any]) -> None:
    """Handle task-created event."""
    try:
        task_id = UUID(event.get("task_id"))
        user_id = UUID(event.get("user_id"))
        payload = event.get("payload", {})

        change_data = {
            "title": payload.get("title"),
            "description": payload.get("description"),
            "priority": payload.get("priority"),
            "tags": payload.get("tags"),
            "due_at": payload.get("due_at"),
            "remind_at": payload.get("remind_at"),
            "recurrence_rule": payload.get("recurrence_rule"),
        }

        await record_audit_log(
            user_id=user_id,
            action="created",
            task_id=task_id,
            change_data=change_data,
        )

    except Exception as e:
        logger.error(f"Error handling task-created event: {e}", exc_info=True)


async def handle_task_updated(event: Dict[str, Any]) -> None:
    """Handle task-updated event."""
    try:
        task_id = UUID(event.get("task_id"))
        user_id = UUID(event.get("user_id"))
        payload = event.get("payload", {})

        change_data = {
            "previous_values": payload.get("previous_values"),
            "updated_values": payload.get("updated_values"),
        }

        await record_audit_log(
            user_id=user_id,
            action="updated",
            task_id=task_id,
            change_data=change_data,
        )

    except Exception as e:
        logger.error(f"Error handling task-updated event: {e}", exc_info=True)


async def handle_task_completed(event: Dict[str, Any]) -> None:
    """Handle task-completed event."""
    try:
        task_id = UUID(event.get("task_id"))
        user_id = UUID(event.get("user_id"))

        change_data = {
            "completed_at": event.get("payload", {}).get("completed_at"),
            "has_recurrence": bool(event.get("payload", {}).get("recurrence_rule")),
        }

        await record_audit_log(
            user_id=user_id,
            action="completed",
            task_id=task_id,
            change_data=change_data,
        )

    except Exception as e:
        logger.error(f"Error handling task-completed event: {e}", exc_info=True)


async def handle_task_deleted(event: Dict[str, Any]) -> None:
    """Handle task-deleted event."""
    try:
        task_id = UUID(event.get("task_id"))
        user_id = UUID(event.get("user_id"))

        change_data = {
            "title": event.get("payload", {}).get("title"),
            "reason": event.get("payload", {}).get("reason"),
        }

        await record_audit_log(
            user_id=user_id,
            action="deleted",
            task_id=task_id,
            change_data=change_data,
        )

    except Exception as e:
        logger.error(f"Error handling task-deleted event: {e}", exc_info=True)


async def handle_task_event(event: Dict[str, Any]) -> None:
    """Route task events to appropriate handler."""
    try:
        event_type = event.get("event_type")

        logger.debug(f"Processing event: {event_type}")

        if event_type == "task-created":
            await handle_task_created(event)
        elif event_type == "task-updated":
            await handle_task_updated(event)
        elif event_type == "task-completed":
            await handle_task_completed(event)
        elif event_type == "task-deleted":
            await handle_task_deleted(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")

    except Exception as e:
        logger.error(f"Error handling task event: {e}", exc_info=True)


@app.post("/task-events")
async def task_events_handler(event_data: Dict[str, Any]):
    """Dapr pub/sub subscription handler for task events."""
    try:
        # Extract event from Dapr envelope
        event = event_data.get("data", {})
        if not event:
            event = event_data

        await handle_task_event(event)

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Error in task_events_handler: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    try:
        session = get_session()
        session.close()
        return {"status": "healthy", "service": "audit-log-service", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        session = get_session()
        session.close()
        return {
            "ready": True,
            "service": "audit-log-service",
            "database": "connected"
        }
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "service": "audit-log-service",
            "error": str(e)
        }, 503


@app.get("/audit-logs/{user_id}", tags=["audit"])
async def get_audit_logs(user_id: str, limit: int = 100, offset: int = 0):
    """Retrieve audit logs for a user."""
    try:
        session = get_session()

        user_uuid = UUID(user_id)
        query = select(AuditLog).where(
            AuditLog.user_id == user_uuid
        ).order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)

        logs = session.exec(query).all()
        session.close()

        return {
            "user_id": user_id,
            "count": len(logs),
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "task_id": str(log.task_id),
                    "timestamp": log.timestamp.isoformat(),
                    "service_name": log.service_name,
                    "change_data": log.change_data,
                }
                for log in logs
            ]
        }

    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Audit Log Service...")
    # Run with Dapr sidecar: dapr run --app-id audit-log-service --app-port 8003 python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )
