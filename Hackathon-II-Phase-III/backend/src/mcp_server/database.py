"""
Database connection and session management.

Provides async SQLModel engine and session factory for Neon PostgreSQL.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, select

from .config import Config


# Async engine for Neon Serverless PostgreSQL
async_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10
)


async def get_session() -> AsyncSession:
    """Get async database session."""
    async with AsyncSession(async_engine) as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    from .models import Task  # noqa: F401
    from sqlmodel import SQLModel

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
