"""Database connection and session management."""
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Generator
import logging

from src.config import settings

logger = logging.getLogger(__name__)

# Create SQLModel engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)


def get_engine():
    """Get the database engine."""
    return engine


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


def create_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def init_db():
    """Initialize the database."""
    create_tables()
    logger.info("Database initialized")
