import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from jose import jwt
from src.api.main import app
from src.config.settings import settings
from src.database.session import create_db_and_tables, get_session
from src.models.task import Task, TaskCreate
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import patch


@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(name="session")
def fixture_session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(engine):
    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_test_token(user_id: str, expires_delta: timedelta = None):
    """Helper function to create a test JWT token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration_delta)

    to_encode = {"sub": user_id, "exp": expire.timestamp()}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


class TestAuthentication:
    """Test suite for authentication functionality."""

    def test_unauthenticated_access_returns_401(self, client):
        """Test that unauthenticated requests return 401 Unauthorized."""
        # Test GET /api/v1/tasks without token
        response = client.get("/api/v1/tasks")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
        assert response.json()["error_code"] == "AUTH_001"

        # Test POST /api/v1/tasks without token
        response = client.post("/api/v1/tasks", json={"title": "Test task"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
        assert response.json()["error_code"] == "AUTH_001"

        # Test GET /api/v1/tasks/{id} without token
        response = client.get("/api/v1/tasks/1")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
        assert response.json()["error_code"] == "AUTH_001"

        # Test PUT /api/v1/tasks/{id} without token
        response = client.put("/api/v1/tasks/1", json={"title": "Updated task"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
        assert response.json()["error_code"] == "AUTH_001"

        # Test DELETE /api/v1/tasks/{id} without token
        response = client.delete("/api/v1/tasks/1")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
        assert response.json()["error_code"] == "AUTH_001"

    def test_invalid_token_format_returns_401(self, client):
        """Test that requests with invalid token format return 401."""
        # Test with malformed token
        response = client.get("/api/v1/tasks", headers={"Authorization": "InvalidToken"})
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

        # Test with wrong scheme
        response = client.get("/api/v1/tasks", headers={"Authorization": "Basic some_token"})
        assert response.status_code == 401
        assert "Invalid authentication scheme" in response.json()["detail"]

        # Test with no token after scheme
        response = client.get("/api/v1/tasks", headers={"Authorization": "Bearer"})
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    def test_invalid_token_signature_returns_401(self, client):
        """Test that requests with invalid token signatures return 401."""
        # Create a token with a different secret to simulate invalid signature
        invalid_token = jwt.encode(
            {"sub": "user123", "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()},
            "different_secret",
            algorithm=settings.jwt_algorithm
        )
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {invalid_token}"})
        assert response.status_code == 401
        assert "Invalid token signature" in response.json()["detail"]

    def test_expired_token_returns_401(self, client):
        """Test that requests with expired tokens return 401."""
        expired_token = create_test_token("user123", expires_delta=timedelta(seconds=-1))
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_valid_token_allows_access(self, client, session):
        """Test that requests with valid tokens are allowed."""
        valid_token = create_test_token("user123")

        # Test GET /api/v1/tasks with valid token
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200
        assert response.json() == []

        # Test creating a task with valid token
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Test task", "description": "Test description"},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test task"
        assert response.json()["owner_id"] == "user123"

        task_id = response.json()["id"]

        # Test getting a specific task with valid token
        response = client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_cross_user_access_prevention(self, client, session):
        """Test that users cannot access other users' tasks."""
        user1_token = create_test_token("user1")
        user2_token = create_test_token("user2")

        # Create a task for user1
        response = client.post(
            "/api/v1/tasks",
            json={"title": "User1's task", "description": "Private task"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 201
        task_id = response.json()["id"]
        assert response.json()["owner_id"] == "user1"

        # Try to access user1's task with user2's token (should fail)
        response = client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user2_token}"})
        assert response.status_code == 404  # Task should not be found for user2

        # User1 should still be able to access their own task
        response = client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user1_token}"})
        assert response.status_code == 200
        assert response.json()["id"] == task_id
        assert response.json()["owner_id"] == "user1"

    def test_cross_user_modification_prevention(self, client, session):
        """Test that users cannot modify other users' tasks."""
        user1_token = create_test_token("user1")
        user2_token = create_test_token("user2")

        # Create a task for user1
        response = client.post(
            "/api/v1/tasks",
            json={"title": "User1's task", "description": "Private task"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 201
        task_id = response.json()["id"]
        assert response.json()["owner_id"] == "user1"

        # Try to update user1's task with user2's token (should fail)
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Hacked task"},
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 404  # Task should not be found for user2

        # Verify task is unchanged from user1's perspective
        response = client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user1_token}"})
        assert response.status_code == 200
        assert response.json()["title"] == "User1's task"  # Should not be "Hacked task"

    def test_cross_user_deletion_prevention(self, client, session):
        """Test that users cannot delete other users' tasks."""
        user1_token = create_test_token("user1")
        user2_token = create_test_token("user2")

        # Create a task for user1
        response = client.post(
            "/api/v1/tasks",
            json={"title": "User1's task", "description": "Private task"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 201
        task_id = response.json()["id"]
        assert response.json()["owner_id"] == "user1"

        # Try to delete user1's task with user2's token (should fail)
        response = client.delete(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user2_token}"})
        assert response.status_code == 404  # Task should not be found for user2

        # Verify task still exists from user1's perspective
        response = client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user1_token}"})
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_missing_user_id_in_token_returns_401(self, client):
        """Test that tokens without user ID (sub) return 401."""
        # Create a token without the 'sub' field
        token_without_user_id = jwt.encode(
            {"exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {token_without_user_id}"})
        assert response.status_code == 401
        assert "Invalid token: missing user ID" in response.json()["detail"]

    def test_malformed_jwt_returns_401(self, client):
        """Test that malformed JWT tokens return 401."""
        malformed_token = "this.is.not.a.valid.jwt.token"
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {malformed_token}"})
        assert response.status_code == 401
        assert "Invalid token signature" in response.json()["detail"]

    def test_token_validation_on_all_endpoints(self, client, session):
        """Test that all endpoints require valid tokens."""
        valid_token = create_test_token("user123")

        # Test all endpoints without token (should return 401)
        endpoints = [
            ("GET", "/api/v1/tasks"),
            ("POST", "/api/v1/tasks"),
            ("GET", "/api/v1/tasks/1"),
            ("PUT", "/api/v1/tasks/1"),
            ("DELETE", "/api/v1/tasks/1")
        ]

        for method, endpoint in endpoints:
            response = client.request(method, endpoint)
            assert response.status_code == 401, f"{method} {endpoint} should require authentication"

        # Test all endpoints with valid token (should work or return appropriate error)
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Test task"},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code in [201, 422]  # Success or validation error (not 401)

        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200  # Should be accessible with valid token


class TestTaskEndpointsWithAuth:
    """Test task endpoints specifically with authentication."""

    def test_create_task_with_authentication(self, client, session):
        """Test creating tasks with authenticated user."""
        token = create_test_token("test_user_123")

        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "This is a test task",
                "is_completed": False
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "This is a test task"
        assert data["is_completed"] is False
        assert data["owner_id"] == "test_user_123"  # Should be associated with authenticated user
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_all_tasks_filters_by_user(self, client, session):
        """Test that getting all tasks only returns tasks for the authenticated user."""
        user1_token = create_test_token("user1")
        user2_token = create_test_token("user2")

        # Create tasks for user1
        client.post(
            "/api/v1/tasks",
            json={"title": "User1 Task 1"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        client.post(
            "/api/v1/tasks",
            json={"title": "User1 Task 2"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        # Create tasks for user2
        client.post(
            "/api/v1/tasks",
            json={"title": "User2 Task 1"},
            headers={"Authorization": f"Bearer {user2_token}"}
        )

        # User1 should only see their own tasks
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {user1_token}"})
        assert response.status_code == 200
        user1_tasks = response.json()
        assert len(user1_tasks) == 2
        for task in user1_tasks:
            assert task["owner_id"] == "user1"

        # User2 should only see their own task
        response = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {user2_token}"})
        assert response.status_code == 200
        user2_tasks = response.json()
        assert len(user2_tasks) == 1
        assert user2_tasks[0]["owner_id"] == "user2"