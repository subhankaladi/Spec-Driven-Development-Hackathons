"""Conversation service for CRUD operations on conversations and messages.

This service provides stateless functions for managing conversations and messages,
enforcing user isolation and following FastAPI best practices.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from ..models.conversation import Conversation
from ..models.message import Message


def create_conversation(
    user_id: UUID,
    title: Optional[str],
    session: Session
) -> Conversation:
    """Create a new conversation for a user.

    Args:
        user_id: UUID of the user creating the conversation
        title: Optional conversation title
        session: Database session

    Returns:
        Conversation: Newly created conversation object

    Raises:
        SQLAlchemyError: If database operation fails
    """
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation(
    conversation_id: UUID,
    user_id: UUID,
    session: Session
) -> Optional[Conversation]:
    """Get a conversation by ID with user isolation enforcement.

    Args:
        conversation_id: UUID of the conversation to retrieve
        user_id: UUID of the user requesting the conversation
        session: Database session

    Returns:
        Optional[Conversation]: Conversation object if found and owned by user, None otherwise
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conversation = session.exec(statement).first()
    return conversation


def get_user_conversations(
    user_id: UUID,
    session: Session,
    limit: int = 50,
    offset: int = 0
) -> List[Conversation]:
    """Get all conversations for a user, ordered by most recent update.

    Args:
        user_id: UUID of the user
        session: Database session
        limit: Maximum number of conversations to return (default: 50)
        offset: Number of conversations to skip (default: 0)

    Returns:
        List[Conversation]: List of conversation objects ordered by updated_at desc
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    conversations = session.exec(statement).all()
    return list(conversations)


def create_message(
    conversation_id: UUID,
    role: str,
    content: str,
    session: Session
) -> Message:
    """Create a new message in a conversation.

    Args:
        conversation_id: UUID of the parent conversation
        role: Message sender role ('user' or 'agent')
        content: Message text content (max 5000 characters)
        session: Database session

    Returns:
        Message: Newly created message object

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If role is not 'user' or 'agent'
    """
    # Validate role
    if role not in ['user', 'agent']:
        raise ValueError(f"Invalid role: {role}. Must be 'user' or 'agent'")

    # Validate content length
    if len(content) > 5000:
        raise ValueError("Message content exceeds maximum length of 5000 characters")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_conversation_messages(
    conversation_id: UUID,
    session: Session,
    limit: int = 100,
    offset: int = 0
) -> List[Message]:
    """Get all messages for a conversation, ordered by creation time.

    Args:
        conversation_id: UUID of the conversation
        session: Database session
        limit: Maximum number of messages to return (default: 100)
        offset: Number of messages to skip (default: 0)

    Returns:
        List[Message]: List of message objects ordered by created_at asc
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    messages = session.exec(statement).all()
    return list(messages)


def update_conversation_timestamp(
    conversation_id: UUID,
    session: Session
) -> None:
    """Update the updated_at timestamp of a conversation.

    This should be called whenever a new message is added to keep
    conversations sorted by most recent activity.

    Args:
        conversation_id: UUID of the conversation to update
        session: Database session

    Raises:
        ValueError: If conversation does not exist
    """
    statement = select(Conversation).where(Conversation.id == conversation_id)
    conversation = session.exec(statement).first()

    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()


def delete_conversation(
    conversation_id: UUID,
    user_id: UUID,
    session: Session
) -> bool:
    """Delete a conversation and all its messages (with user isolation).

    Args:
        conversation_id: UUID of the conversation to delete
        user_id: UUID of the user requesting deletion
        session: Database session

    Returns:
        bool: True if conversation was deleted, False if not found or not owned by user
    """
    # Verify ownership before deletion
    conversation = get_conversation(conversation_id, user_id, session)

    if conversation is None:
        return False

    # Delete all messages first (cascading would happen automatically if configured)
    statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(statement).all()
    for message in messages:
        session.delete(message)

    # Delete the conversation
    session.delete(conversation)
    session.commit()
    return True
