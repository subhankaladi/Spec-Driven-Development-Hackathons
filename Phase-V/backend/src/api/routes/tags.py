"""Tag API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from ...models.database import get_session
from ...models.tag import Tag
from ...services.tag_service import get_tag_service, TagService
from ...api.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse
)
from ...api.dependencies import get_current_user
from ...models.user import User
from sqlalchemy import func


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagListResponse)
async def list_tags(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all tags for the current user."""
    service = get_tag_service(session)
    tags = service.get_user_tags(current_user.id, skip=skip, limit=limit)
    
    # Count total for pagination
    total = len(tags)  # Simplified for this example
    
    # Calculate pagination details
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    # Convert SQLModel objects to Pydantic response models
    items = []
    for tag in tags:
        items.append(TagResponse(
            id=tag.id,
            user_id=tag.user_id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at,
            updated_at=tag.updated_at
        ))
    
    return TagListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tag."""
    service = get_tag_service(session)
    try:
        tag = service.create_tag(
            user_id=current_user.id,
            tag_data=tag_data
        )
        # Convert SQLModel object to Pydantic response model
        return TagResponse(
            id=tag.id,
            user_id=tag.user_id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at,
            updated_at=tag.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific tag."""
    service = get_tag_service(session)
    tag = service.get_tag(tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Convert SQLModel object to Pydantic response model
    return TagResponse(
        id=tag.id,
        user_id=tag.user_id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    update_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a tag."""
    service = get_tag_service(session)
    tag = service.update_tag(tag_id, current_user.id, update_data)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Convert SQLModel object to Pydantic response model
    return TagResponse(
        id=tag.id,
        user_id=tag.user_id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )


@router.patch("/{tag_id}", response_model=TagResponse)
async def partially_update_tag(
    tag_id: UUID,
    update_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Partially update a tag."""
    service = get_tag_service(session)
    tag = service.update_tag(tag_id, current_user.id, update_data)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Convert SQLModel object to Pydantic response model
    return TagResponse(
        id=tag.id,
        user_id=tag.user_id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a tag."""
    service = get_tag_service(session)
    success = service.delete_tag(tag_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return