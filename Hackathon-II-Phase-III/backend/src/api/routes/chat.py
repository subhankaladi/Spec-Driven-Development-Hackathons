import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.utils.errors import create_error_response
from src.auth.dependencies import get_user_id_from_path
from src.chat.agent import run_chat_agent
from src.chat.persistence import append_message, load_or_create_conversation, get_conversation_history
from src.chat.schemas import ChatRequest, ChatResponse
from src.database.session import get_session


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user_id: str = Depends(get_user_id_from_path),
    session: Session = Depends(get_session),
) -> ChatResponse:
    try:
        logger.info(f"Processing chat request for user {user_id}")

        # Verify that the authenticated user ID matches the path user ID
        # (This is handled by the get_user_id_from_path dependency)

        convo = load_or_create_conversation(session, user_id)
        logger.debug(f"Loaded/created conversation {convo.id} for user {user_id}")

        # Get conversation history for context (implementing US2 - resume conversation after restart)
        history = get_conversation_history(session, convo.id)
        logger.debug(f"Fetched {len(history)} history messages for conversation {convo.id}")

        # Append user message to conversation before running agent
        user_msg = append_message(session, convo.id, role="user", content=payload.message)
        logger.debug(f"Saved user message to conversation {convo.id}")

        # Run the agent to process the request with conversation history context
        agent_response = await run_chat_agent(
            user_id=user_id,
            conversation_id=str(convo.id),
            user_message=payload.message,
            history=history  # Pass history for context-aware responses
        )

        # Save the assistant's response to the conversation
        assistant_msg = append_message(session, convo.id, role="assistant", content=agent_response["response_text"])
        logger.debug(f"Saved assistant response to conversation {convo.id}")

        logger.info(f"Successfully processed chat request for user {user_id}, conversation {convo.id}")

        return ChatResponse(
            conversation_id=agent_response["conversation_id"],
            assistant_message=agent_response["response_text"]
        )
    except HTTPException:
        logger.warning(f"HTTP exception in chat for user {user_id}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat for user {user_id}: {e}", exc_info=True)
        # Standardize error response format to match backend/src/api/main.py:create_error_response
        raise HTTPException(status_code=500, detail=str(e))
