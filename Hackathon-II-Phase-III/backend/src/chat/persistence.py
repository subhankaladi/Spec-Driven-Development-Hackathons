from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message


def load_or_create_conversation(session: Session, user_id: str) -> Conversation:
    """Get the most recent conversation for a user, or create a new one."""
    convo = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).first()

    if convo:
        return convo

    convo = Conversation(user_id=user_id)
    session.add(convo)
    session.commit()
    session.refresh(convo)
    return convo


def append_message(
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls_json: Optional[str] = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls_json=tool_calls_json,
    )
    session.add(msg)

    convo = session.get(Conversation, conversation_id)
    if convo:
        convo.updated_at = datetime.utcnow()
        session.add(convo)

    session.commit()
    session.refresh(msg)
    return msg


def list_recent_messages(
    session: Session,
    conversation_id: UUID,
    limit: int = 20,
) -> list[Message]:
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()


def get_conversation_history(
    session: Session,
    conversation_id: UUID,
    limit: int = 50,
) -> list[Message]:
    """Get conversation history ordered chronologically (oldest first)."""
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    ).all()
