"""Pydantic schemas for chat API requests and responses.

This module defines the request/response models for the chat API endpoints,
ensuring proper validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel


class ToolCall(BaseModel):
    """Represents a single tool invocation by the agent.

    Attributes:
        tool: Name of the MCP tool invoked (e.g., "add_task", "list_tasks")
        parameters: Input parameters passed to the tool
        result: Result returned by the tool execution
    """

    tool: str = Field(..., description="Name of the tool invoked")
    parameters: dict = Field(
        default_factory=dict, description="Parameters passed to the tool"
    )
    result: dict = Field(
        default_factory=dict, description="Result returned by the tool"
    )


class Message(BaseModel):
    """Represents a single message in a conversation.

    Attributes:
        id: Unique message identifier
        role: Message sender role (user or assistant)
        content: Text content of the message
        tool_calls: Optional list of tool invocations (for assistant messages)
        created_at: Timestamp when message was created
    """

    id: UUID = Field(..., description="Unique message identifier")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    tool_calls: Optional[list[ToolCall]] = Field(
        default=None, description="Tool calls made by assistant (if any)"
    )
    created_at: datetime = Field(..., description="Message creation timestamp")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is either 'user' or 'assistant'."""
        if v not in ("user", "assistant"):
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries",
                "toolCalls": None,
                "createdAt": "2026-01-16T12:00:00Z",
            }
        }
    )


class ChatRequest(BaseModel):
    """Request schema for POST /api/chat endpoint.

    Attributes:
        conversation_id: Optional existing conversation ID (omit for new conversation)
        message: User's text message (max 5000 characters)
    """

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID (omit to create new conversation)",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's message text (1-5000 characters)",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "conversationId": None,
                "message": "Add a task to buy groceries for tomorrow",
            }
        }
    )


class ChatResponse(BaseModel):
    """Response schema for POST /api/chat endpoint.

    Attributes:
        conversation_id: ID of the conversation (new or existing)
        user_message: The user's message that was processed
        agent_response: The agent's response with optional tool calls
    """

    conversation_id: UUID = Field(..., description="Conversation identifier")
    user_message: Message = Field(..., description="User's message")
    agent_response: Message = Field(..., description="Agent's response")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "conversationId": "550e8400-e29b-41d4-a716-446655440000",
                "userMessage": {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "role": "user",
                    "content": "Add a task to buy groceries",
                    "toolCalls": None,
                    "createdAt": "2026-01-16T12:00:00Z",
                },
                "agentResponse": {
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "role": "assistant",
                    "content": "I've added a task to buy groceries for you.",
                    "toolCalls": [
                        {
                            "tool": "add_task",
                            "parameters": {"title": "Buy groceries"},
                            "result": {"success": True, "task_id": "task-123"},
                        }
                    ],
                    "createdAt": "2026-01-16T12:00:01Z",
                },
            }
        }
    )


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing endpoint.

    Attributes:
        id: Conversation identifier
        title: Conversation title (derived from first message)
        created_at: When conversation was created
        updated_at: When conversation was last updated
        message_count: Number of messages in conversation
    """

    id: UUID = Field(..., description="Conversation identifier")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Task Management",
                "createdAt": "2026-01-16T12:00:00Z",
                "updatedAt": "2026-01-16T12:05:00Z",
                "messageCount": 6,
            }
        }
    )


class ConversationDetail(BaseModel):
    """Detailed conversation with all messages.

    Attributes:
        id: Conversation identifier
        title: Conversation title
        created_at: When conversation was created
        updated_at: When conversation was last updated
        messages: All messages in chronological order
    """

    id: UUID = Field(..., description="Conversation identifier")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    messages: list[Message] = Field(
        default_factory=list, description="All messages in order"
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Task Management",
                "createdAt": "2026-01-16T12:00:00Z",
                "updatedAt": "2026-01-16T12:05:00Z",
                "messages": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "role": "user",
                        "content": "Add a task to buy groceries",
                        "toolCalls": None,
                        "createdAt": "2026-01-16T12:00:00Z",
                    },
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "role": "assistant",
                        "content": "I've added the task for you.",
                        "toolCalls": [
                            {
                                "tool": "add_task",
                                "parameters": {"title": "Buy groceries"},
                                "result": {"success": True},
                            }
                        ],
                        "createdAt": "2026-01-16T12:00:01Z",
                    },
                ],
            }
        }
    )


class ConversationListResponse(BaseModel):
    """Response schema for GET /api/chat/conversations endpoint.

    Attributes:
        conversations: List of conversation summaries
        total: Total number of conversations for the user
        limit: Number of conversations per page
        offset: Current offset in pagination
    """

    conversations: list[ConversationSummary] = Field(
        default_factory=list, description="List of conversations"
    )
    total: int = Field(..., description="Total conversation count")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "conversations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Task Management",
                        "createdAt": "2026-01-16T12:00:00Z",
                        "updatedAt": "2026-01-16T12:05:00Z",
                        "messageCount": 6,
                    }
                ],
                "total": 1,
                "limit": 20,
                "offset": 0,
            }
        }
    )
