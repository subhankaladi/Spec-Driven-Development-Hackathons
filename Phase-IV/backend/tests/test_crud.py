"""Integration tests for CRUD operations."""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient


class TestCreateTask:
    """Tests for POST /users/{user_id}/tasks."""

    def test_create_task_success(self, client: TestClient, sample_user_id: uuid4):
        """Test successful task creation."""
        response = client.post(
            f"/users/{sample_user_id}/tasks",
            json={"title": "New Task", "description": "Task description"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["is_completed"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_task_without_description(self, client: TestClient, sample_user_id: uuid4):
        """Test task creation without optional description."""
        response = client.post(
            f"/users/{sample_user_id}/tasks",
            json={"title": "Task without description"},
        )
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_task_empty_title(self, client: TestClient, sample_user_id: uuid4):
        """Test task creation fails with empty title (validation at API level)."""
        response = client.post(
            f"/users/{sample_user_id}/tasks",
            json={"title": ""},
        )
        # Empty string will fail Pydantic validation (min_length=1)
        assert response.status_code in [400, 422]

    def test_create_task_missing_title(self, client: TestClient, sample_user_id: uuid4):
        """Test task creation fails when title is missing."""
        response = client.post(
            f"/users/{sample_user_id}/tasks",
            json={},
        )
        assert response.status_code == 422  # Validation error


class TestListTasks:
    """Tests for GET /users/{user_id}/tasks."""

    def test_list_tasks_empty(self, client: TestClient, sample_user_id: uuid4):
        """Test listing tasks when user has none."""
        response = client.get(f"/users/{sample_user_id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_tasks_with_pagination(self, client: TestClient, sample_user_id: uuid4):
        """Test pagination parameters."""
        response = client.get(
            f"/users/{sample_user_id}/tasks?page=1&page_size=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5


class TestGetTask:
    """Tests for GET /users/{user_id}/tasks/{task_id}."""

    def test_get_task_success(self, client: TestClient, sample_task):
        """Test successful task retrieval."""
        # Use the user_id from the sample_task fixture
        response = client.get(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_task.id)
        assert data["title"] == sample_task.title

    def test_get_task_not_found(self, client: TestClient, sample_user_id: uuid4):
        """Test task not found returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/users/{sample_user_id}/tasks/{fake_id}"
        )
        assert response.status_code == 404
        data = response.json()
        # FastAPI returns error in 'detail' key for HTTPException
        detail = data.get("detail", {})
        assert "not found" in detail.get("message", "").lower()


class TestUpdateTask:
    """Tests for PUT/PATCH /users/{user_id}/tasks/{task_id}."""

    def test_update_task_put(self, client: TestClient, sample_task):
        """Test full update with PUT."""
        response = client.put(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            json={"title": "Updated Title", "is_completed": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["is_completed"] is True

    def test_update_task_patch(self, client: TestClient, sample_task):
        """Test partial update with PATCH."""
        response = client.patch(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}",
            json={"title": "Patched Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Patched Title"


class TestDeleteTask:
    """Tests for DELETE /users/{user_id}/tasks/{task_id}."""

    def test_delete_task_success(self, client: TestClient, sample_task):
        """Test successful task deletion."""
        response = client.delete(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}"
        )
        assert response.status_code == 204

        # Verify task is gone
        get_response = client.get(
            f"/users/{sample_task._test_user_id}/tasks/{sample_task.id}"
        )
        assert get_response.status_code == 404
