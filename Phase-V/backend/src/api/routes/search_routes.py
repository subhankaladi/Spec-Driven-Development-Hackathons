"""Search API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.user import User
from ..schemas.search import SearchRequest, SearchResponse
from ..controllers.search_controller import get_search_controller, SearchController
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/tasks", response_model=SearchResponse)
async def search_tasks(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Search tasks with advanced filters, sorting, and pagination."""
    return await controller.search_tasks(
        user_id=current_user.id,
        search_request=search_request,
        session=session
    )


@router.get("/tasks", response_model=SearchResponse)
async def get_filtered_tasks(
    current_user: User = Depends(get_current_user),
    priority: List[str] = Query(None, description="Filter by priority levels"),
    tags: List[str] = Query(None, description="Filter by tag names"),
    due_after: datetime = Query(None, description="Filter tasks with due date after this date"),
    due_before: datetime = Query(None, description="Filter tasks with due date before this date"),
    completed: bool = Query(None, description="Filter by completion status"),
    title_contains: str = Query(None, description="Filter tasks with title containing this text"),
    description_contains: str = Query(None, description="Filter tasks with description containing this text"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Get tasks with filters, sorting, and pagination."""
    return await controller.get_filtered_tasks(
        user_id=current_user.id,
        priority=priority,
        tags=tags,
        due_after=due_after,
        due_before=due_before,
        completed=completed,
        title_contains=title_contains,
        description_contains=description_contains,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        session=session
    )


@router.get("/tasks/sorted", response_model=SearchResponse)
async def get_sorted_tasks(
    current_user: User = Depends(get_current_user),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Get tasks sorted by specified field."""
    return await controller.get_sorted_tasks(
        user_id=current_user.id,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        session=session
    )


@router.get("/tasks/by-tag/{tag_name}", response_model=SearchResponse)
async def get_tasks_by_tag(
    tag_name: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Get all tasks associated with a specific tag."""
    return await controller.get_tasks_by_tag(
        user_id=current_user.id,
        tag_name=tag_name,
        page=page,
        page_size=page_size,
        session=session
    )


@router.get("/tasks/overdue", response_model=SearchResponse)
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Get all overdue tasks for the user."""
    return await controller.get_overdue_tasks(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        session=session
    )


@router.get("/stats", response_model=dict)
async def get_search_stats(
    current_user: User = Depends(get_current_user),
    controller: SearchController = Depends(get_search_controller),
    session: Session = Depends(get_session)
):
    """Get search statistics for the user."""
    return await controller.get_search_stats(
        user_id=current_user.id,
        session=session
    )