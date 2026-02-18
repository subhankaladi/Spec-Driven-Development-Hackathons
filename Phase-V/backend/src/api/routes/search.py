"""Search API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from typing import List
from ...models.database import get_session
from ...models.task import Task
from ...services.search_service import get_search_service, SearchService
from ...api.schemas.search import (
    SearchRequest,
    SearchResponse
)
from ...api.dependencies import get_current_user
from ...models.user import User
from ...api.schemas.task import TaskResponse


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/tasks", response_model=SearchResponse)
async def search_tasks(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Search tasks with filters, sorting, and pagination."""
    service = get_search_service(session)
    try:
        results, total = service.search_tasks(
            user_id=current_user.id,
            search_request=search_request,
            skip=skip,
            limit=limit
        )
        
        # Convert SQLModel objects to Pydantic response models
        items = []
        for task in results:
            items.append(TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                due_date=task.due_date,
                priority=task.priority,
                parent_template_id=task.parent_template_id,
                tags=[],  # In a real implementation, you'd fetch associated tags
                created_at=task.created_at,
                updated_at=task.updated_at
            ))
        
        # Calculate pagination details
        page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        return SearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")