"""Async database session management for MCP server.

This module provides async SQLModel session factory for database operations.
Uses asyncpg driver for non-blocking PostgreSQL operations.
"""

import os
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """Get async database URL from environment.

    Converts DATABASE_URL to async format if needed (postgresql+asyncpg://).

    Returns:
        Async PostgreSQL connection string

    Raises:
        ValueError: If DATABASE_URL not set in environment
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Convert to async format if not already
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        raise ValueError("DATABASE_URL must be a PostgreSQL connection string")

    return database_url


def create_db_engine() -> AsyncEngine:
    """Create async SQLAlchemy engine with connection pooling.

    Returns:
        Async database engine configured for production use

    Configuration:
        - pool_size: 5 connections
        - max_overflow: 10 additional connections
        - pool_pre_ping: True (verify connections before use)
        - echo: False (no SQL logging by default)
    """
    database_url = get_database_url()

    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connection health
    )

    return engine


def create_session_factory(engine: AsyncEngine) -> sessionmaker:
    """Create async session factory from engine.

    Args:
        engine: Async database engine

    Returns:
        Session factory for creating async sessions
    """
    async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return async_session_factory


async def get_async_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Get async database session (context manager).

    Args:
        engine: Async database engine

    Yields:
        Async database session

    Usage:
        async with get_async_session(engine) as session:
            result = await session.exec(select(Task))
    """
    async_session_factory = create_session_factory(engine)

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
