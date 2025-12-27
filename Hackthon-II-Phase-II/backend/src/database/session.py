from sqlmodel import create_engine, Session
from src.config.settings import settings
from typing import Generator


# Create the database engine with connection pooling
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session for FastAPI endpoints."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create database tables - call this on application startup."""
    from src.models.task import Task
    from src.models.user import User
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)