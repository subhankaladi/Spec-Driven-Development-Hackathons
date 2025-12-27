from fastapi.testclient import TestClient
from backend.src.api.main import app
from backend.src.models.task import Task


def test_create_task():
    """Test creating a new task."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Test description"
    assert data["is_completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_missing_title():
    """Test creating a task with missing required title."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/tasks",
        json={"description": "Test description without title"}
    )
    assert response.status_code == 400


def test_read_tasks():
    """Test reading all tasks."""
    client = TestClient(app)
    # First create a task
    client.post(
        "/api/v1/tasks",
        json={"title": "Test task for reading", "description": "Test description"}
    )

    # Then read all tasks
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Check that our test task is in the response
    task_found = any(task["title"] == "Test task for reading" for task in data)
    assert task_found


def test_read_single_task():
    """Test reading a single task."""
    client = TestClient(app)
    # Create a task first
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Single task", "description": "Description for single task"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Read the specific task
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single task"
    assert data["description"] == "Description for single task"


def test_read_nonexistent_task():
    """Test reading a task that doesn't exist."""
    client = TestClient(app)
    response = client.get("/api/v1/tasks/999999")
    assert response.status_code == 404


def test_update_task():
    """Test updating a task."""
    client = TestClient(app)
    # Create a task first
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Original task", "description": "Original description"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Update the task
    response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated task", "is_completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated task"
    assert data["is_completed"] is True
    assert data["description"] == "Original description"  # Should remain unchanged


def test_update_nonexistent_task():
    """Test updating a task that doesn't exist."""
    client = TestClient(app)
    response = client.put(
        "/api/v1/tasks/999999",
        json={"title": "Updated task", "is_completed": True}
    )
    assert response.status_code == 404


def test_delete_task():
    """Test deleting a task."""
    client = TestClient(app)
    # Create a task first
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Task to delete", "description": "Description for deletion"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify the task is gone
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_task():
    """Test deleting a task that doesn't exist."""
    client = TestClient(app)
    response = client.delete("/api/v1/tasks/999999")
    assert response.status_code == 404