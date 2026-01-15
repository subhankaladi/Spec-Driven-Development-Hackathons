from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="User message in natural language")


class ChatResponse(BaseModel):
    conversation_id: str
    assistant_message: str
