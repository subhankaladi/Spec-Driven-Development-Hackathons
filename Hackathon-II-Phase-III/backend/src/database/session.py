from sqlmodel import create_engine, Session
from src.config.settings import settings
from typing import Generator


# Create the database engine with connection pooling
# Different configuration for SQLite vs PostgreSQL
if settings.is_sqlite:
    # SQLite configuration
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=not settings.is_production,  # Log SQL queries in development
    )
else:
    # PostgreSQL (Neon) configuration
    engine = create_engine(
        settings.database_url,
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Max connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections after 5 minutes
        echo=not settings.is_production,  # Log SQL queries in development
    )


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session for FastAPI endpoints."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create database tables - call this on application startup."""
    from src.models.task import Task
    from src.models.user import User
    from src.models.conversation import Conversation
    from src.models.message import Message
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)