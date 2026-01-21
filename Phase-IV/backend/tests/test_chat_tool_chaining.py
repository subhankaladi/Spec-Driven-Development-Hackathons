"""Integration tests for User Story 3: Tool Chaining.

These tests verify that the AI agent can chain multiple tools together
for complex requests like "list and delete" or "show and update".
"""

import pytest
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
TEST_DATABASE_URL = "sqlite:///./test_chat_tool_chaining.db"
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


class TestChatToolChaining:
    """Integration tests for US3: Tool Chaining."""

    @pytest.mark.asyncio
    async def test_agent_chains_list_and_delete_tasks(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: User sends 'List my tasks and delete all the completed ones'.

        Expected:
        - Agent calls list_tasks to get task list
        - Identifies 2 completed tasks
        - Calls delete_task for each completed task
        - Final response shows: Deleted 2 tasks, 3 tasks remaining
        """
        task1_id = str(uuid4())
        task2_id = str(uuid4())
        task3_id = str(uuid4())
        task4_id = str(uuid4())
        task5_id = str(uuid4())

        # Mock OpenAI API response - first call to interpret intent
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        # First tool call: list_tasks
                        Mock(
                            id="call_list",
                            function=Mock(
                                name="list_tasks",
                                arguments='{}'
                            )
                        ),
                        # Second tool call: delete first completed task
                        Mock(
                            id="call_delete1",
                            function=Mock(
                                name="delete_task",
                                arguments=f'{{"task_id": "{task1_id}"}}'
                            )
                        ),
                        # Third tool call: delete second completed task
                        Mock(
                            id="call_delete2",
                            function=Mock(
                                name="delete_task",
                                arguments=f'{{"task_id": "{task3_id}"}}'
                            )
                        ),
                    ]
                )
            )
        ]

        # Mock final response after tool execution
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I've deleted 2 completed tasks. You have 3 tasks remaining."
                )
            )
        ]

        # Mock MCP server responses
        mock_list_response = {
            "tasks": [
                {"id": task1_id, "title": "Task 1", "is_completed": True},
                {"id": task2_id, "title": "Task 2", "is_completed": False},
                {"id": task3_id, "title": "Task 3", "is_completed": True},
                {"id": task4_id, "title": "Task 4", "is_completed": False},
                {"id": task5_id, "title": "Task 5", "is_completed": False},
            ],
            "total": 5,
            "page": 1,
            "page_size": 20
        }

        mock_delete_response = {
            "message": "Task deleted successfully"
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

                # Setup different responses for different endpoints
                async def mock_post(url, json=None):
                    mock_response = AsyncMock()
                    mock_response.raise_for_status = Mock()

                    if "/list_tasks" in url:
                        mock_response.json.return_value = mock_list_response
                    elif "/delete_task" in url:
                        mock_response.json.return_value = mock_delete_response

                    return mock_response

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "List my tasks and delete all the completed ones"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check agent response mentions deletion
        assert data["agent_response"]["role"] == "assistant"
        agent_content = data["agent_response"]["content"].lower()
        assert "deleted" in agent_content or "2" in agent_content

        # Check tool calls - should have list_tasks and 2 delete_task calls
        assert data["agent_response"]["tool_calls"] is not None
        tool_calls = data["agent_response"]["tool_calls"]
        assert len(tool_calls) >= 2  # At least list and one delete

        # Verify list_tasks was called
        tool_names = [tc["tool"] for tc in tool_calls]
        assert "list_tasks" in tool_names

        # Verify delete_task was called
        assert "delete_task" in tool_names

    @pytest.mark.asyncio
    async def test_agent_chains_list_and_update_tasks(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: User sends 'Show me my important tasks and mark them as urgent'.

        Expected:
        - Agent calls list_tasks
        - Filters for important tasks
        - Calls update_task for each important task
        - Final response confirms updates
        """
        task1_id = str(uuid4())
        task2_id = str(uuid4())

        # Mock OpenAI API response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        # First tool call: list_tasks
                        Mock(
                            id="call_list",
                            function=Mock(
                                name="list_tasks",
                                arguments='{}'
                            )
                        ),
                        # Second tool call: update first important task
                        Mock(
                            id="call_update1",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task1_id}", "description": "URGENT"}}'
                            )
                        ),
                        # Third tool call: update second important task
                        Mock(
                            id="call_update2",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task2_id}", "description": "URGENT"}}'
                            )
                        ),
                    ]
                )
            )
        ]

        # Mock final response
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I've marked 2 important tasks as urgent."
                )
            )
        ]

        # Mock MCP responses
        mock_list_response = {
            "tasks": [
                {"id": task1_id, "title": "Important: Fix bug", "is_completed": False},
                {"id": task2_id, "title": "Important: Deploy feature", "is_completed": False},
            ],
            "total": 2,
            "page": 1,
            "page_size": 20
        }

        mock_update_response = {
            "id": task1_id,
            "title": "Important: Fix bug",
            "description": "URGENT",
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

                async def mock_post(url, json=None):
                    mock_response = AsyncMock()
                    mock_response.raise_for_status = Mock()

                    if "/list_tasks" in url:
                        mock_response.json.return_value = mock_list_response
                    elif "/update_task" in url:
                        mock_response.json.return_value = mock_update_response

                    return mock_response

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Show me my important tasks and mark them as urgent"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check tool calls
        assert data["agent_response"]["tool_calls"] is not None
        tool_calls = data["agent_response"]["tool_calls"]

        # Verify list_tasks and update_task were called
        tool_names = [tc["tool"] for tc in tool_calls]
        assert "list_tasks" in tool_names
        assert "update_task" in tool_names

        # Verify agent confirms action
        agent_content = data["agent_response"]["content"].lower()
        assert "marked" in agent_content or "urgent" in agent_content

    @pytest.mark.asyncio
    async def test_partial_tool_failure_continues_execution(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: Tool chaining continues even if one tool fails.

        Scenario: User says 'Update tasks A, B, and C to high priority'
        - Task A update succeeds
        - Task B update fails (AUTHORIZATION_ERROR)
        - Task C update succeeds
        Expected: Execution continues, final response summarizes results
        """
        task_a_id = str(uuid4())
        task_b_id = str(uuid4())
        task_c_id = str(uuid4())

        # Mock OpenAI API response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_update_a",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task_a_id}", "description": "High priority"}}'
                            )
                        ),
                        Mock(
                            id="call_update_b",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task_b_id}", "description": "High priority"}}'
                            )
                        ),
                        Mock(
                            id="call_update_c",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{task_c_id}", "description": "High priority"}}'
                            )
                        ),
                    ]
                )
            )
        ]

        # Mock final response with partial success
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I've updated 2 tasks to high priority. One task wasn't accessible."
                )
            )
        ]

        with patch("src.services.agent_service.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = [
                mock_openai_response,
                mock_final_response
            ]
            mock_openai_class.return_value = mock_client

            with patch("httpx.AsyncClient") as mock_httpx:
                mock_http_client = AsyncMock()

                call_count = [0]

                async def mock_post(url, json=None):
                    mock_response = AsyncMock()

                    if "/update_task" in url:
                        call_count[0] += 1
                        # Second call fails (task B)
                        if call_count[0] == 2:
                            mock_response.raise_for_status = Mock(
                                side_effect=Exception("AUTHORIZATION_ERROR: Task not found")
                            )
                            # Simulate HTTP error
                            import httpx
                            raise httpx.HTTPStatusError(
                                "403 Forbidden",
                                request=Mock(url=url),
                                response=Mock(status_code=403, text='{"error": "AUTHORIZATION_ERROR"}', json=lambda: {"error": "AUTHORIZATION_ERROR"})
                            )
                        else:
                            mock_response.raise_for_status = Mock()
                            mock_response.json.return_value = {
                                "id": json.get("task_id"),
                                "description": "High priority"
                            }

                    return mock_response

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": f"Update tasks {task_a_id}, {task_b_id}, and {task_c_id} to high priority"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check that execution continued despite failure
        assert data["agent_response"]["tool_calls"] is not None
        tool_calls = data["agent_response"]["tool_calls"]

        # Should have 3 tool calls (even though one failed)
        assert len(tool_calls) == 3

        # Verify some calls succeeded and some failed
        success_count = sum(1 for tc in tool_calls if tc.get("result", {}).get("success") != False)
        failure_count = sum(1 for tc in tool_calls if tc.get("result", {}).get("success") == False or "error" in tc.get("result", {}))

        # At least one should succeed and one should fail
        assert success_count >= 1
        assert failure_count >= 1
