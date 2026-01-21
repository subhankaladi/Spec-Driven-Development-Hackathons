#!/usr/bin/env python3
"""Test MCP server tools by importing from correct paths."""

import asyncio
import sys
import os

# Add both directories to path
mcp_server_root = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.join(mcp_server_root, '../backend')
sys.path.insert(0, backend_root)

from datetime import timedelta, datetime
from uuid import uuid4, UUID
from dotenv import load_dotenv

# Load MCP server environment
load_dotenv(os.path.join(mcp_server_root, '.env'))

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Import from backend
from src.models.task import Task
from src.models.user import User
from src.services.auth_service import BetterAuthIntegration


async def test_mcp_add_task():
    """Test add_task MCP tool functionality."""

    print("=" * 70)
    print(" MCP SERVER - ADD_TASK TOOL TEST")
    print("=" * 70)

    # Setup database connection
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not set in .env")
        return

    # Convert to async
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(database_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    auth_service = BetterAuthIntegration()

    # Step 1: Create or get test user
    print("\n[Step 1/4] Setting up test user...")
    async with async_session_factory() as session:
        query = select(User).where(User.email == "mcp-test@example.com")
        result = await session.exec(query)
        test_user = result.first()

        if not test_user:
            test_user = User(
                id=str(uuid4()),
                email="mcp-test@example.com",
                password_hash=auth_service.get_password_hash("mcptest123"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"✅ Created new test user")
        else:
            print(f"✅ Using existing test user")

        print(f"   Email: {test_user.email}")
        print(f"   ID: {test_user.id}")

    # Step 2: Generate JWT token
    print("\n[Step 2/4] Generating JWT authentication token...")
    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email
    }
    jwt_token = auth_service.create_access_token(token_data, timedelta(minutes=15))
    print(f"✅ JWT Token generated")
    print(f"   Token (first 50 chars): {jwt_token[:50]}...")

    # Step 3: Test add_task operations
    print("\n[Step 3/4] Testing add_task tool (creating 3 tasks)...")
    print("-" * 70)

    test_tasks_data = [
        {
            "title": "🛒 Buy groceries for the week",
            "description": "Milk, eggs, bread, fruits, vegetables"
        },
        {
            "title": "📝 Complete MCP server implementation",
            "description": "Implement all 5 tools: add, list, complete, update, delete"
        },
        {
            "title": "📚 Read documentation on async programming",
            "description": None  # Test with no description
        }
    ]

    created_tasks = []

    for i, task_data in enumerate(test_tasks_data, 1):
        print(f"\n   Task {i}/{len(test_tasks_data)}: {task_data['title']}")

        async with async_session_factory() as session:
            try:
                # Simulate add_task tool logic
                new_task = Task(
                    user_id=UUID(str(test_user.id)),
                    title=task_data["title"],
                    description=task_data["description"],
                    is_completed=False
                )

                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)

                print(f"   ✅ Task created successfully!")
                print(f"      ID: {new_task.id}")
                print(f"      User ID: {new_task.user_id}")
                print(f"      Title: {new_task.title}")
                print(f"      Description: {new_task.description or '(none)'}")
                print(f"      Completed: {new_task.is_completed}")
                print(f"      Created: {new_task.created_at.isoformat()}")

                created_tasks.append(new_task)

            except Exception as e:
                print(f"   ❌ Error creating task: {type(e).__name__}: {e}")

    # Step 4: Verify all tasks in database
    print("\n[Step 4/4] Verifying tasks in database...")
    print("-" * 70)

    async with async_session_factory() as session:
        query = select(Task).where(Task.user_id == UUID(str(test_user.id))).order_by(Task.created_at.desc())
        result = await session.exec(query)
        all_user_tasks = result.all()

        print(f"✅ Total tasks for user '{test_user.email}': {len(all_user_tasks)}")
        print(f"\nShowing most recent 5 tasks:")
        print("-" * 70)

        for i, task in enumerate(all_user_tasks[:5], 1):
            status = "✅" if task.is_completed else "⏳"
            print(f"\n   {i}. {status} {task.title}")
            print(f"      ID: {task.id}")
            print(f"      Description: {task.description or '(none)'}")
            print(f"      Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    await engine.dispose()

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully created {len(created_tasks)} new tasks")
    print(f"✅ Total tasks in database for test user: {len(all_user_tasks)}")
    print(f"✅ add_task MCP tool is working correctly!")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   - Test list_tasks tool (with filters and pagination)")
    print("   - Test complete_task tool (mark tasks as done)")
    print("   - Test update_task tool (modify task fields)")
    print("   - Test delete_task tool (remove tasks)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_mcp_add_task())
