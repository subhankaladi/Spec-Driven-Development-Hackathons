import asyncio
import threading
import time
import requests
import json
from src.main import app
import uvicorn
import os

# Set up local database
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

def run_server():
    """Run the FastAPI server in a separate thread."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8003, log_level="info")
    server = uvicorn.Server(config)
    server.run()

def test_api():
    """Test the API endpoints after server starts."""
    time.sleep(3)  # Wait for server to start

    print("Testing signup...")
    try:
        response = requests.post(
            "http://127.0.0.1:8003/auth/auth/signup",
            headers={"Content-Type": "application/json"},
            json={"email": "newuser6@example.com", "password": "password123"}
        )
        print(f"Signup response: {response.status_code}")
        print(f"Signup content: {response.text}")

        if response.status_code == 201:
            print("Signup successful!")
            data = response.json()
            access_token = data.get("access_token")

            print("Testing sign-in...")
            # Test sign-in with the same credentials
            signin_response = requests.post(
                "http://127.0.0.1:8003/auth/auth/signin",
                headers={"Content-Type": "application/json"},
                json={"email": "newuser6@example.com", "password": "password123"}
            )
            print(f"Signin response: {signin_response.status_code}")
            print(f"Signin content: {signin_response.text}")

            if signin_response.status_code == 200:
                print("Sign-in successful!")
                signin_data = signin_response.json()
                access_token = signin_data.get("access_token")

                # Test adding a task
                print("Testing add task...")
                # We need to get the user ID first, let's use the signup response
                user_id = data["user"]["id"]

                task_response = requests.post(
                    f"http://127.0.0.1:8003/users/{user_id}/tasks",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    },
                    json={"title": "Test task", "description": "This is a test task"}
                )
                print(f"Add task response: {task_response.status_code}")
                print(f"Add task content: {task_response.text}")

        elif response.status_code == 422:
            print("Validation error occurred")
        else:
            print("Signup failed")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Run tests in main thread
    test_api()

    # Keep the script running briefly to allow server to process
    time.sleep(5)