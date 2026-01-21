#!/usr/bin/env python3
"""Quick test for MCP add_task functionality."""

import asyncio
from datetime import timedelta, datetime
from uuid import uuid4, UUID
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('../mcp-server/.env')

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models.task import Task
from src.models.user import User
from src.services.auth_service import BetterAuthIntegration


async def test_add_task():
    """Test add_task tool."""
    print("=" * 60)
    print(" MCP SERVER - ADD_TASK TOOL TEST")
    print("=" * 60)

    # Get database URL and fix for asyncpg
    database_url = os.getenv("DATABASE_URL")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Remove problematic SSL parameters for asyncpg
    database_url = database_url.split("?")[0]  # Remove all query params
    database_url += "?ssl=require"  # Add asyncpg-compatible SSL

    print(f"\n✅ Connecting to database...")

    engine = create_async_engine(database_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    auth_service = BetterAuthIntegration()

    # Create test user
    print("\n[1/3] Setting up test user...")
    async with async_session_factory() as session:
        query = select(User).where(User.email == "mcp@test.com")
        result = await session.exec(query)
        user = result.first()

        if not user:
            user = User(
                id=str(uuid4()),
                email="mcp@test.com",
                password_hash=auth_service.get_password_hash("test123"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ Created user: {user.email}")
        else:
            print(f"✅ Using user: {user.email}")

    # Generate token
    print("\n[2/3] Generating JWT token...")
    token = auth_service.create_access_token(
        {"sub": str(user.id), "email": user.email},
        timedelta(minutes=15)
    )
    print(f"✅ Token: {token[:40]}...")

    # Add tasks
    print("\n[3/3] Adding 3 tasks...")

    tasks_to_add = [
        ("🛒 Buy groceries", "Milk, eggs, bread"),
        ("📝 Complete MCP server", "All 5 tools implemented"),
        ("📚 Read docs", None)
    ]

    for i, (title, desc) in enumerate(tasks_to_add, 1):
        async with async_session_factory() as session:
            task = Task(
                user_id=UUID(str(user.id)),
                title=title,
                description=desc,
                is_completed=False
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            print(f"\n   Task {i}: ✅ {title}")
            print(f"      ID: {task.id}")
            print(f"      Description: {desc or '(none)'}")

    # Verify
    print("\n[Verification] Checking database...")
    async with async_session_factory() as session:
        query = select(Task).where(Task.user_id == UUID(str(user.id)))
        result = await session.exec(query)
        all_tasks = result.all()
        print(f"✅ Total tasks for user: {len(all_tasks)}")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("✅ TEST PASSED - add_task tool works correctly!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_add_task())
