"""Search Service for advanced task search, filter, and sort functionality."""
from datetime import datetime
from typing import List, Tuple, Optional
from sqlmodel import Session, select, func, and_, or_
from uuid import UUID
from ..models.task import Task
from ..models.tag import Tag
from ..models.task_tag import TaskTag
from ..api.schemas.search import SearchRequest
from sqlalchemy.sql.elements import BinaryExpression


class SearchService:
    """Service class for advanced task search, filtering, and sorting."""

    def __init__(self, session: Session):
        self.session = session

    def search_tasks(
        self, 
        user_id: UUID, 
        search_request: SearchRequest,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Task], int]:
        """Search tasks with filters, sorting, and pagination."""
        # Build the base query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply filters if provided
        if search_request.filters:
            query = self._apply_filters(query, search_request.filters)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()
        
        # Apply sorting
        query = self._apply_sorting(query, search_request.sort_by, search_request.sort_order)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute the query
        results = self.session.exec(query).all()
        
        return results, total

    def _apply_filters(self, query, filters):
        """Apply filters to the query."""
        if filters.title:
            query = query.where(Task.title.ilike(f"%{filters.title}%"))
        
        if filters.priority:
            query = query.where(Task.priority.in_(filters.priority))
        
        if filters.due_after:
            query = query.where(Task.due_date >= filters.due_after)
        
        if filters.due_before:
            query = query.where(Task.due_date <= filters.due_before)
        
        if filters.completed is not None:
            query = query.where(Task.is_completed == filters.completed)
        
        if filters.tags:
            # Join with TaskTag and Tag tables to filter by tags
            query = query.join(TaskTag, Task.id == TaskTag.task_instance_id)
            query = query.join(Tag, TaskTag.tag_id == Tag.id)
            query = query.where(Tag.name.in_(filters.tags))
        
        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """Apply sorting to the query."""
        # Define valid sort fields
        valid_sort_fields = {
            'created_at': Task.created_at,
            'due_date': Task.due_date,
            'priority': Task.priority,
            'title': Task.title,
            'updated_at': Task.updated_at
        }
        
        # Validate sort field
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'  # Default sort field
        
        # Get the column to sort by
        sort_column = valid_sort_fields[sort_by]
        
        # Apply sorting
        if sort_order.lower() == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        return query

    def get_tasks_with_filters(
        self,
        user_id: UUID,
        priority: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        due_after: Optional[datetime] = None,
        due_before: Optional[datetime] = None,
        completed: Optional[bool] = None,
        title_contains: Optional[str] = None,
        description_contains: Optional[str] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'asc',
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Task], int]:
        """Get tasks with various filters and sorting."""
        # Build the base query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply filters
        if priority:
            query = query.where(Task.priority.in_(priority))
        
        if due_after:
            query = query.where(Task.due_date >= due_after)
        
        if due_before:
            query = query.where(Task.due_date <= due_before)
        
        if completed is not None:
            query = query.where(Task.is_completed == completed)
        
        if title_contains:
            query = query.where(Task.title.ilike(f"%{title_contains}%"))
        
        if description_contains:
            query = query.where(Task.description.ilike(f"%{description_contains}%"))
        
        # Apply tag filtering separately since it requires joins
        if tags:
            # Get task IDs that have any of the specified tags
            tag_query = select(TaskTag.task_instance_id).join(
                Tag, TaskTag.tag_id == Tag.id
            ).where(
                Tag.name.in_(tags)
            )
            tagged_task_ids = [row.task_instance_id for row in self.session.exec(tag_query).all()]
            
            if tagged_task_ids:
                query = query.where(Task.id.in_(tagged_task_ids))
            else:
                # If no tasks have the specified tags, return empty result
                return [], 0
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()
        
        # Apply sorting
        valid_sort_fields = {
            'created_at': Task.created_at,
            'due_date': Task.due_date,
            'priority': Task.priority,
            'title': Task.title,
            'updated_at': Task.updated_at
        }
        
        if sort_by in valid_sort_fields:
            sort_column = valid_sort_fields[sort_by]
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute the query
        results = self.session.exec(query).all()
        
        return results, total


def get_search_service(session: Session) -> SearchService:
    """Get a SearchService instance with the given session."""
    return SearchService(session)