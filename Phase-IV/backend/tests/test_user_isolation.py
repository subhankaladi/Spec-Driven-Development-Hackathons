"""Tests for user isolation security."""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient


class TestUserIsolation:
    """Tests to verify cross-user access is blocked."""

    def test_cannot_access_other_user_task(self, client: TestClient):
        """Test that users cannot access tasks belonging to other users."""
        user1_id = uuid4()
        user2_id = uuid4()

        # User 1 creates a task
        create_response = client.post(
            f"/users/{user1_id}/tasks",
            json={"title": "User 1's Task"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User 2 tries to access User 1's task - should return 404
        get_response = client.get(
            f"/users/{user2_id}/tasks/{task_id}"
        )
        assert get_response.status_code == 404

    def test_cannot_update_other_user_task(self, client: TestClient):
        """Test that users cannot update tasks belonging to other users."""
        user1_id = uuid4()
        user2_id = uuid4()

        # User 1 creates a task
        create_response = client.post(
            f"/users/{user1_id}/tasks",
            json={"title": "User 1's Task"},
        )
        task_id = create_response.json()["id"]

        # User 2 tries to update User 1's task - should return 404
        update_response = client.put(
            f"/users/{user2_id}/tasks/{task_id}",
            json={"title": "Hacked Title"},
        )
        assert update_response.status_code == 404

    def test_cannot_delete_other_user_task(self, client: TestClient):
        """Test that users cannot delete tasks belonging to other users."""
        user1_id = uuid4()
        user2_id = uuid4()

        # User 1 creates a task
        create_response = client.post(
            f"/users/{user1_id}/tasks",
            json={"title": "User 1's Task"},
        )
        task_id = create_response.json()["id"]

        # User 2 tries to delete User 1's task - should return 404
        delete_response = client.delete(
            f"/users/{user2_id}/tasks/{task_id}"
        )
        assert delete_response.status_code == 404

        # Verify task still exists for User 1
        get_response = client.get(
            f"/users/{user1_id}/tasks/{task_id}"
        )
        assert get_response.status_code == 200

    def test_list_does_not_show_other_user_tasks(self, client: TestClient):
        """Test that listing tasks only shows user's own tasks."""
        user1_id = uuid4()
        user2_id = uuid4()

        # User 1 creates a task
        response1 = client.post(
            f"/users/{user1_id}/tasks",
            json={"title": "User 1's Task"},
        )
        assert response1.status_code == 201

        # User 2 creates their own task
        response2 = client.post(
            f"/users/{user2_id}/tasks",
            json={"title": "User 2's Task"},
        )
        assert response2.status_code == 201

        # User 1 lists their tasks - should only see their own
        list_response = client.get(f"/users/{user1_id}/tasks")
        assert list_response.status_code == 200
        tasks = list_response.json()["items"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "User 1's Task"
