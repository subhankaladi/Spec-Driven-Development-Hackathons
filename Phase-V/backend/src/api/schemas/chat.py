"""Chat Pydantic schemas for API request/response.

These schemas define the contract for the chat agent API endpoints,
including conversation creation, message sending, and agent responses.
"""
from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ChatRequest(BaseModel):
    """Schema for sending a chat message to the agent.

    Attributes:
        conversation_id: Optional UUID of existing conversation (None creates new conversation)
        message: User's message text (required, 1-5000 characters)
    """

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Optional conversation ID (null creates new conversation)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's message text (required, 1-5000 characters)"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_schema_extra={
            "example": {
                "conversationId": None,
                "message": "Create a task to buy milk tomorrow"
            }
        }
    )


class ToolInvocationSummary(BaseModel):
    """Schema for summarizing a tool invocation in the response.

    Attributes:
        tool_name: Name of the invoked MCP tool
        success: Boolean indicating if tool invocation succeeded
        result: Optional string representation of the tool result
        error: Optional error message if invocation failed
    """

    tool_name: str = Field(
        ...,
        description="Name of the invoked MCP tool"
    )
    success: bool = Field(
        ...,
        description="Boolean indicating if tool invocation succeeded"
    )
    result: Optional[str] = Field(
        default=None,
        description="Optional string representation of the tool result"
    )
    error: Optional[str] = Field(
        default=None,
        description="Optional error message if invocation failed"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_schema_extra={
            "example": {
                "toolName": "create_task",
                "success": True,
                "result": "Task created with ID: 550e8400-e29b-41d4-a716-446655440000",
                "error": None
            }
        }
    )


class ChatResponse(BaseModel):
    """Schema for agent response to a chat message.

    Attributes:
        conversation_id: UUID of the conversation
        message_id: UUID of the agent's message
        agent_response: Agent's text response to the user
        tool_invocations: List of tool invocations that occurred during processing
    """

    conversation_id: UUID = Field(
        ...,
        description="UUID of the conversation"
    )
    message_id: UUID = Field(
        ...,
        description="UUID of the agent's message"
    )
    agent_response: str = Field(
        ...,
        description="Agent's text response to the user"
    )
    tool_invocations: List[ToolInvocationSummary] = Field(
        default_factory=list,
        description="List of tool invocations that occurred during processing"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_schema_extra={
            "example": {
                "conversationId": "550e8400-e29b-41d4-a716-446655440001",
                "messageId": "550e8400-e29b-41d4-a716-446655440002",
                "agentResponse": "I've created a task to buy milk for tomorrow.",
                "toolInvocations": [
                    {
                        "toolName": "create_task",
                        "success": True,
                        "result": "Task created with ID: 550e8400-e29b-41d4-a716-446655440000",
                        "error": None
                    }
                ]
            }
        }
    )


class ConversationResponse(BaseModel):
    """Schema for conversation metadata response.

    Attributes:
        id: Unique conversation identifier
        user_id: Owner user identifier
        title: Optional conversation title
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID = Field(..., description="Unique conversation identifier")
    user_id: UUID = Field(..., description="Owner user identifier")
    title: Optional[str] = Field(default=None, description="Optional conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "userId": "550e8400-e29b-41d4-a716-446655440003",
                "title": "Task Planning Session",
                "createdAt": "2026-01-19T10:30:00Z",
                "updatedAt": "2026-01-19T10:35:00Z"
            }
        }
    )


class MessageResponse(BaseModel):
    """Schema for individual message response.

    Attributes:
        id: Unique message identifier
        conversation_id: Parent conversation identifier
        role: Message sender role ('user' or 'agent')
        content: Message text content
        created_at: Creation timestamp
    """

    id: UUID = Field(..., description="Unique message identifier")
    conversation_id: UUID = Field(..., description="Parent conversation identifier")
    role: str = Field(..., description="Message sender role ('user' or 'agent')")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "conversationId": "550e8400-e29b-41d4-a716-446655440001",
                "role": "user",
                "content": "Create a task to buy milk tomorrow",
                "createdAt": "2026-01-19T10:30:00Z"
            }
        }
    )


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history (conversation + messages).

    Attributes:
        conversation: Conversation metadata
        messages: List of messages in chronological order
    """

    conversation: ConversationResponse = Field(..., description="Conversation metadata")
    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="List of messages in chronological order"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation": {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "userId": "550e8400-e29b-41d4-a716-446655440003",
                    "title": "Task Planning Session",
                    "createdAt": "2026-01-19T10:30:00Z",
                    "updatedAt": "2026-01-19T10:35:00Z"
                },
                "messages": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "conversationId": "550e8400-e29b-41d4-a716-446655440001",
                        "role": "user",
                        "content": "Create a task to buy milk tomorrow",
                        "createdAt": "2026-01-19T10:30:00Z"
                    },
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440004",
                        "conversationId": "550e8400-e29b-41d4-a716-446655440001",
                        "role": "agent",
                        "content": "I've created a task to buy milk for tomorrow.",
                        "createdAt": "2026-01-19T10:30:05Z"
                    }
                ]
            }
        }
    )


class ConversationListResponse(BaseModel):
    """Schema for list of conversations.

    Attributes:
        conversations: List of conversation metadata
        total: Total number of conversations for the user
    """

    conversations: List[ConversationResponse] = Field(
        default_factory=list,
        description="List of conversation metadata"
    )
    total: int = Field(..., description="Total number of conversations for the user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "userId": "550e8400-e29b-41d4-a716-446655440003",
                        "title": "Task Planning Session",
                        "createdAt": "2026-01-19T10:30:00Z",
                        "updatedAt": "2026-01-19T10:35:00Z"
                    }
                ],
                "total": 1
            }
        }
    )
