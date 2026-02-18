"""Test configuration and fixtures."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from uuid import uuid4, UUID
from typing import Generator

from src.main import app
from src.models.database import get_session
from src.models.task import Task
from src.models.user import User
from src.core.auth import hash_password, create_jwt_token, verify_jwt_token
from src.config import get_settings


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine")
def fixture_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables including users
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(engine):
    """Create test client with dependency overrides."""

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_id() -> UUID:
    """Return a sample user ID for testing."""
    return uuid4()


@pytest.fixture
def test_user(session: Session) -> User:
    """Create a test user with hashed password."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers with valid JWT token."""
    settings = get_settings()
    token = create_jwt_token(
        user_id=test_user.id,
        email=test_user.email,
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def different_user(session: Session) -> User:
    """Create a different test user."""
    user = User(
        email="other@example.com",
        password_hash=hash_password("otherpassword456"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def different_user_headers(different_user: User) -> dict:
    """Create authorization headers for different user."""
    settings = get_settings()
    token = create_jwt_token(
        user_id=different_user.id,
        email=different_user.email,
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token(test_user: User) -> str:
    """Create an expired JWT token for testing."""
    settings = get_settings()
    token = create_jwt_token(
        user_id=test_user.id,
        email=test_user.email,
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expiration_hours=-1,  # Already expired
    )
    return token


@pytest.fixture
def expired_auth_headers(expired_token: str) -> dict:
    """Create authorization headers with expired JWT token."""
    return {"Authorization": f"Bearer {expired_token}"}


@pytest.fixture
def sample_task(session: Session, user_id: UUID = None) -> Task:
    """Create and return a sample task using the sample_user_id fixture."""
    from uuid import uuid4
    task_user_id = user_id if user_id else uuid4()

    # Store the user_id for later retrieval
    task = Task(
        user_id=task_user_id,
        title="Test Task",
        description="Test Description",
        is_completed=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    # Attach the user_id for test access
    task._test_user_id = task_user_id
    return task
