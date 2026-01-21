"""Integration tests for protected endpoints with authentication."""
import pytest
from fastapi.testclient import TestClient


class TestProtectedEndpoints:
    """Tests for authenticated access to task endpoints."""

    def test_create_task_with_auth(self, client: TestClient, test_user, auth_headers):
        """Test creating a task with valid authentication."""
        response = client.post(
            f"/users/{test_user.id}/tasks",
            json={"title": "New Task", "description": "Task description"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["is_completed"] is False

    def test_list_tasks_with_auth(self, client: TestClient, test_user, auth_headers):
        """Test listing tasks with valid authentication."""
        response = client.get(
            f"/users/{test_user.id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_task_with_auth(self, client: TestClient, sample_task, auth_headers):
        """Test getting a specific task with valid authentication."""
        response = client.get(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_task.id)
        assert data["title"] == sample_task.title

    def test_update_task_with_auth(self, client: TestClient, sample_task, auth_headers):
        """Test updating a task with valid authentication."""
        response = client.put(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            json={"title": "Updated Title", "is_completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["is_completed"] is True

    def test_delete_task_with_auth(self, client: TestClient, sample_task, auth_headers):
        """Test deleting a task with valid authentication."""
        response = client.delete(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestUserIsolation:
    """Tests for user isolation with authenticated endpoints."""

    def test_cannot_access_other_user_tasks(
        self, client: TestClient, test_user, different_user_headers
    ):
        """Test that user cannot access another user's tasks."""
        # Try to access test_user's tasks with different user's token
        response = client.get(
            f"/users/{test_user.id}/tasks",
            headers=different_user_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "FORBIDDEN"

    def test_cannot_create_task_for_other_user(
        self, client: TestClient, test_user, different_user_headers
    ):
        """Test that user cannot create tasks for another user."""
        response = client.post(
            f"/users/{test_user.id}/tasks",
            json={"title": "Hacked Task"},
            headers=different_user_headers,
        )
        assert response.status_code == 403

    def test_cannot_update_other_user_task(
        self, client: TestClient, sample_task, different_user_headers
    ):
        """Test that user cannot update another user's task."""
        response = client.put(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            json={"title": "Hacked Update"},
            headers=different_user_headers,
        )
        assert response.status_code == 403

    def test_cannot_delete_other_user_task(
        self, client: TestClient, sample_task, different_user_headers
    ):
        """Test that user cannot delete another user's task."""
        response = client.delete(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            headers=different_user_headers,
        )
        assert response.status_code == 403

    def test_user_can_access_own_tasks(
        self, client: TestClient, test_user, auth_headers
    ):
        """Test that user can access their own tasks."""
        response = client.get(
            f"/users/{test_user.id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
