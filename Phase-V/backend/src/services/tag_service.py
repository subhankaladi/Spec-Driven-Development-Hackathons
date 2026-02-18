"""Tag Service for managing task tags and tag associations."""
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from ..models.tag import Tag
from ..models.task_tag import TaskTag
from ..models.task import Task
from ..api.schemas.tag import TagCreate, TagUpdate


class TagService:
    """Service class for managing tags and tag associations."""

    def __init__(self, session: Session):
        self.session = session

    def create_tag(self, user_id: UUID, tag_data: TagCreate) -> Tag:
        """Create a new tag for a user."""
        # Check if tag with this name already exists for the user
        existing_tag = self.session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == tag_data.name
            )
        ).first()
        
        if existing_tag:
            raise ValueError(f"Tag with name '{tag_data.name}' already exists for user {user_id}")
        
        # Create the tag
        tag = Tag(
            user_id=user_id,
            name=tag_data.name,
            color=tag_data.color
        )
        
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        
        return tag

    def get_tag(self, tag_id: UUID, user_id: UUID) -> Optional[Tag]:
        """Get a specific tag for a user."""
        statement = select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_user_tags(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags for a user."""
        statement = select(Tag).where(
            Tag.user_id == user_id
        ).order_by(Tag.name.asc()).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def get_tag_by_name(self, user_id: UUID, name: str) -> Optional[Tag]:
        """Get a tag by name for a user."""
        statement = select(Tag).where(
            Tag.user_id == user_id,
            Tag.name == name
        )
        return self.session.exec(statement).first()

    def update_tag(self, tag_id: UUID, user_id: UUID, update_data: TagUpdate) -> Optional[Tag]:
        """Update a tag."""
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return None

        # Check if new name already exists for this user (if name is being updated)
        if update_data.name is not None and update_data.name != tag.name:
            existing_tag = self.session.exec(
                select(Tag).where(
                    Tag.user_id == user_id,
                    Tag.name == update_data.name
                )
            ).first()
            
            if existing_tag:
                raise ValueError(f"Tag with name '{update_data.name}' already exists for user {user_id}")
        
        # Update fields if provided
        if update_data.name is not None:
            tag.name = update_data.name
        if update_data.color is not None:
            tag.color = update_data.color
        
        # Update the timestamp
        tag.updated_at = datetime.utcnow()
        
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        
        return tag

    def delete_tag(self, tag_id: UUID, user_id: UUID) -> bool:
        """Delete a tag and remove all associations."""
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return False
        
        # Remove all associations with this tag
        stmt = select(TaskTag).where(TaskTag.tag_id == tag_id)
        associations = self.session.exec(stmt).all()
        
        for assoc in associations:
            self.session.delete(assoc)
        
        # Delete the tag
        self.session.delete(tag)
        self.session.commit()
        
        return True

    def add_tag_to_task(self, task_instance_id: UUID, tag_id: UUID, user_id: UUID) -> bool:
        """Associate a tag with a task."""
        # Verify that both the task and tag belong to the user
        task = self.session.exec(
            select(Task).where(Task.id == task_instance_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            raise ValueError(f"Task {task_instance_id} not found or does not belong to user {user_id}")
        
        tag = self.session.exec(
            select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        ).first()
        
        if not tag:
            raise ValueError(f"Tag {tag_id} not found or does not belong to user {user_id}")
        
        # Check if association already exists
        existing_assoc = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_instance_id == task_instance_id,
                TaskTag.tag_id == tag_id
            )
        ).first()
        
        if existing_assoc:
            # Association already exists
            return True
        
        # Create the association
        task_tag = TaskTag(
            task_instance_id=task_instance_id,
            tag_id=tag_id
        )
        
        self.session.add(task_tag)
        self.session.commit()
        
        return True

    def remove_tag_from_task(self, task_instance_id: UUID, tag_id: UUID, user_id: UUID) -> bool:
        """Remove a tag association from a task."""
        # Verify that both the task and tag belong to the user
        task = self.session.exec(
            select(Task).where(Task.id == task_instance_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            raise ValueError(f"Task {task_instance_id} not found or does not belong to user {user_id}")
        
        tag = self.session.exec(
            select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        ).first()
        
        if not tag:
            raise ValueError(f"Tag {tag_id} not found or does not belong to user {user_id}")
        
        # Find and delete the association
        assoc = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_instance_id == task_instance_id,
                TaskTag.tag_id == tag_id
            )
        ).first()
        
        if not assoc:
            # Association doesn't exist
            return False
        
        self.session.delete(assoc)
        self.session.commit()
        
        return True

    def get_task_tags(self, task_instance_id: UUID, user_id: UUID) -> List[Tag]:
        """Get all tags associated with a task."""
        # Verify that the task belongs to the user
        task = self.session.exec(
            select(Task).where(Task.id == task_instance_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            raise ValueError(f"Task {task_instance_id} not found or does not belong to user {user_id}")
        
        # Get all tag IDs associated with this task
        stmt = select(TaskTag.tag_id).where(TaskTag.task_instance_id == task_instance_id)
        tag_ids = [row.tag_id for row in self.session.exec(stmt).all()]
        
        if not tag_ids:
            return []
        
        # Get the tag details
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        return self.session.exec(stmt).all()

    def get_tasks_by_tag(self, tag_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks associated with a specific tag."""
        # Verify that the tag belongs to the user
        tag = self.session.exec(
            select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        ).first()
        
        if not tag:
            raise ValueError(f"Tag {tag_id} not found or does not belong to user {user_id}")
        
        # Get all task IDs associated with this tag
        stmt = select(TaskTag.task_instance_id).where(TaskTag.tag_id == tag_id)
        task_ids = [row.task_instance_id for row in self.session.exec(stmt).all()]
        
        if not task_ids:
            return []
        
        # Get the task details
        stmt = select(Task).where(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        ).offset(skip).limit(limit)
        return self.session.exec(stmt).all()


def get_tag_service(session: Session) -> TagService:
    """Get a TagService instance with the given session."""
    return TagService(session)