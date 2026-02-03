"""Integration tests for User Story 4: Error Handling.

These tests verify that the AI agent provides user-friendly error messages
and handles edge cases gracefully.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.exc import OperationalError

from src.main import app
from src.models.database import get_session
from src.models.user import User
from src.models.conversation import Conversation, Message, MessageRole
from src.services.auth_service import auth_service


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_chat_error_handling.db"
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


class TestChatErrorHandling:
    """Integration tests for US4: Error Handling."""

    def test_empty_message_handling(self, client: TestClient, auth_token: str):
        """Test: POST /api/chat with empty message ('').

        Expected:
        - Returns 400 Bad Request
        - User-friendly message: 'I didn't catch that. What would you like to do with your tasks?'
        """
        # Send empty message
        response = client.post(
            "/api/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "didn't catch that" in data["detail"].lower()

    def test_whitespace_only_message_handling(self, client: TestClient, auth_token: str):
        """Test: POST /api/chat with whitespace-only message.

        Expected:
        - Returns 400 Bad Request
        - User-friendly message about empty input
        """
        # Send whitespace-only message
        response = client.post(
            "/api/chat",
            json={"message": "   \n\t   "},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "didn't catch that" in data["detail"].lower()

    def test_message_too_long_handling(self, client: TestClient, auth_token: str):
        """Test: POST /api/chat with message > 5000 characters.

        Expected:
        - Returns 400 Bad Request
        - Message: 'That message is too long. Please use fewer than 5000 characters.'
        """
        # Create message longer than 5000 characters
        long_message = "a" * 5001

        response = client.post(
            "/api/chat",
            json={"message": long_message},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "too long" in data["detail"].lower()
        assert "5000" in data["detail"]

    def test_expired_token_handling(self, client: TestClient):
        """Test: Request with expired token.

        Expected:
        - Returns 401 Unauthorized
        - Message: 'Your session has expired. Please log in again.'
        """
        # Use invalid/expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        response = client.post(
            "/api/chat",
            json={"message": "Add a task"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Verify response
        assert response.status_code == 401
        data = response.json()
        assert "session has expired" in data["detail"].lower() or "log in again" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_unauthorized_access_friendly_message(
        self, client: TestClient, auth_token: str, test_user: User, session: Session
    ):
        """Test: User tries to access another user's conversation.

        Expected:
        - Returns 403 or 404
        - User-friendly message (not technical AUTHORIZATION_ERROR code)
        """
        # Create conversation for a different user
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            password=auth_service.get_password_hash("password123")
        )
        session.add(other_user)
        session.commit()

        other_conversation = Conversation(
            id=uuid4(),
            user_id=other_user.id,
            title="Other user's conversation"
        )
        session.add(other_conversation)
        session.commit()

        # Try to access other user's conversation
        response = client.get(
            f"/api/chat/{other_conversation.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Verify response
        assert response.status_code in [403, 404]
        data = response.json()

        # Should not contain technical error codes
        detail = data["detail"].lower()
        assert "authorization_error" not in detail
        assert "forbidden" not in detail or "access denied" in detail

    @pytest.mark.asyncio
    async def test_invalid_task_id_friendly_message(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: Agent calls update_task with invalid task_id.

        Expected:
        - MCP returns NOT_FOUND_ERROR
        - Translated to: 'I couldn't find that task'
        - No technical error codes exposed to user
        """
        invalid_task_id = str(uuid4())

        # Mock OpenAI API response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_update",
                            function=Mock(
                                name="update_task",
                                arguments=f'{{"task_id": "{invalid_task_id}", "title": "Updated"}}'
                            )
                        )
                    ]
                )
            )
        ]

        # Mock final response with user-friendly error
        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I couldn't find that task. Could you show me your task list first?"
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

                # Simulate NOT_FOUND error from MCP
                import httpx
                async def mock_post(url, json=None):
                    raise httpx.HTTPStatusError(
                        "404 Not Found",
                        request=Mock(url=url),
                        response=Mock(
                            status_code=404,
                            text='{"error": "NOT_FOUND_ERROR: Task not found"}',
                            json=lambda: {"error": "NOT_FOUND_ERROR: Task not found"}
                        )
                    )

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Update my task"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Agent should handle error gracefully
        agent_content = data["agent_response"]["content"].lower()

        # Should NOT contain technical error codes
        assert "not_found_error" not in agent_content
        assert "404" not in agent_content

        # Should contain user-friendly message
        assert "couldn't find" in agent_content or "not found" in agent_content or "can't find" in agent_content

    @pytest.mark.asyncio
    async def test_database_error_user_guidance(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: Database connection failure.

        Expected:
        - Returns 500 Internal Server Error
        - Message: 'I'm having trouble connecting to the database. This might be temporary. Please try again in a moment.'
        - No technical implementation details exposed
        """
        # Mock database error in conversation service
        with patch("src.services.conversation_service.create_conversation") as mock_create:
            mock_create.side_effect = OperationalError(
                "could not connect to server",
                params=None,
                orig=None
            )

            with patch("src.services.agent_service.OpenAI") as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Add a task"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 500
        data = response.json()

        # Should contain user-friendly database error message
        detail = data["detail"].lower()
        assert "database" in detail or "try again" in detail

        # Should NOT contain technical error details
        assert "operationalerror" not in detail
        assert "could not connect to server" not in detail

    @pytest.mark.asyncio
    async def test_tool_execution_partial_failure_aggregation(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: Multiple tools called, some succeed, some fail.

        Scenario: Update 3 tasks - A succeeds, B fails, C succeeds
        Expected:
        - Execution continues for all tasks
        - Final response aggregates: 'Updated 2 tasks. One task wasn't accessible.'
        - Clear summary without technical errors
        """
        task_a_id = str(uuid4())
        task_b_id = str(uuid4())
        task_c_id = str(uuid4())

        # Mock OpenAI responses
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(id="call_a", function=Mock(name="update_task", arguments=f'{{"task_id": "{task_a_id}"}}')),
                        Mock(id="call_b", function=Mock(name="update_task", arguments=f'{{"task_id": "{task_b_id}"}}')),
                        Mock(id="call_c", function=Mock(name="update_task", arguments=f'{{"task_id": "{task_c_id}"}}')),
                    ]
                )
            )
        ]

        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="I've updated 2 tasks. One task wasn't accessible."
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
                    call_count[0] += 1
                    mock_response = AsyncMock()

                    # Second call fails
                    if call_count[0] == 2:
                        import httpx
                        raise httpx.HTTPStatusError(
                            "403 Forbidden",
                            request=Mock(url=url),
                            response=Mock(
                                status_code=403,
                                text='{"error": "AUTHORIZATION_ERROR"}',
                                json=lambda: {"error": "AUTHORIZATION_ERROR"}
                            )
                        )

                    mock_response.raise_for_status = Mock()
                    mock_response.json.return_value = {"id": json.get("task_id"), "title": "Updated"}
                    return mock_response

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Update all my tasks"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check agent aggregated results
        agent_content = data["agent_response"]["content"].lower()
        assert "2" in agent_content or "two" in agent_content
        assert "updated" in agent_content

        # Should have user-friendly error handling
        assert "authorization_error" not in agent_content
        assert "403" not in agent_content

    def test_missing_auth_token_handling(self, client: TestClient):
        """Test: Request without authentication token.

        Expected:
        - Returns 401 Unauthorized
        - Clear message about authentication
        """
        # Send request without auth header
        response = client.post(
            "/api/chat",
            json={"message": "Add a task"}
        )

        # Verify response
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_malformed_request_body(self, client: TestClient, auth_token: str):
        """Test: Request with missing required field.

        Expected:
        - Returns 422 Unprocessable Entity (FastAPI validation)
        - Clear validation error
        """
        # Send request without 'message' field
        response = client.post(
            "/api/chat",
            json={},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Verify response
        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_error_translation_layer_authentication_error(
        self, client: TestClient, auth_token: str, test_user: User
    ):
        """Test: Error translation for AUTHENTICATION_ERROR from MCP.

        Expected:
        - MCP returns AUTHENTICATION_ERROR
        - Translated to: 'Your authentication token expired. Please log in again.'
        """
        # Mock OpenAI response
        mock_openai_response = Mock()
        mock_openai_response.choices = [
            Mock(
                message=Mock(
                    content=None,
                    tool_calls=[
                        Mock(
                            id="call_list",
                            function=Mock(name="list_tasks", arguments='{}')
                        )
                    ]
                )
            )
        ]

        mock_final_response = Mock()
        mock_final_response.choices = [
            Mock(
                message=Mock(
                    content="Your authentication token expired. Please log in again."
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

                # Simulate AUTHENTICATION_ERROR from MCP
                import httpx
                async def mock_post(url, json=None):
                    raise httpx.HTTPStatusError(
                        "401 Unauthorized",
                        request=Mock(url=url),
                        response=Mock(
                            status_code=401,
                            text='{"error": "AUTHENTICATION_ERROR: Token expired"}',
                            json=lambda: {"error": "AUTHENTICATION_ERROR: Token expired"}
                        )
                    )

                mock_http_client.post = mock_post
                mock_http_client.__aenter__.return_value = mock_http_client
                mock_http_client.__aexit__.return_value = None
                mock_httpx.return_value = mock_http_client

                # Send chat message
                response = client.post(
                    "/api/chat",
                    json={"message": "Show my tasks"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check error was translated to user-friendly message
        agent_content = data["agent_response"]["content"].lower()
        assert "authentication_error" not in agent_content
        assert "401" not in agent_content
        assert ("expired" in agent_content or "log in" in agent_content)
