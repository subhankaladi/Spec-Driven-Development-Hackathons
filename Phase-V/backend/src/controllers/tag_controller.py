"""Tag Controller for managing task tags and tag associations."""
from typing import List
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from ..models.database import get_session
from ..models.tag import Tag
from ..models.task_tag import TaskTag
from ..schemas.tag import TagCreate, TagUpdate, TagResponse
from ..services.tag_service import TagService
from ..services.event_service import EventService


class TagController:
    """Controller class for managing tags and tag associations."""

    def __init__(
        self,
        tag_service: TagService,
        event_service: EventService
    ):
        self.tag_service = tag_service
        self.event_service = event_service

    async def create_tag(
        self,
        user_id: UUID,
        tag_data: TagCreate,
        session: Session
    ) -> TagResponse:
        """Create a new tag for a user."""
        try:
            # Check if a tag with this name already exists for the user
            existing_tag = self.tag_service.get_tag_by_name(user_id, tag_data.name)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Tag with name '{tag_data.name}' already exists for user {user_id}"
                )
            
            # Create the tag
            tag = self.tag_service.create_tag(
                user_id=user_id,
                tag_data=tag_data
            )
            
            # Log and publish the tag creation event
            await self.event_service.log_tag_created(
                user_id=user_id,
                tag_id=tag.id,
                tag_data=tag_data.dict()
            )
            
            return TagResponse(
                id=tag.id,
                user_id=tag.user_id,
                name=tag.name,
                color=tag.color,
                created_at=tag.created_at,
                updated_at=tag.updated_at
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create tag: {str(e)}"
            )

    async def get_tag(
        self,
        tag_id: UUID,
        user_id: UUID,
        session: Session
    ) -> TagResponse:
        """Get a specific tag for a user."""
        tag = self.tag_service.get_tag(tag_id, user_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        return TagResponse(
            id=tag.id,
            user_id=tag.user_id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at,
            updated_at=tag.updated_at
        )

    async def get_user_tags(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ) -> List[TagResponse]:
        """Get all tags for a user."""
        try:
            tags = self.tag_service.get_user_tags(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
            
            responses = []
            for tag in tags:
                responses.append(TagResponse(
                    id=tag.id,
                    user_id=tag.user_id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at
                ))
            
            return responses
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user tags: {str(e)}"
            )

    async def update_tag(
        self,
        tag_id: UUID,
        user_id: UUID,
        update_data: TagUpdate,
        session: Session
    ) -> TagResponse:
        """Update a tag."""
        # Verify the tag exists and belongs to the user
        existing_tag = self.tag_service.get_tag(tag_id, user_id)
        if not existing_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        try:
            # If updating the name, check if the new name already exists for the user
            if update_data.name is not None:
                # Check if another tag with this name already exists for the user
                existing_by_name = self.tag_service.get_tag_by_name(user_id, update_data.name)
                if existing_by_name and existing_by_name.id != tag_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Tag with name '{update_data.name}' already exists for user {user_id}"
                    )
            
            # Update the tag
            updated_tag = self.tag_service.update_tag(
                tag_id=tag_id,
                user_id=user_id,
                update_data=update_data
            )
            
            if not updated_tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tag not found"
                )
            
            # Log and publish the tag update event
            await self.event_service.log_tag_updated(
                user_id=user_id,
                tag_id=updated_tag.id,
                update_data=update_data.dict()
            )
            
            return TagResponse(
                id=updated_tag.id,
                user_id=updated_tag.user_id,
                name=updated_tag.name,
                color=updated_tag.color,
                created_at=updated_tag.created_at,
                updated_at=updated_tag.updated_at
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update tag: {str(e)}"
            )

    async def delete_tag(
        self,
        tag_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Delete a tag and all its associations."""
        # Verify the tag exists and belongs to the user
        tag = self.tag_service.get_tag(tag_id, user_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        try:
            # Delete the tag (this should also remove all associations)
            success = self.tag_service.delete_tag(tag_id, user_id)
            
            if success:
                # Log and publish the tag deletion event
                await self.event_service.log_tag_deleted(
                    user_id=user_id,
                    tag_id=tag_id
                )
            
            return success
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete tag: {str(e)}"
            )

    async def add_tag_to_task(
        self,
        task_instance_id: UUID,
        tag_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Associate a tag with a task."""
        try:
            # Verify both the task and tag belong to the user
            task = self.task_service.get_task(task_instance_id, user_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )
            
            tag = self.tag_service.get_tag(tag_id, user_id)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tag not found or does not belong to user"
                )
            
            # Create the association
            success = self.tag_service.add_tag_to_task(
                task_instance_id=task_instance_id,
                tag_id=tag_id,
                user_id=user_id
            )
            
            if success:
                # Log and publish the tag association event
                await self.event_service.log_tag_associated_with_task(
                    user_id=user_id,
                    task_id=task_instance_id,
                    tag_id=tag_id
                )
            
            return success
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to associate tag with task: {str(e)}"
            )

    async def remove_tag_from_task(
        self,
        task_instance_id: UUID,
        tag_id: UUID,
        user_id: UUID,
        session: Session
    ) -> bool:
        """Remove a tag association from a task."""
        try:
            # Verify both the task and tag belong to the user
            task = self.task_service.get_task(task_instance_id, user_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )
            
            tag = self.tag_service.get_tag(tag_id, user_id)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tag not found or does not belong to user"
                )
            
            # Remove the association
            success = self.tag_service.remove_tag_from_task(
                task_instance_id=task_instance_id,
                tag_id=tag_id,
                user_id=user_id
            )
            
            if success:
                # Log and publish the tag disassociation event
                await self.event_service.log_tag_disassociated_from_task(
                    user_id=user_id,
                    task_id=task_instance_id,
                    tag_id=tag_id
                )
            
            return success
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove tag from task: {str(e)}"
            )

    async def get_task_tags(
        self,
        task_instance_id: UUID,
        user_id: UUID,
        session: Session
    ) -> List[TagResponse]:
        """Get all tags associated with a task."""
        try:
            # Verify the task belongs to the user
            task = self.task_service.get_task(task_instance_id, user_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )
            
            # Get the tags associated with the task
            tags = self.tag_service.get_task_tags(
                task_instance_id=task_instance_id,
                user_id=user_id
            )
            
            responses = []
            for tag in tags:
                responses.append(TagResponse(
                    id=tag.id,
                    user_id=tag.user_id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at
                ))
            
            return responses
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get task tags: {str(e)}"
            )


def get_tag_controller(
    tag_service: TagService = Depends(),
    event_service: EventService = Depends()
) -> TagController:
    """Get a TagController instance with dependencies."""
    return TagController(
        tag_service=tag_service,
        event_service=event_service
    )