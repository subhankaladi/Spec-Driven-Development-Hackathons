import requests
import time
import os
import threading
from src.main import app
import uvicorn

# Set up local database
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

def run_server():
    """Run the FastAPI server in a separate thread."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8004, log_level="info")
    server = uvicorn.Server(config)
    server.run()

def test_task_operations():
    """Test task operations after server starts."""
    time.sleep(3)  # Wait for server to start

    # Sign up a new user
    print("Creating a new user...")
    signup_response = requests.post(
        "http://127.0.0.1:8004/auth/auth/signup",
        headers={"Content-Type": "application/json"},
        json={"email": "tasktest@example.com", "password": "password123"}
    )

    if signup_response.status_code != 201:
        print(f"Signup failed: {signup_response.status_code} - {signup_response.text}")
        return

    signup_data = signup_response.json()
    user_id = signup_data["user"]["id"]
    access_token = signup_data["access_token"]

    print(f"User created with ID: {user_id}")

    # Add a task
    print("Adding a task...")
    task_response = requests.post(
        f"http://127.0.0.1:8004/users/{user_id}/tasks",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={"title": "Test task from verification", "description": "This is a test task for verification"}
    )

    if task_response.status_code != 201:
        print(f"Add task failed: {task_response.status_code} - {task_response.text}")
        return

    task_data = task_response.json()
    task_id = task_data["id"]
    print(f"Task created with ID: {task_id}")

    # Get the task
    print("Retrieving the task...")
    get_task_response = requests.get(
        f"http://127.0.0.1:8004/users/{user_id}/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if get_task_response.status_code != 200:
        print(f"Get task failed: {get_task_response.status_code} - {get_task_response.text}")
        return

    retrieved_task = get_task_response.json()
    print(f"Retrieved task: {retrieved_task['title']} - {retrieved_task['description']}")

    # List all tasks for the user
    print("Listing all tasks for the user...")
    list_tasks_response = requests.get(
        f"http://127.0.0.1:8004/users/{user_id}/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if list_tasks_response.status_code != 200:
        print(f"List tasks failed: {list_tasks_response.status_code} - {list_tasks_response.text}")
        return

    tasks_list = list_tasks_response.json()
    print(f"User has {tasks_list['total']} task(s)")
    for task in tasks_list['items']:
        print(f"- Task: {task['title']}")

    print("All task operations completed successfully!")

if __name__ == "__main__":
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Run tests in main thread
    test_task_operations()

    # Keep the script running briefly to allow server to process
    time.sleep(5)