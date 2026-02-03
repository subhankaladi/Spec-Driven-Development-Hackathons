"""Integration tests for User Story 1: Natural Language Task Management.

These tests verify end-to-end functionality of the AI Agent Chat API,
including natural language processing, MCP tool invocation, and task management.
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from src.main import app
from src.models.database import get_session
from src.models.user import User
from src.models.conversation import Conversation, Message, MessageRole
from src.services.auth_service import auth_service


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_chat.db"
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


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create authentication token for test user."""
    token = auth_service.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return token


@pytest.fixture(name="client")
def client_fixture():
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestChatIntegrationUS1:
    """Integration tests for US1: Natural Language Task Management."""

    @pytest.mark.asyncio
    async def test_end_to_end_add_task_via_chat(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: User sends 'Add a task to buy groceries' and task is created.

        Expected:
        - Task created in MCP with title 'buy groceries'
        - Response has conversation_id, user_message, agent_response
        - Agent response confirms action
        - Tool call recorded with add_task
        """
        # Mock OpenAI API response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_123",
                            function=Mock(
                                name="add_task",
                                arguments='{"title": "Buy groceries"}'
                            )
                        )
                    ]
                )
            )
        ]

        # Mock final response after tool execution
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I've added 'Buy groceries' to your task list!"
                )
            )
        ]

        # Mock MCP server response
        mock_mcp_response = {
            "id": str(uuid4()),
            "user_id": str(test_user.id),
            "title": "Buy groceries",
            "description": None,
            "is_completed": False,
            "created_at": "2026-01-17T12:00:00",
            "updated_at": "2026-01-17T12:00:00"
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

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Add a task to buy groceries"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check conversation created
        assert "conversation_id" in data
        assert data["conversation_id"] is not None

        # Check user message
        assert data["user_message"]["role"] == "user"
        assert "buy groceries" in data["user_message"]["content"].lower()

        # Check agent response
        assert data["agent_response"]["role"] == "assistant"
        assert "added" in data["agent_response"]["content"].lower()

        # Check tool calls
        assert data["agent_response"]["tool_calls"] is not None
        assert len(data["agent_response"]["tool_calls"]) > 0
        tool_call = data["agent_response"]["tool_calls"][0]
        assert tool_call["tool"] == "add_task"
        assert "title" in tool_call["parameters"]

    @pytest.mark.asyncio
    async def test_agent_interprets_list_tasks_intent(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: User sends 'Show me my tasks' and agent calls list_tasks.

        Expected:
        - Agent calls list_tasks tool
        - Response includes task list from agent
        """
        # Mock OpenAI API response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_456",
                            function=Mock(
                                name="list_tasks",
                                arguments='{"completed": false}'
                            )
                        )
                    ]
                )
            )
        ]

        # Mock final response
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="Here are your tasks:\n1. Buy groceries\n2. Walk the dog"
                )
            )
        ]

        # Mock MCP server response
        mock_mcp_response = {
            "items": [
                {
                    "id": str(uuid4()),
                    "title": "Buy groceries",
                    "is_completed": False
                },
                {
                    "id": str(uuid4()),
                    "title": "Walk the dog",
                    "is_completed": False
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
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

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Show me my tasks"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check tool call
        assert data["agent_response"]["tool_calls"] is not None
        tool_call = data["agent_response"]["tool_calls"][0]
        assert tool_call["tool"] == "list_tasks"

        # Check agent response mentions tasks
        assert "tasks" in data["agent_response"]["content"].lower()

    @pytest.mark.asyncio
    async def test_agent_interprets_complete_task_intent(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: User sends 'Mark the grocery task as done' and agent completes task.

        Expected:
        - Agent identifies task and calls complete_task
        - Task marked complete in MCP
        """
        task_id = str(uuid4())

        # Mock OpenAI responses (two calls: list to find task, then complete)
        mock_list_response = Mock()
        mock_list_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_789",
                            function=Mock(
                                name="list_tasks",
                                arguments='{"completed": false}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_complete_response = Mock()
        mock_complete_response.choices = [
            Mock(
                message=Mock(
                    content="Great! I've marked 'Buy groceries' as completed."
                )
            )
        ]

        # Mock MCP server responses
        mock_list_mcp_response = {
            "items": [
                {
                    "id": task_id,
                    "title": "Buy groceries",
                    "is_completed": False
                }
            ],
            "total": 1
        }

        mock_complete_mcp_response = {
            "id": task_id,
            "title": "Buy groceries",
            "is_completed": True
        }

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_list_response,
                mock_complete_response
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()

                # Mock different responses for list and complete
                async def mock_post(*args, **kwargs):
                    mock_response = AsyncMock()
                    url = args[0] if args else kwargs.get("url", "")

                    if "list_tasks" in url:
                        mock_response.json.return_value = mock_list_mcp_response
                    else:
                        mock_response.json.return_value = mock_complete_mcp_response

                    mock_response.raise_for_status = Mock()
                    return mock_response

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Mark the grocery task as done"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check tool calls include list_tasks
        assert data["agent_response"]["tool_calls"] is not None
        tool_names = [tc["tool"] for tc in data["agent_response"]["tool_calls"]]
        assert "list_tasks" in tool_names

        # Check agent confirms completion
        assert any(
            word in data["agent_response"]["content"].lower()
            for word in ["marked", "completed", "done"]
        )

    @pytest.mark.asyncio
    async def test_conversation_persistence(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: Verify conversation and messages are persisted correctly.

        Expected:
        - Conversation created in database
        - User and assistant messages persisted
        - Tool calls stored in message.tool_calls JSON
        """
        # Mock OpenAI and MCP as in previous tests
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_abc",
                            function=Mock(
                                name="add_task",
                                arguments='{"title": "Test task"}'
                            )
                        )
                    ]
                )
            )
        ]

        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(message=Mock(content="Task added!"))
        ]

        mock_mcp_response = {
            "id": str(uuid4()),
            "title": "Test task",
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
                    json={"message": "Add a test task"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify conversation in database
        from sqlmodel import select
        conversation = session.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        ).first()

        assert conversation is not None
        assert conversation.user_id == test_user.id

        # Verify messages in database
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        assert len(messages) == 2

        # Check user message
        user_msg = messages[0]
        assert user_msg.role == MessageRole.USER
        assert "test task" in user_msg.content.lower()
        assert user_msg.tool_calls is None

        # Check assistant message
        assistant_msg = messages[1]
        assert assistant_msg.role == MessageRole.ASSISTANT
        assert assistant_msg.tool_calls is not None
        assert "calls" in assistant_msg.tool_calls
        assert len(assistant_msg.tool_calls["calls"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
