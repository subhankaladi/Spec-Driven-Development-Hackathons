"""Event Log Controller for managing task event logs."""
from typing import List
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.event_log import TaskEventLog
from ..schemas.event_log import EventLogResponse, EventLogListResponse
from ..services.event_service import EventService


class EventLogController:
    """Controller class for managing task event logs."""

    def __init__(self, event_service: EventService):
        self.event_service = event_service

    async def get_user_event_logs(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        event_type: str = None,
        task_instance_id: UUID = None,
        after: datetime = None,
        before: datetime = None,
        processed_by_kafka: bool = None,
        session: Session = Depends(get_session)
    ) -> EventLogListResponse:
        """Get event logs for a user with optional filters."""
        try:
            # Get event logs with filters
            event_logs, total = self.event_service.get_user_event_logs(
                user_id=user_id,
                skip=skip,
                limit=limit,
                event_type=event_type,
                task_instance_id=task_instance_id,
                after=after,
                before=before,
                processed_by_kafka=processed_by_kafka
            )
            
            # Convert to response models
            items = []
            for event_log in event_logs:
                items.append(EventLogResponse(
                    id=event_log.id,
                    user_id=event_log.user_id,
                    task_instance_id=event_log.task_instance_id,
                    event_type=event_log.event_type,
                    payload=event_log.payload,
                    processed_by_kafka=event_log.processed_by_kafka,
                    created_at=event_log.created_at
                ))
            
            # Calculate pagination details
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            current_page = (skip // limit) + 1
            
            return EventLogListResponse(
                items=items,
                total=total,
                page=current_page,
                page_size=limit,
                total_pages=total_pages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve event logs: {str(e)}"
            )

    async def get_task_event_logs(
        self,
        task_instance_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ) -> EventLogListResponse:
        """Get all event logs for a specific task."""
        try:
            # Verify that the task belongs to the user
            task = self.task_service.get_task(task_instance_id, user_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )
            
            # Get event logs for the task
            event_logs, total = self.event_service.get_task_event_logs(
                task_instance_id=task_instance_id,
                skip=skip,
                limit=limit
            )
            
            # Convert to response models
            items = []
            for event_log in event_logs:
                items.append(EventLogResponse(
                    id=event_log.id,
                    user_id=event_log.user_id,
                    task_instance_id=event_log.task_instance_id,
                    event_type=event_log.event_type,
                    payload=event_log.payload,
                    processed_by_kafka=event_log.processed_by_kafka,
                    created_at=event_log.created_at
                ))
            
            # Calculate pagination details
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            current_page = (skip // limit) + 1
            
            return EventLogListResponse(
                items=items,
                total=total,
                page=current_page,
                page_size=limit,
                total_pages=total_pages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve task event logs: {str(e)}"
            )

    async def get_unprocessed_events(
        self,
        session: Session = Depends(get_session)
    ) -> EventLogListResponse:
        """Get all unprocessed events (for Kafka processing)."""
        try:
            # Get unprocessed events
            event_logs, total = self.event_service.get_unprocessed_events()
            
            # Convert to response models
            items = []
            for event_log in event_logs:
                items.append(EventLogResponse(
                    id=event_log.id,
                    user_id=event_log.user_id,
                    task_instance_id=event_log.task_instance_id,
                    event_type=event_log.event_type,
                    payload=event_log.payload,
                    processed_by_kafka=event_log.processed_by_kafka,
                    created_at=event_log.created_at
                ))
            
            # Calculate pagination details (assuming default limit of 100)
            limit = 100
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
            return EventLogListResponse(
                items=items,
                total=total,
                page=1,
                page_size=limit,
                total_pages=total_pages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve unprocessed events: {str(e)}"
            )

    async def mark_event_as_processed(
        self,
        event_id: UUID,
        session: Session
    ) -> EventLogResponse:
        """Mark an event as processed by Kafka."""
        try:
            # Get the event to verify it exists
            event_log = self.event_service.get_event_log(event_id)
            if not event_log:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event log not found"
                )
            
            # Mark as processed
            updated_event = self.event_service.mark_event_as_processed(event_id)
            
            if not updated_event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Failed to update event log"
                )
            
            # Convert to response model
            return EventLogResponse(
                id=updated_event.id,
                user_id=updated_event.user_id,
                task_instance_id=updated_event.task_instance_id,
                event_type=updated_event.event_type,
                payload=updated_event.payload,
                processed_by_kafka=updated_event.processed_by_kafka,
                created_at=updated_event.created_at
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark event as processed: {str(e)}"
            )

    async def get_event_stats(
        self,
        user_id: UUID,
        session: Session = Depends(get_session)
    ) -> dict:
        """Get statistics about user's event logs."""
        try:
            stats = self.event_service.get_user_event_stats(user_id)
            
            return {
                "total_events": stats["total_events"],
                "processed_events": stats["processed_events"],
                "unprocessed_events": stats["unprocessed_events"],
                "event_types": stats["event_types"],
                "last_event_timestamp": stats["last_event_timestamp"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve event statistics: {str(e)}"
            )

    async def get_events_by_type(
        self,
        user_id: UUID,
        event_type: str,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ) -> EventLogListResponse:
        """Get event logs filtered by event type."""
        try:
            # Get event logs filtered by type
            event_logs, total = self.event_service.get_events_by_type(
                user_id=user_id,
                event_type=event_type,
                skip=skip,
                limit=limit
            )
            
            # Convert to response models
            items = []
            for event_log in event_logs:
                items.append(EventLogResponse(
                    id=event_log.id,
                    user_id=event_log.user_id,
                    task_instance_id=event_log.task_instance_id,
                    event_type=event_log.event_type,
                    payload=event_log.payload,
                    processed_by_kafka=event_log.processed_by_kafka,
                    created_at=event_log.created_at
                ))
            
            # Calculate pagination details
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            current_page = (skip // limit) + 1
            
            return EventLogListResponse(
                items=items,
                total=total,
                page=current_page,
                page_size=limit,
                total_pages=total_pages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve events by type: {str(e)}"
            )


def get_event_log_controller(
    event_service: EventService = Depends()
) -> EventLogController:
    """Get an EventLogController instance with dependencies."""
    return EventLogController(event_service=event_service)