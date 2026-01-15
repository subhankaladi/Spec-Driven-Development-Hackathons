from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    conversation_id: UUID = Field(index=True, foreign_key="conversation.id")

    role: str = Field(max_length=32)
    content: str

    # serialized JSON for tool calls/results for audit/debug
    tool_calls_json: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
