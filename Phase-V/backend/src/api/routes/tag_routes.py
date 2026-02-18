"""Tag API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from ..models.database import get_session
from ..models.user import User
from ..schemas.tag import TagCreate, TagUpdate, TagResponse
from ..controllers.tag_controller import get_tag_controller, TagController
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Create a new tag for the user."""
    return await controller.create_tag(
        user_id=current_user.id,
        tag_data=tag_data,
        session=session
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Get a specific tag."""
    return await controller.get_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/", response_model=List[TagResponse])
async def get_user_tags(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Get all tags for the user."""
    return await controller.get_user_tags(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        session=session
    )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    update_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Update a tag."""
    return await controller.update_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.patch("/{tag_id}", response_model=TagResponse)
async def partially_update_tag(
    tag_id: UUID,
    update_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Partially update a tag."""
    return await controller.update_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Delete a tag and all its associations."""
    success = await controller.delete_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return


@router.post("/{tag_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_task(
    tag_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Associate a tag with a task."""
    success = await controller.add_tag_to_task(
        task_instance_id=task_id,
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or tag not found"
        )
    
    return


@router.delete("/{tag_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_task(
    tag_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Remove a tag association from a task."""
    success = await controller.remove_tag_from_task(
        task_instance_id=task_id,
        tag_id=tag_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or tag not found, or association doesn't exist"
        )
    
    return


@router.get("/by-task/{task_id}", response_model=List[TagResponse])
async def get_task_tags(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Get all tags associated with a task."""
    return await controller.get_task_tags(
        task_instance_id=task_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/suggest", response_model=List[TagResponse])
async def suggest_tags(
    query: str = Query(..., min_length=1, max_length=50),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=20),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Get tag suggestions based on partial name match."""
    # In a real implementation, this would search for tags matching the query
    # For now, we'll return an empty list as a placeholder
    return []


@router.get("/stats", response_model=dict)
async def get_tag_stats(
    current_user: User = Depends(get_current_user),
    controller: TagController = Depends(get_tag_controller),
    session: Session = Depends(get_session)
):
    """Get statistics about tags for the user."""
    # In a real implementation, this would return tag usage statistics
    # For now, we'll return a placeholder response
    return {
        "total_tags": 0,
        "most_used_tags": [],
        "tags_by_color": {}
    }