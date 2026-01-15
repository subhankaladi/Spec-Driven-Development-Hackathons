"""
Configuration management for MCP Server & Todo Tooling.

Loads environment variables and provides database connection configuration.
"""

import os
from typing import Optional


class Config:
    """Database and server configuration."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost/todo_db"
    )

    # JWT
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "change-me-in-production"
    )
    JWT_ALGORITHM: str = "HS256"

    # MCP Server
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "todo-mcp-server")
    MCP_LOG_LEVEL: str = os.getenv("MCP_LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.DATABASE_URL or cls.DATABASE_URL.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be set and use asyncpg driver")
        if cls.JWT_SECRET == "change-me-in-production":
            import warnings
            warnings.warn("JWT_SECRET is not set; using default insecure value", UserWarning)
