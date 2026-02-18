"""Integration tests for User Story 2: Multi-Turn Conversation & State Reconstruction.

These tests verify:
- Multi-turn conversation with full context reconstruction
- Conversation history retrieval in chronological order
- Stateless behavior (all state in PostgreSQL)
- User authorization and isolation
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select

from src.main import app
from src.models.database import get_session
from src.models.user import User
from src.models.conversation import Conversation, Message, MessageRole
from src.services.auth_service import auth_service


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_conversation_persistence.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


def get_test_session():
    """Override database session for testing."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="session")
def session_fixture():
    """Create test database tables and provide session."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password=auth_service.get_password_hash("password123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="different_user")
def different_user_fixture(session: Session):
    """Create different test user for isolation tests."""
    user = User(
        id=uuid4(),
        email="other@example.com",
        password=auth_service.get_password_hash("otherpass456")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create authentication token for test user."""
    token = auth_service.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return token


@pytest.fixture(name="different_auth_token")
def different_auth_token_fixture(different_user: User):
    """Create authentication token for different user."""
    token = auth_service.create_access_token(
        data={"sub": str(different_user.id), "email": different_user.email}
    )
    return token


@pytest.fixture(name="client")
def client_fixture():
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_conversation")
def test_conversation_fixture(session: Session, test_user: User):
    """Create a test conversation with multiple messages."""
    conversation = Conversation(
        id=uuid4(),
        user_id=test_user.id,
        title="Test Conversation"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@pytest.fixture(name="test_messages")
def test_messages_fixture(session: Session, test_conversation: Conversation, test_user: User):
    """Create test messages in chronological order."""
    messages = [
        Message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Add a task to buy groceries"
        ),
        Message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="I've added the task 'Buy groceries' for you.",
            tool_calls={"calls": [{"tool": "add_task", "parameters": {"title": "Buy groceries"}, "result": {"id": str(uuid4())}}]}
        ),
        Message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Make it high priority"
        ),
        Message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="I've updated the task to high priority.",
            tool_calls={"calls": [{"tool": "update_task", "parameters": {"task_id": str(uuid4()), "priority": "high"}, "result": {"success": True}}]}
        ),
        Message(
            conversation_id=test_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Show me all high priority tasks"
        )
    ]

    for msg in messages:
        session.add(msg)
    session.commit()

    return messages


class TestConversationPersistenceUS2:
    """Integration tests for US2: Multi-Turn Conversation & State Reconstruction."""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_with_context(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test T033: Multi-turn conversation where agent uses context.

        Scenario:
        1. User: "Add a task to buy groceries tomorrow"
        2. User: "Make it high priority" (requires context from previous message)
        3. User: "Show me all high priority tasks" (requires context of modifications)

        Expected:
        - Agent uses full history to interpret "it" and "all high priority"
        - All 3 messages persisted with tool_calls
        - Agent response correctly interprets context
        """
        conversation_id = None

        # Message 1: Add task
        mock_openai_response_1 = Mock()
        mock_openai_response_1.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_1",
                            function=Mock(
                                name="add_task",
                                arguments='{"title": "Buy groceries tomorrow"}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_final_response_1 = Mock()
        mock_final_response_1.choices = [
            Mock(
                message=Mock(
                    content="I've added 'Buy groceries tomorrow' to your task list!"
                )
            )
        ]

        task_id = str(uuid4())
        mock_mcp_response_1 = {
            "id": task_id,
            "user_id": str(test_user.id),
            "title": "Buy groceries tomorrow",
            "is_completed": False
        }

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_openai_response_1,
                mock_final_response_1
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()
                mock_http_response = AsyncMock()
                mock_http_response.json.return_value = mock_mcp_response_1
                mock_http_response.raise_for_status = Mock()
                mock_http_client.post.return_value = mock_http_response
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                response = client.post(
                    "/api/chat",
                    json={"message": "Add a task to buy groceries tomorrow"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]
        assert data["agent_response"]["tool_calls"] is not None

        # Message 2: "Make it high priority" - requires context
        mock_openai_response_2 = Mock()
        mock_openai_response_2.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_2",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task_id}", "priority": "high"}}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_final_response_2 = Mock()
        mock_final_response_2.choices = [
            Mock(
                message=Mock(
                    content="I've updated the 'Buy groceries tomorrow' task to high priority."
                )
            )
        ]

        mock_mcp_response_2 = {
            "id": task_id,
            "title": "Buy groceries tomorrow",
            "priority": "high",
            "is_completed": False
        }

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_openai_response_2,
                mock_final_response_2
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()
                mock_http_response = AsyncMock()
                mock_http_response.json.return_value = mock_mcp_response_2
                mock_http_response.raise_for_status = Mock()
                mock_http_client.post.return_value = mock_http_response
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                response = client.post(
                    "/api/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Make it high priority"
                    },
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        # Verify agent understood context ("it" refers to the task)
        assert data["agent_response"]["tool_calls"] is not None
        assert data["agent_response"]["tool_calls"][0]["tool"] == "update_task"

        # Message 3: "Show me all high priority tasks"
        mock_openai_response_3 = Mock()
        mock_openai_response_3.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_3",
                            function=Mock(
                                name="list_tasks",
                                arguments='{"priority": "high"}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_final_response_3 = Mock()
        mock_final_response_3.choices = [
            Mock(
                message=Mock(
                    content="Here are your high priority tasks:\n1. Buy groceries tomorrow"
                )
            )
        ]

        mock_mcp_response_3 = {
            "items": [
                {
                    "id": task_id,
                    "title": "Buy groceries tomorrow",
                    "priority": "high",
                    "is_completed": False
                }
            ],
            "total": 1
        }

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_openai_response_3,
                mock_final_response_3
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()
                mock_http_response = AsyncMock()
                mock_http_response.json.return_value = mock_mcp_response_3
                mock_http_response.raise_for_status = Mock()
                mock_http_client.post.return_value = mock_http_response
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                response = client.post(
                    "/api/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Show me all high priority tasks"
                    },
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_response"]["tool_calls"] is not None
        assert data["agent_response"]["tool_calls"][0]["tool"] == "list_tasks"

        # Verify all messages persisted
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        # 3 user messages + 3 assistant messages = 6 total
        assert len(messages) == 6

        # Verify conversation updated_at was updated
        conversation = session.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        ).first()
        assert conversation is not None
        assert conversation.updated_at > conversation.created_at

    @pytest.mark.asyncio
    async def test_conversation_history_retrieved_correctly(
        self, client: TestClient, auth_token: str, test_user: User,
        session: Session, test_conversation: Conversation, test_messages: list[Message]
    ):
        """Test T034: Conversation history retrieved in correct chronological order.

        Expected:
        - All 5 messages returned in chronological order (created_at ASC)
        - Message roles are correct (user, assistant, user, assistant, user)
        - Tool calls present in assistant messages
        - Timestamps are in ascending order
        """
        response = client.get(
            f"/api/chat/{test_conversation.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify conversation details
        assert data["id"] == str(test_conversation.id)
        assert data["title"] == test_conversation.title

        # Verify messages
        messages = data["messages"]
        assert len(messages) == 5

        # Verify chronological order
        expected_roles = ["user", "assistant", "user", "assistant", "user"]
        for i, msg in enumerate(messages):
            assert msg["role"] == expected_roles[i]

        # Verify timestamps in ascending order
        timestamps = [msg["created_at"] for msg in messages]
        assert timestamps == sorted(timestamps)

        # Verify tool calls in assistant messages
        assert messages[1]["tool_calls"] is not None
        assert len(messages[1]["tool_calls"]) > 0
        assert messages[1]["tool_calls"][0]["tool"] == "add_task"

        assert messages[3]["tool_calls"] is not None
        assert len(messages[3]["tool_calls"]) > 0
        assert messages[3]["tool_calls"][0]["tool"] == "update_task"

        # Verify user messages have no tool calls
        assert messages[0]["tool_calls"] is None
        assert messages[2]["tool_calls"] is None
        assert messages[4]["tool_calls"] is None

    @pytest.mark.asyncio
    async def test_stateless_no_in_memory_storage(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test T031: Verify stateless behavior - no in-memory state loss.

        Expected:
        - Message persisted in database
        - No error on simulated restart (application is stateless)
        - All messages still present and in correct order after retrieval
        """
        # Create conversation and send message
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_stateless",
                            function=Mock(
                                name="add_task",
                                arguments='{"title": "Test stateless task"}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="Task added!"
                )
            )
        ]

        mock_mcp_response = {
            "id": str(uuid4()),
            "title": "Test stateless task",
            "is_completed": False
        }

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_openai_response,
                mock_final_response
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()
                mock_http_response = AsyncMock()
                mock_http_response.json.return_value = mock_mcp_response
                mock_http_response.raise_for_status = Mock()
                mock_http_client.post.return_value = mock_http_response
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                response = client.post(
                    "/api/chat",
                    json={"message": "Add a stateless test task"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify message persisted in database
        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()

        assert len(messages) == 2  # user + assistant

        # Simulate application health check (no errors should occur)
        health_response = client.get("/health")
        assert health_response.status_code == 200

        # Fetch conversation via GET endpoint to verify persistence
        get_response = client.get(
            f"/api/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert get_response.status_code == 200
        retrieved_data = get_response.json()

        # Verify all messages still present and in correct order
        assert len(retrieved_data["messages"]) == 2
        assert retrieved_data["messages"][0]["role"] == "user"
        assert retrieved_data["messages"][1]["role"] == "assistant"
        assert "stateless" in retrieved_data["messages"][0]["content"].lower()

    @pytest.mark.asyncio
    async def test_list_conversations_ordered_by_activity(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: GET /api/chat/conversations returns conversations by updated_at DESC.

        Expected:
        - Conversations ordered by most recent activity first
        - Pagination works correctly
        - Message counts are accurate
        """
        # Create multiple conversations with different update times
        conv1 = Conversation(
            id=uuid4(),
            user_id=test_user.id,
            title="Old Conversation",
            created_at=datetime(2026, 1, 1, 10, 0, 0),
            updated_at=datetime(2026, 1, 1, 10, 0, 0)
        )
        conv2 = Conversation(
            id=uuid4(),
            user_id=test_user.id,
            title="Recent Conversation",
            created_at=datetime(2026, 1, 15, 10, 0, 0),
            updated_at=datetime(2026, 1, 17, 14, 0, 0)  # Most recent
        )
        conv3 = Conversation(
            id=uuid4(),
            user_id=test_user.id,
            title="Middle Conversation",
            created_at=datetime(2026, 1, 10, 10, 0, 0),
            updated_at=datetime(2026, 1, 12, 10, 0, 0)
        )

        session.add(conv1)
        session.add(conv2)
        session.add(conv3)
        session.commit()

        # Add messages to conversations
        msg1 = Message(
            conversation_id=conv1.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Old message"
        )
        msg2 = Message(
            conversation_id=conv2.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Recent message 1"
        )
        msg3 = Message(
            conversation_id=conv2.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Recent message 2"
        )

        session.add(msg1)
        session.add(msg2)
        session.add(msg3)
        session.commit()

        # List conversations
        response = client.get(
            "/api/chat/conversations?limit=10&offset=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify conversations ordered by updated_at DESC
        conversations = data["conversations"]
        assert len(conversations) == 3

        # Most recent first
        assert conversations[0]["title"] == "Recent Conversation"
        assert conversations[0]["message_count"] == 2

        assert conversations[1]["title"] == "Middle Conversation"
        assert conversations[2]["title"] == "Old Conversation"
        assert conversations[2]["message_count"] == 1

        # Verify pagination info
        assert data["total"] == 3
        assert data["limit"] == 10
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_user_isolation_get_conversation(
        self, client: TestClient, auth_token: str, different_auth_token: str,
        test_user: User, different_user: User, session: Session
    ):
        """Test: User B cannot access User A's conversation.

        Expected:
        - User A creates conversation
        - User B tries GET /api/chat/{user-a-conversation-id}
        - Response: 403 Forbidden
        """
        # User A creates conversation
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user.id,
            title="User A's private conversation"
        )
        session.add(conversation)
        session.commit()

        # User B tries to access User A's conversation
        response = client.get(
            f"/api/chat/{conversation.id}",
            headers={"Authorization": f"Bearer {different_auth_token}"}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_conversation_pagination(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: Pagination works correctly for message retrieval.

        Expected:
        - limit and offset parameters control message retrieval
        - Messages returned in chronological order with pagination
        """
        # Create conversation with 10 messages
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user.id,
            title="Pagination Test"
        )
        session.add(conversation)
        session.commit()

        for i in range(10):
            msg = Message(
                conversation_id=conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}"
            )
            session.add(msg)
        session.commit()

        # Get first 5 messages
        response = client.get(
            f"/api/chat/{conversation.id}?limit=5&offset=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        messages = data["messages"]

        assert len(messages) == 5
        assert "Message 0" in messages[0]["content"]
        assert "Message 4" in messages[4]["content"]

        # Get next 5 messages
        response = client.get(
            f"/api/chat/{conversation.id}?limit=5&offset=5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        messages = data["messages"]

        assert len(messages) == 5
        assert "Message 5" in messages[0]["content"]
        assert "Message 9" in messages[4]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
