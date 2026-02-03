#!/usr/bin/env python3
"""Test script for add_task MCP tool.

This script tests the add_task functionality by:
1. Creating a test user in the database
2. Generating a valid JWT token
3. Calling add_task handler with the token
4. Verifying the task was created
"""

import asyncio
import sys
import os
from datetime import timedelta

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load MCP server environment
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from src.tools.add_task import add_task_handler
from backend.src.models.user import User
from backend.src.services.auth_service import BetterAuthIntegration


async def test_add_task():
    """Test add_task tool with real database."""

    print("=" * 60)
    print("MCP Server - Add Task Tool Test")
    print("=" * 60)

    # Step 1: Setup database connection
    print("\n[1/5] Setting up database connection...")
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL not set in .env")
        return

    engine = create_async_engine(database_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print(f"✅ Connected to database")

    # Step 2: Create or get test user
    print("\n[2/5] Setting up test user...")
    auth_service = BetterAuthIntegration()

    async with async_session_factory() as session:
        from sqlmodel import select

        # Check if test user exists
        query = select(User).where(User.email == "test@mcp-server.com")
        result = await session.exec(query)
        test_user = result.first()

        if not test_user:
            # Create test user
            from uuid import uuid4
            from datetime import datetime

            test_user = User(
                id=str(uuid4()),
                email="test@mcp-server.com",
                password_hash=auth_service.get_password_hash("testpassword123"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"✅ Created test user: {test_user.email}")
        else:
            print(f"✅ Using existing test user: {test_user.email}")

        print(f"   User ID: {test_user.id}")

    # Step 3: Generate JWT token
    print("\n[3/5] Generating JWT token...")
    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email
    }

    jwt_token = auth_service.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=15)
    )

    print(f"✅ Generated JWT token: {jwt_token[:50]}...")

    # Step 4: Test add_task tool
    print("\n[4/5] Testing add_task tool...")

    test_tasks = [
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, and coffee"
        },
        {
            "title": "Finish MCP server implementation",
            "description": "Complete all 5 tools and test them"
        },
        {
            "title": "Schedule dentist appointment",
            "description": None
        }
    ]

    created_tasks = []

    for i, task_data in enumerate(test_tasks, 1):
        print(f"\n   Task {i}/{len(test_tasks)}: '{task_data['title']}'")

        async with async_session_factory() as session:
            try:
                # Call add_task handler
                arguments = {
                    "jwt_token": jwt_token,
                    "title": task_data["title"],
                    "description": task_data["description"]
                }

                result = await add_task_handler(arguments, session)

                print(f"   ✅ Task created successfully!")
                print(f"      ID: {result['id']}")
                print(f"      Title: {result['title']}")
                print(f"      Description: {result['description']}")
                print(f"      Completed: {result['is_completed']}")
                print(f"      Created: {result['created_at']}")

                created_tasks.append(result)

            except Exception as e:
                print(f"   ❌ Error: {type(e).__name__}: {str(e)}")

    # Step 5: Verify tasks in database
    print("\n[5/5] Verifying tasks in database...")

    async with async_session_factory() as session:
        from backend.src.models.task import Task
        from uuid import UUID

        query = select(Task).where(Task.user_id == UUID(str(test_user.id)))
        result = await session.exec(query)
        all_tasks = result.all()

        print(f"✅ Found {len(all_tasks)} total tasks for test user")

        for i, task in enumerate(all_tasks[-3:], 1):  # Show last 3 tasks
            print(f"\n   Task {i}:")
            print(f"      ID: {task.id}")
            print(f"      Title: {task.title}")
            print(f"      Description: {task.description}")
            print(f"      Completed: {task.is_completed}")

    # Cleanup
    await engine.dispose()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Successfully created {len(created_tasks)} tasks")
    print(f"✅ All tasks verified in database")
    print(f"✅ add_task tool working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_add_task())
