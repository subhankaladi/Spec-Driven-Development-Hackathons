#!/usr/bin/env python3
"""Simple test script for MCP server add_task tool."""

import asyncio
import sys
import os
from datetime import timedelta, datetime
from uuid import uuid4

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from dotenv import load_dotenv
load_dotenv()

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Import backend models and services
from src.models.task import Task
from src.models.user import User
from src.services.auth_service import BetterAuthIntegration


async def test_add_task_direct():
    """Test add_task by directly calling the database operations."""

    print("=" * 60)
    print("MCP Server Tool Test - Add Tasks")
    print("=" * 60)

    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not set")
        return

    # Convert to async format
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"\n✅ Database URL configured")

    # Create engine
    engine = create_async_engine(database_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Setup test user
    auth_service = BetterAuthIntegration()

    print("\n[1/3] Setting up test user...")
    async with async_session_factory() as session:
        query = select(User).where(User.email == "test@mcp-server.com")
        result = await session.exec(query)
        test_user = result.first()

        if not test_user:
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
            print(f"✅ Using existing user: {test_user.email}")

        print(f"   User ID: {test_user.id}")

    # Generate JWT token
    print("\n[2/3] Generating JWT token...")
    token_data = {"sub": str(test_user.id), "email": test_user.email}
    jwt_token = auth_service.create_access_token(token_data, timedelta(minutes=15))
    print(f"✅ JWT token: {jwt_token[:50]}...")

    # Test adding tasks
    print("\n[3/3] Adding tasks via MCP tool simulation...")

    test_tasks = [
        {"title": "Buy groceries", "description": "Milk, eggs, bread"},
        {"title": "Complete MCP server", "description": "Implement all 5 tools"},
        {"title": "Write documentation", "description": None}
    ]

    created_count = 0

    for i, task_data in enumerate(test_tasks, 1):
        print(f"\n   Task {i}/{len(test_tasks)}: '{task_data['title']}'")

        async with async_session_factory() as session:
            try:
                # Simulate add_task tool behavior
                from uuid import UUID

                new_task = Task(
                    user_id=UUID(str(test_user.id)),
                    title=task_data["title"],
                    description=task_data["description"],
                    is_completed=False
                )

                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)

                print(f"   ✅ Created successfully!")
                print(f"      ID: {new_task.id}")
                print(f"      Title: {new_task.title}")
                print(f"      Description: {new_task.description}")
                print(f"      Completed: {new_task.is_completed}")

                created_count += 1

            except Exception as e:
                print(f"   ❌ Error: {e}")

    # Verify in database
    print("\n[Verification] Checking database...")
    async with async_session_factory() as session:
        from uuid import UUID
        query = select(Task).where(Task.user_id == UUID(str(test_user.id)))
        result = await session.exec(query)
        all_tasks = result.all()

        print(f"✅ Total tasks for user: {len(all_tasks)}")
        print(f"\nLast 3 tasks:")
        for i, task in enumerate(all_tasks[-3:], 1):
            print(f"   {i}. {task.title} (completed: {task.is_completed})")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print(f"✅ Successfully added {created_count} tasks")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_add_task_direct())
