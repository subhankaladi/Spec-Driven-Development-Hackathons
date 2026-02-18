"""Chat API endpoints for AI agent interaction."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import logging

from src.models.database import get_session
from src.models.conversation import Conversation
from src.models.message import Message
from src.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ToolInvocationSummary,
    ConversationHistoryResponse,
    ConversationResponse,
    MessageResponse
)
from src.api.schemas.errors import ValidationError
from src.api.dependencies.auth import get_current_user, TokenUser
from src.services.agent_service import process_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user: TokenUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send a message to the AI chat agent and receive a response.

    This endpoint enables natural language interaction with the task management
    system through an AI agent. The agent can create, list, update, and delete
    tasks based on conversational commands.

    Args:
        chat_request: ChatRequest containing message and optional conversation_id
        current_user: Authenticated user from JWT token
        session: Database session for transaction management

    Returns:
        ChatResponse with agent response, conversation_id, message_id, and tool_invocations

    Raises:
        HTTPException 400: If message validation fails
        HTTPException 401: If authentication fails
        HTTPException 500: If agent processing or database operations fail

    Example:
        Request:
        ```json
        {
            "conversation_id": null,
            "message": "Create a task to buy milk tomorrow"
        }
        ```

        Response:
        ```json
        {
            "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
            "message_id": "550e8400-e29b-41d4-a716-446655440002",
            "agent_response": "I've created a task to buy milk for tomorrow.",
            "tool_invocations": [
                {
                    "tool_name": "create_task",
                    "success": true,
                    "result": "Task created successfully",
                    "error": null
                }
            ]
        }
        ```
    """
    try:
        # Validate message: not empty, min 1 char, max 5000 chars
        # Pydantic already validates min_length=1, max_length=5000
        # Additional validation for whitespace-only messages
        if not chat_request.message.strip():
            raise ValidationError(
                message="Message cannot be empty or contain only whitespace",
                details={"field": "message", "value": "empty or whitespace only"}
            )

        # Validate conversation_id: if provided, must be valid UUID format
        # Pydantic already validates UUID type, but we add explicit error handling
        # The UUID type validation happens during Pydantic parsing, so any
        # invalid UUID will be caught before reaching this point

        # Extract user_id from JWT token
        user_id = current_user.user_id

        logger.info(
            f"Processing chat message for user {user_id}, "
            f"conversation_id: {chat_request.conversation_id}"
        )

        # Call agent service to process the message
        # agent_service.process_message handles:
        # - Loading/creating conversation
        # - Loading conversation history from database
        # - Building OpenAI messages with system prompt and history
        # - Calling OpenAI API with function tools
        # - Executing any tool calls via MCP tools
        # - Persisting user message and agent response to database
        # - Returning agent response and metadata
        agent_response_text, conversation_id, message_id, tool_invocations = process_message(
            user_message=chat_request.message,
            user_id=user_id,
            session=session,
            conversation_id=chat_request.conversation_id
        )

        # Convert tool invocations to response format
        tool_invocation_summaries = [
            ToolInvocationSummary(
                tool_name=invocation["tool_name"],
                success=invocation["success"],
                result=invocation.get("output_result") if invocation["success"] else None,
                error=invocation.get("error_message") if not invocation["success"] else None
            )
            for invocation in tool_invocations
        ]

        logger.info(
            f"Chat message processed successfully. "
            f"Conversation: {conversation_id}, Message: {message_id}, "
            f"Tools invoked: {len(tool_invocation_summaries)}"
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message_id=message_id,
            agent_response=agent_response_text,
            tool_invocations=tool_invocation_summaries
        )

    except ValidationError:
        # Re-raise validation errors (already formatted correctly)
        raise

    except ValueError as e:
        # Handle validation errors from agent_service (e.g., message too long)
        logger.warning(f"Validation error in chat endpoint: {str(e)}")
        raise ValidationError(
            message=str(e),
            details={"validation_error": str(e)}
        )

    except Exception as e:
        # Handle agent failures, tool errors, database errors
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)

        # Determine if this is an OpenAI API error
        error_message = str(e)
        if "openai" in error_message.lower() or "api" in error_message.lower():
            error_code = "AGENT_ERROR"
            user_message = "AI agent service is temporarily unavailable. Please try again later."
        elif "database" in error_message.lower() or "sql" in error_message.lower():
            error_code = "DATABASE_ERROR"
            user_message = "Database operation failed. Please try again."
        else:
            error_code = "INTERNAL_ERROR"
            user_message = "An unexpected error occurred while processing your message."

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": error_code,
                "message": user_message,
                "details": {"error": error_message} if logger.level == logging.DEBUG else None
            }
        )


@router.get("/{conversation_id}", response_model=ConversationHistoryResponse, status_code=status.HTTP_200_OK)
async def get_conversation_history(
    conversation_id: UUID,
    current_user: TokenUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Retrieve conversation history with all messages.

    This endpoint allows retrieving a complete conversation with all messages
    in chronological order. This enables resuming conversations after restarts
    and viewing conversation history.

    Args:
        conversation_id: UUID of the conversation to retrieve
        current_user: Authenticated user from JWT token
        session: Database session for querying

    Returns:
        ConversationHistoryResponse with conversation metadata and all messages

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 403: If user doesn't own the conversation
        HTTPException 404: If conversation doesn't exist
        HTTPException 500: If database operation fails

    Example:
        Request:
        ```
        GET /api/chat/{conversation_id}
        ```

        Response:
        ```json
        {
            "conversation": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440003",
                "title": "Task Planning Session",
                "created_at": "2026-01-19T10:30:00Z",
                "updated_at": "2026-01-19T10:35:00Z"
            },
            "messages": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                    "role": "user",
                    "content": "Create a task to buy milk tomorrow",
                    "created_at": "2026-01-19T10:30:00Z"
                }
            ]
        }
        ```
    """
    try:
        # Extract user_id from JWT token
        user_id = current_user.user_id

        logger.info(f"Fetching conversation {conversation_id} for user {user_id}")

        # Query conversation from database
        statement = select(Conversation).where(Conversation.id == conversation_id)
        conversation = session.exec(statement).first()

        # Check if conversation exists
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": f"Conversation with ID {conversation_id} does not exist"
                }
            )

        # Enforce user isolation - verify user owns this conversation
        if conversation.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access conversation {conversation_id} "
                f"owned by user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You do not have permission to access this conversation"
                }
            )

        # Query all messages for this conversation, ordered chronologically
        messages_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = session.exec(messages_statement).all()

        logger.info(
            f"Retrieved conversation {conversation_id} with {len(messages)} messages"
        )

        # Convert to response schemas
        conversation_response = ConversationResponse.model_validate(conversation)
        message_responses = [
            MessageResponse.model_validate(msg) for msg in messages
        ]

        return ConversationHistoryResponse(
            conversation=conversation_response,
            messages=message_responses
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(
            f"Error fetching conversation {conversation_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve conversation history",
                "details": {"error": str(e)} if logger.level == logging.DEBUG else None
            }
        )
