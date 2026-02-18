"""Event Log API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.user import User
from ..schemas.event_log import EventLogListResponse
from ..controllers.event_log_controller import get_event_log_controller, EventLogController
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/event-logs", tags=["event-logs"])


@router.get("/", response_model=EventLogListResponse)
async def get_user_event_logs(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    event_type: str = Query(None, description="Filter by event type"),
    task_instance_id: UUID = Query(None, description="Filter by specific task instance"),
    after: datetime = Query(None, description="Filter events after this date"),
    before: datetime = Query(None, description="Filter events before this date"),
    processed_by_kafka: bool = Query(None, description="Filter by Kafka processing status"),
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Get event logs for the user with optional filters."""
    return await controller.get_user_event_logs(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        event_type=event_type,
        task_instance_id=task_instance_id,
        after=after,
        before=before,
        processed_by_kafka=processed_by_kafka,
        session=session
    )


@router.get("/tasks/{task_instance_id}", response_model=EventLogListResponse)
async def get_task_event_logs(
    task_instance_id: UUID,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Get all event logs for a specific task."""
    return await controller.get_task_event_logs(
        task_instance_id=task_instance_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        session=session
    )


@router.get("/unprocessed", response_model=EventLogListResponse)
async def get_unprocessed_events(
    current_user: User = Depends(get_current_user),  # This might require admin privileges in production
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Get all unprocessed events (for Kafka processing)."""
    return await controller.get_unprocessed_events(
        session=session
    )


@router.patch("/{event_id}/mark-processed", status_code=status.HTTP_204_NO_CONTENT)
async def mark_event_as_processed(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Mark an event as processed by Kafka."""
    # In a real implementation, you might want to restrict this to admin users
    # For now, we'll allow it for any authenticated user
    await controller.mark_event_as_processed(
        event_id=event_id,
        session=session
    )
    return


@router.get("/stats", response_model=dict)
async def get_event_stats(
    current_user: User = Depends(get_current_user),
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Get event statistics for the user."""
    return await controller.get_event_stats(
        user_id=current_user.id,
        session=session
    )


@router.get("/by-type/{event_type}", response_model=EventLogListResponse)
async def get_events_by_type(
    event_type: str,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: EventLogController = Depends(get_event_log_controller),
    session: Session = Depends(get_session)
):
    """Get events filtered by event type."""
    return await controller.get_events_by_type(
        user_id=current_user.id,
        event_type=event_type,
        skip=skip,
        limit=limit,
        session=session
    )