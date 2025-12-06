import pytest
from src.todo.task import Task
from src.todo.repository import TaskRepository

@pytest.fixture
def repository():
    return TaskRepository()

def test_add_task(repository: TaskRepository):
    task = repository.add("Test Title", "Test Description")
    assert task.title == "Test Title"
    assert task.description == "Test Description"
    assert task.completed is False
    assert len(repository.get_all()) == 1

def test_get_all_tasks(repository: TaskRepository):
    repository.add("Task 1", "Desc 1")
    repository.add("Task 2", "Desc 2")
    tasks = repository.get_all()
    assert len(tasks) == 2

def test_get_task_by_id(repository: TaskRepository):
    task = repository.add("Test Task", "Test Desc")
    retrieved_task = repository.get_by_id(task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id

def test_update_task(repository: TaskRepository):
    task = repository.add("Original Title", "Original Desc")
    updated_task = repository.update(task.id, "New Title", "New Desc")
    assert updated_task is not None
    assert updated_task.title == "New Title"
    assert updated_task.description == "New Desc"

def test_delete_task(repository: TaskRepository):
    task = repository.add("To Be Deleted", "Delete Me")
    assert repository.delete(task.id) is True
    assert repository.get_by_id(task.id) is None
    assert len(repository.get_all()) == 0

def test_toggle_task_status(repository: TaskRepository):
    task = repository.add("Test Task", "Test Desc")
    assert task.completed is False
    task.completed = not task.completed
    assert task.completed is True
