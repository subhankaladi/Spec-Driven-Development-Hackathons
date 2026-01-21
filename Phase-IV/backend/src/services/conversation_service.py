"""Conversation persistence and retrieval service.

This service handles all database operations for conversations and messages,
including user authorization and pagination.
"""
import logging
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy import func

from src.models.conversation import Conversation, Message, MessageRole

logger = logging.getLogger(__name__)


async def create_conversation(
    session: Session,
    user_id: UUID,
    title: Optional[str] = None
) -> Conversation:
    """Create new conversation for user.

    Args:
        session: Database session
        user_id: UUID of the owning user
        title: Optional conversation title

    Returns:
        Created Conversation entity

    Raises:
        SQLAlchemyError: On database operation failure
    """
    logger.debug(f"create_conversation called with user_id={user_id}, title={title}")

    try:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation

    except Exception as e:
        logger.error(f"Failed to create conversation for user {user_id}: {str(e)}")
        raise


async def add_message(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict] = None
) -> Message:
    """Add message to conversation.

    Args:
        session: Database session
        conversation_id: UUID of the parent conversation
        user_id: UUID of the owning user (for authorization)
        role: Message role (user or assistant)
        content: Message content text (non-empty)
        tool_calls: Optional JSON of MCP tool invocations

    Returns:
        Created Message entity

    Raises:
        ValueError: If conversation not found or user not authorized
        SQLAlchemyError: On database operation failure
    """
    from datetime import datetime

    logger.debug(
        f"add_message called with conversation_id={conversation_id}, "
        f"user_id={user_id}, role={role}, content_length={len(content)}"
    )

    try:
        # Validate content length (1-50000 chars)
        content = content.strip()
        if not content:
            raise ValueError("Message content cannot be empty")
        if len(content) > 50000:
            raise ValueError("Message content exceeds maximum length of 50000 characters")

        # Verify conversation exists and user is authorized
        conversation_query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = session.exec(conversation_query)
        conversation = result.first()

        if not conversation:
            logger.error(
                f"Failed to add message: conversation {conversation_id} not found "
                f"or user {user_id} not authorized"
            )
            raise ValueError("Conversation not found or user not authorized")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )

        session.add(message)

        # Update conversation.updated_at
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        session.commit()
        session.refresh(message)

        logger.info(
            f"Added {role} message {message.id} to conversation {conversation_id} "
            f"for user {user_id}"
        )
        return message

    except ValueError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to add message to conversation {conversation_id} "
            f"for user {user_id}: {str(e)}"
        )
        raise


async def get_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """Fetch conversation with user scoping.

    Args:
        session: Database session
        conversation_id: UUID of the conversation to fetch
        user_id: UUID of the requesting user (for authorization)

    Returns:
        Conversation entity if found and user is authorized, None otherwise

    Raises:
        SQLAlchemyError: On database operation failure
    """
    logger.debug(f"get_conversation called with conversation_id={conversation_id}, user_id={user_id}")

    try:
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = session.exec(query)
        conversation = result.first()

        if conversation:
            logger.info(f"Retrieved conversation {conversation_id} for user {user_id}")
        else:
            logger.info(f"Conversation {conversation_id} not found for user {user_id}")

        return conversation

    except Exception as e:
        logger.error(f"Failed to retrieve conversation {conversation_id} for user {user_id}: {str(e)}")
        raise


async def get_conversation_messages(
    session: Session,
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0
) -> list[Message]:
    """Get paginated messages for conversation.

    Messages are ordered by created_at ASC (chronological order).

    Args:
        session: Database session
        conversation_id: UUID of the conversation
        limit: Maximum number of messages to return (default 100)
        offset: Number of messages to skip (default 0)

    Returns:
        List of Message entities ordered by creation time

    Raises:
        SQLAlchemyError: On database operation failure
    """
    logger.debug(
        f"get_conversation_messages called with conversation_id={conversation_id}, "
        f"limit={limit}, offset={offset}"
    )

    try:
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(offset).limit(limit)

        result = session.exec(query)
        messages = result.all()

        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        return messages

    except Exception as e:
        logger.error(f"Failed to retrieve messages for conversation {conversation_id}: {str(e)}")
        raise


async def verify_user_owns_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> bool:
    """Verify user authorization for conversation.

    Args:
        session: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user to verify

    Returns:
        True if user owns the conversation, False otherwise

    Raises:
        SQLAlchemyError: On database operation failure
    """
    conversation = await get_conversation(session, conversation_id, user_id)
    return conversation is not None


async def list_conversations(
    session: Session,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[Conversation], int]:
    """List user's conversations with pagination.

    Conversations are ordered by updated_at DESC (most recent first).

    Args:
        session: Database session
        user_id: UUID of the owning user
        limit: Maximum number of conversations to return (default 50)
        offset: Number of conversations to skip (default 0)

    Returns:
        Tuple of (list of Conversation entities, total count)

    Raises:
        SQLAlchemyError: On database operation failure
    """
    logger.debug(f"list_conversations called with user_id={user_id}, limit={limit}, offset={offset}")

    try:
        # Count total conversations for user
        count_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        count_result = session.exec(count_query)
        total = count_result.one()

        # Get paginated conversations
        query = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)

        result = session.exec(query)
        conversations = result.all()

        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id} (total: {total})")
        return conversations, total

    except Exception as e:
        logger.error(f"Failed to list conversations for user {user_id}: {str(e)}")
        raise
