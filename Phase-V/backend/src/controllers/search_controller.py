"""Search Controller for advanced task search, filter, and sort functionality."""
from typing import List
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..schemas.search import SearchRequest, SearchResponse
from ..services.search_service import SearchService
from ..services.event_service import EventService


class SearchController:
    """Controller class for advanced task search, filtering, and sorting."""

    def __init__(
        self,
        search_service: SearchService,
        event_service: EventService
    ):
        self.search_service = search_service
        self.event_service = event_service

    async def search_tasks(
        self,
        user_id: UUID,
        search_request: SearchRequest,
        session: Session
    ) -> SearchResponse:
        """Search tasks with filters, sorting, and pagination."""
        try:
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(search_request.page - 1) * search_request.page_size,
                limit=search_request.page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                # Get associated tags for each task
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + search_request.page_size - 1) // search_request.page_size if total > 0 else 1
            
            # Create the response
            response = SearchResponse(
                items=items,
                total=total,
                page=search_request.page,
                page_size=search_request.page_size,
                total_pages=total_pages
            )
            
            # Log the search event
            await self.event_service.log_task_searched(
                user_id=user_id,
                search_params=search_request.dict(),
                results_count=len(items)
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Search failed: {str(e)}"
            )

    async def get_filtered_tasks(
        self,
        user_id: UUID,
        priority: List[str] = None,
        tags: List[str] = None,
        due_after: datetime = None,
        due_before: datetime = None,
        completed: bool = None,
        title_contains: str = None,
        description_contains: str = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
        session: Session = Depends(get_session)
    ) -> SearchResponse:
        """Get tasks with filters, sorting, and pagination."""
        try:
            # Build search request from parameters
            search_request = SearchRequest(
                filters=SearchFilters(
                    priority=priority,
                    tags=tags,
                    due_after=due_after,
                    due_before=due_before,
                    completed=completed,
                    title_contains=title_contains,
                    description_contains=description_contains
                ),
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                page_size=page_size
            )
            
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                # Get associated tags for each task
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            # Create the response
            response = SearchResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            # Log the filter event
            await self.event_service.log_task_filtered(
                user_id=user_id,
                filter_params={
                    "priority": priority,
                    "tags": tags,
                    "due_after": due_after,
                    "due_before": due_before,
                    "completed": completed,
                    "title_contains": title_contains,
                    "description_contains": description_contains
                },
                results_count=len(items)
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filter failed: {str(e)}"
            )

    async def get_sorted_tasks(
        self,
        user_id: UUID,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
        session: Session = Depends(get_session)
    ) -> SearchResponse:
        """Get tasks sorted by specified field."""
        try:
            # Validate sort parameters
            valid_sort_fields = ["created_at", "due_date", "priority", "title", "updated_at"]
            if sort_by not in valid_sort_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sort field. Valid fields: {valid_sort_fields}"
                )
            
            if sort_order not in ["asc", "desc"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sort order. Valid values: asc, desc"
                )
            
            # Build search request for sorting
            search_request = SearchRequest(
                filters=SearchFilters(),
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                page_size=page_size
            )
            
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                # Get associated tags for each task
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            # Create the response
            response = SearchResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            # Log the sort event
            await self.event_service.log_task_sorted(
                user_id=user_id,
                sort_params={
                    "sort_by": sort_by,
                    "sort_order": sort_order
                },
                results_count=len(items)
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sort failed: {str(e)}"
            )

    async def get_tasks_by_tag(
        self,
        user_id: UUID,
        tag_name: str,
        page: int = 1,
        page_size: int = 20,
        session: Session = Depends(get_session)
    ) -> SearchResponse:
        """Get all tasks associated with a specific tag."""
        try:
            # Find the tag for the user
            tag = self.tag_service.get_tag_by_name(user_id, tag_name)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tag '{tag_name}' not found for user {user_id}"
                )
            
            # Build search request for tag-based search
            search_request = SearchRequest(
                filters=SearchFilters(
                    tags=[tag_name]
                ),
                sort_by="created_at",
                sort_order="desc",
                page=page,
                page_size=page_size
            )
            
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                # Get all tags for each task
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            # Create the response
            response = SearchResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            # Log the tag-based search event
            await self.event_service.log_tasks_searched_by_tag(
                user_id=user_id,
                tag_id=tag.id,
                tag_name=tag_name,
                results_count=len(items)
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag search failed: {str(e)}"
            )

    async def get_overdue_tasks(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        session: Session = Depends(get_session)
    ) -> SearchResponse:
        """Get all overdue tasks for a user."""
        try:
            # Build search request for overdue tasks
            search_request = SearchRequest(
                filters=SearchFilters(
                    due_before=datetime.utcnow(),
                    completed=False
                ),
                sort_by="due_date",
                sort_order="asc",  # Sort by oldest overdue first
                page=page,
                page_size=page_size
            )
            
            # Perform the search
            results, total = self.search_service.search_tasks(
                user_id=user_id,
                search_request=search_request,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # Convert to response models
            items = []
            for task in results:
                # Get associated tags for each task
                tags = self.tag_service.get_task_tags(task.id, user_id)
                tag_names = [tag.name for tag in tags]
                
                items.append(TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    parent_template_id=task.parent_template_id,
                    tags=tag_names,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                ))
            
            # Calculate pagination details
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            # Create the response
            response = SearchResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
            # Log the overdue tasks event
            await self.event_service.log_overdue_tasks_retrieved(
                user_id=user_id,
                results_count=len(items)
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Overdue tasks retrieval failed: {str(e)}"
            )


def get_search_controller(
    search_service: SearchService = Depends(),
    event_service: EventService = Depends()
) -> SearchController:
    """Get a SearchController instance with dependencies."""
    return SearchController(
        search_service=search_service,
        event_service=event_service
    )