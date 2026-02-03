"""Chat API routes for AI agent interaction.

This module defines the chat endpoints:
- POST /api/chat - Send a message to the agent
- GET /api/chat/{conversation_id} - Retrieve conversation history
- GET /api/chat/conversations - List user's conversations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlmodel import Session
from sqlalchemy import func, select
from uuid import UUID

from src.api.dependencies.auth import get_current_user, TokenUser
from src.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Message as MessageSchema,
    ToolCall,
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary
)
from src.models.database import get_session
from src.models.conversation import MessageRole, Conversation, Message
from src.services.conversation_service import (
    create_conversation,
    add_message,
    get_conversation_messages,
    get_conversation,
    verify_user_owns_conversation,
    list_conversations
)
from src.services.agent_service import get_agent_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


def extract_jwt_token(request: Request) -> str:
    """Extract JWT token from request cookies or headers.

    Args:
        request: FastAPI request object

    Returns:
        JWT token string

    Raises:
        HTTPException: If no token found
    """
    # Try multiple cookie names (access_token, better-auth-session)
    token = request.cookies.get("access_token") or request.cookies.get("better-auth-session")

    # Try Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token not found"
        )

    return token


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to AI agent for task management",
    description="""
    Process a natural language message through the AI agent for task management.

    The agent can:
    - Create new tasks from natural language ("Add a task to buy groceries")
    - List and filter tasks ("Show me my important tasks")
    - Complete tasks ("Mark the grocery task as done")
    - Update task details ("Change the title of task X to Y")
    - Delete tasks ("Remove all completed tasks")
    - Chain multiple operations ("List my tasks and delete all completed ones")

    **Multi-turn Conversations:**
    - First message creates a new conversation (conversation_id returned)
    - Subsequent messages can reference the conversation_id for context
    - Agent remembers last 10 messages for contextual responses

    **Tool Invocation:**
    - Agent automatically invokes MCP tools based on user intent
    - Tool calls are recorded and returned in the response
    - Multiple tools can be chained for complex requests

    **Rate Limiting:**
    - Limited to 10 requests per minute per authenticated user
    - Returns 429 if limit exceeded

    **Example Requests:**
    - "Add a task to buy groceries"
    - "Show me all my incomplete tasks"
    - "Mark task abc123 as completed"
    - "List my tasks and delete all the completed ones"
    """,
    responses={
        200: {
            "description": "Successful response with agent's message and tool calls",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_message": {
                            "id": "234e5678-e89b-12d3-a456-426614174001",
                            "role": "user",
                            "content": "Add a task to buy groceries",
                            "tool_calls": None,
                            "created_at": "2024-01-17T12:00:00Z"
                        },
                        "agent_response": {
                            "id": "345e6789-e89b-12d3-a456-426614174002",
                            "role": "assistant",
                            "content": "I've added 'Buy groceries' to your task list!",
                            "tool_calls": [
                                {
                                    "tool": "add_task",
                                    "parameters": {"title": "Buy groceries"},
                                    "result": {"success": True, "task_id": "456e7890-e89b-12d3-a456-426614174003"}
                                }
                            ],
                            "created_at": "2024-01-17T12:00:01Z"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation error (empty message or too long)",
            "content": {
                "application/json": {
                    "example": {"detail": "That message is too long. Please use fewer than 5000 characters."}
                }
            }
        },
        401: {
            "description": "Authentication token missing or invalid",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication token not found"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Too many requests. Please try again in a moment."}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process chat message. Please try again."}
                }
            }
        }
    }
)
async def send_message(
    chat_request: ChatRequest,
    request: Request,
    current_user: TokenUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Send a message to the AI agent and get a response.

    This endpoint handles natural language task management by:
    1. Creating or retrieving conversation
    2. Persisting user message
    3. Processing message through AI agent with MCP tools
    4. Persisting agent response with tool calls
    5. Returning complete chat exchange

    Args:
        chat_request: Request containing message and optional conversation_id
        request: FastAPI request for extracting JWT
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ChatResponse with conversation_id, user_message, and agent_response

    Raises:
        HTTPException: 400 if validation fails, 401 if unauthorized, 500 if processing fails
    """
    # Input validation
    if not chat_request.message or not chat_request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="I didn't catch that. What would you like to do with your tasks?"
        )

    if len(chat_request.message) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That message is too long. Please use fewer than 5000 characters."
        )

    try:
        # Extract JWT token for MCP authentication
        jwt_token = extract_jwt_token(request)

        # Get or create conversation
        if chat_request.conversation_id:
            # Verify user owns this conversation
            from src.services.conversation_service import verify_user_owns_conversation

            is_owner = await verify_user_owns_conversation(
                session=session,
                conversation_id=chat_request.conversation_id,
                user_id=current_user.user_id
            )

            if not is_owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or access denied"
                )

            conversation_id = chat_request.conversation_id

        else:
            # Create new conversation with auto-generated title from first message
            title = chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message

            conversation = await create_conversation(
                session=session,
                user_id=current_user.user_id,
                title=title
            )
            conversation_id = conversation.id

        # Get conversation history for context
        history = await get_conversation_messages(
            session=session,
            conversation_id=conversation_id,
            limit=100
        )

        # Persist user message
        user_message = await add_message(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            role=MessageRole.USER,
            content=chat_request.message,
            tool_calls=None
        )

        # Process message through AI agent
        agent_service = await get_agent_service()

        agent_result = await agent_service.process_user_message(
            user_message=chat_request.message,
            conversation_history=history,
            user_id=current_user.user_id,
            jwt_token=jwt_token,
            session=session
        )

        # Prepare tool_calls for persistence
        tool_calls_json = None
        tool_calls_list = []

        if agent_result.get("tool_calls"):
            tool_calls_json = {"calls": agent_result["tool_calls"]}
            tool_calls_list = [
                ToolCall(
                    tool=tc["tool"],
                    parameters=tc["parameters"],
                    result=tc["result"]
                )
                for tc in agent_result["tool_calls"]
            ]

        # Persist agent response
        assistant_message = await add_message(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            role=MessageRole.ASSISTANT,
            content=agent_result["content"],
            tool_calls=tool_calls_json
        )

        # Build response
        response = ChatResponse(
            conversation_id=conversation_id,
            user_message=MessageSchema(
                id=user_message.id,
                role="user",
                content=user_message.content,
                tool_calls=None,
                created_at=user_message.created_at
            ),
            agent_response=MessageSchema(
                id=assistant_message.id,
                role="assistant",
                content=assistant_message.content,
                tool_calls=tool_calls_list if tool_calls_list else None,
                created_at=assistant_message.created_at
            )
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Handle database and unexpected errors
        import logging
        from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError

        logging.error(f"Chat endpoint error: {str(e)}", exc_info=True)

        # Check if it's a database error
        if isinstance(e, (SQLAlchemyError, DBAPIError, OperationalError)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="I'm having trouble connecting to the database. This might be temporary. Please try again in a moment."
            )

        # General error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again."
        )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's conversations",
    description="""
    Retrieve a paginated list of all conversations owned by the authenticated user.

    **Ordering:**
    - Conversations are ordered by most recent activity (updated_at DESC)
    - Most recently active conversations appear first

    **Pagination:**
    - Use `limit` and `offset` for pagination
    - Returns total count for calculating total pages
    - Default: 50 conversations per page

    **Response includes:**
    - Conversation ID and title
    - Creation and last update timestamps
    - Message count for each conversation

    **Use Cases:**
    - Display conversation list in UI
    - Allow user to select previous conversation
    - Show conversation history
    """,
    responses={
        200: {
            "description": "List of conversations with pagination info",
            "content": {
                "application/json": {
                    "example": {
                        "conversations": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "title": "Add a task to buy groceries...",
                                "created_at": "2024-01-17T12:00:00Z",
                                "updated_at": "2024-01-17T12:05:00Z",
                                "message_count": 4
                            }
                        ],
                        "total": 1,
                        "limit": 50,
                        "offset": 0
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve conversations"}
    }
)
async def list_user_conversations(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(default=0, ge=0, description="Number of conversations to skip"),
    current_user: TokenUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List user's conversations with pagination.

    This endpoint retrieves all conversations owned by the authenticated user,
    ordered by last update (most recent first).

    Args:
        limit: Maximum number of conversations to return (1-100, default 50)
        offset: Number of conversations to skip for pagination (default 0)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationListResponse with conversations, total count, and pagination info

    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        # Get user's conversations with total count
        conversations, total = await list_conversations(
            session=session,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset
        )

        # Convert to schemas with message counts
        conversation_summaries = []
        for conv in conversations:
            # Count messages for this conversation
            count_query = select(func.count(Message.id)).where(
                Message.conversation_id == conv.id
            )
            count_result = await session.exec(count_query)
            message_count = count_result.one()

            conversation_summaries.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title or "Untitled Conversation",
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count
                )
            )

        return ConversationListResponse(
            conversations=conversation_summaries,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        import logging
        logging.error(f"List conversations error: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations. Please try again."
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
    description="""
    Retrieve full conversation details including all messages in chronological order.

    **Authorization:**
    - User must own the conversation
    - Returns 403 if user doesn't own conversation
    - Returns 404 if conversation doesn't exist

    **Message Ordering:**
    - Messages returned in chronological order (oldest first)
    - Allows reconstructing conversation flow

    **Pagination:**
    - Use `limit` and `offset` for large conversations
    - Default: 100 messages per request
    - Maximum: 500 messages per request

    **Response includes:**
    - Conversation metadata (ID, title, timestamps)
    - All messages with role, content, and tool calls
    - Tool invocation details for agent responses

    **Use Cases:**
    - Display conversation history in chat UI
    - Resume previous conversation with context
    - Review agent's tool invocations
    """,
    responses={
        200: {
            "description": "Conversation details with messages",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Add a task to buy groceries...",
                        "created_at": "2024-01-17T12:00:00Z",
                        "updated_at": "2024-01-17T12:05:00Z",
                        "messages": [
                            {
                                "id": "234e5678-e89b-12d3-a456-426614174001",
                                "role": "user",
                                "content": "Add a task to buy groceries",
                                "tool_calls": None,
                                "created_at": "2024-01-17T12:00:00Z"
                            },
                            {
                                "id": "345e6789-e89b-12d3-a456-426614174002",
                                "role": "assistant",
                                "content": "I've added 'Buy groceries' to your task list!",
                                "tool_calls": [
                                    {
                                        "tool": "add_task",
                                        "parameters": {"title": "Buy groceries"},
                                        "result": {"success": True}
                                    }
                                ],
                                "created_at": "2024-01-17T12:00:01Z"
                            }
                        ]
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        403: {"description": "Access denied: You do not own this conversation"},
        404: {"description": "Conversation not found"},
        500: {"description": "Failed to retrieve conversation"}
    }
)
async def get_conversation_detail(
    conversation_id: UUID,
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of messages to return"),
    offset: int = Query(default=0, ge=0, description="Number of messages to skip"),
    current_user: TokenUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retrieve conversation details with all messages.

    This endpoint fetches a conversation and its messages with user authorization.
    Messages are returned in chronological order (oldest first).

    Args:
        conversation_id: UUID of the conversation to retrieve
        limit: Maximum number of messages to return (1-500, default 100)
        offset: Number of messages to skip for pagination (default 0)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationDetail with conversation metadata and messages

    Raises:
        HTTPException: 403 if user doesn't own conversation, 404 if not found
    """
    try:
        # Verify user owns this conversation
        is_owner = await verify_user_owns_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.user_id
        )

        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this conversation"
            )

        # Get conversation
        conversation = await get_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        messages = await get_conversation_messages(
            session=session,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )

        # Convert to schema
        message_schemas = []
        for msg in messages:
            tool_calls_list = None
            if msg.tool_calls and "calls" in msg.tool_calls:
                tool_calls_list = [
                    ToolCall(
                        tool=tc["tool"],
                        parameters=tc.get("parameters", {}),
                        result=tc.get("result", {})
                    )
                    for tc in msg.tool_calls["calls"]
                ]

            message_schemas.append(
                MessageSchema(
                    id=msg.id,
                    role=msg.role.value,
                    content=msg.content,
                    tool_calls=tool_calls_list,
                    created_at=msg.created_at
                )
            )

        return ConversationDetail(
            id=conversation.id,
            title=conversation.title or "Untitled Conversation",
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=message_schemas
        )

    except HTTPException:
        raise

    except Exception as e:
        import logging
        logging.error(f"Get conversation detail error: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation. Please try again."
        )
