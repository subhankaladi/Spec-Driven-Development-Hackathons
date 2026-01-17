"""Pytest fixtures for MCP server testing.

Provides test database session, JWT tokens, test users, and test tasks.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Add backend to path for model imports
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.models.task import Task
from src.models.user import User
from src.services.auth_service import BetterAuthIntegration


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create test database engine."""
    from sqlmodel import SQLModel

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide test database session with automatic rollback."""
    async_session_factory = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def test_user_id() -> str:
    """Provide consistent test user ID."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture(scope="function")
def test_user_email() -> str:
    """Provide consistent test user email."""
    return "test@example.com"


@pytest.fixture(scope="function")
def test_jwt_token(test_user_id: str, test_user_email: str) -> str:
    """Create valid JWT token for testing."""
    auth_service = BetterAuthIntegration()

    token_data = {
        "sub": test_user_id,
        "email": test_user_email
    }

    token = auth_service.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=15)
    )

    return token


@pytest.fixture(scope="function")
def expired_jwt_token(test_user_id: str, test_user_email: str) -> str:
    """Create expired JWT token for testing authentication failures."""
    auth_service = BetterAuthIntegration()

    token_data = {
        "sub": test_user_id,
        "email": test_user_email,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }

    # Manually encode with past expiration
    from jose import jwt
    token = jwt.encode(token_data, auth_service.secret, algorithm=auth_service.algorithm)

    return token


@pytest.fixture(scope="function")
def invalid_jwt_token() -> str:
    """Provide malformed JWT token for testing."""
    return "invalid.jwt.token.string"


@pytest.fixture(scope="function")
async def test_user(
    test_db_session: AsyncSession,
    test_user_id: str,
    test_user_email: str
) -> User:
    """Create test user in database."""
    auth_service = BetterAuthIntegration()

    user = User(
        id=test_user_id,
        email=test_user_email,
        password_hash=auth_service.get_password_hash("testpassword123"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
async def test_tasks(
    test_db_session: AsyncSession,
    test_user: User
) -> list[Task]:
    """Create test tasks in database."""
    tasks = [
        Task(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            title="Buy groceries",
            description="Milk, eggs, bread",
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Task(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            title="Finish project",
            description="Complete MCP server implementation",
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Task(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            title="Read book",
            description=None,
            is_completed=True,
            created_at=datetime.utcnow() - timedelta(days=1),
            updated_at=datetime.utcnow() - timedelta(days=1)
        ),
    ]

    for task in tasks:
        test_db_session.add(task)

    await test_db_session.commit()

    for task in tasks:
        await test_db_session.refresh(task)

    return tasks


@pytest.fixture(scope="function")
def other_user_id() -> str:
    """Provide different user ID for authorization testing."""
    return "987e6543-e89b-12d3-a456-426614174999"


@pytest.fixture(scope="function")
def other_user_jwt_token(other_user_id: str) -> str:
    """Create JWT token for different user (authorization testing)."""
    auth_service = BetterAuthIntegration()

    token_data = {
        "sub": other_user_id,
        "email": "other@example.com"
    }

    token = auth_service.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=15)
    )

    return token
