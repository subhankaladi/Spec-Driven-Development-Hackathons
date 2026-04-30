"""Alembic environment configuration."""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlmodel import SQLModel
from src.config import settings
from src.models.task import Task  # Import all models
from src.models.user import User  # Import user model for auth
from src.models.conversation import Conversation  # Import conversation model
from src.models.message import Message  # Import message model
from src.models.tool_invocation import ToolInvocation  # Import tool invocation model

# Interpret the config file for Python logging.
fileConfig("alembic.ini")

# Set target metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine

    # Use settings.database_url instead of alembic.ini
    # SSL mode is already configured in the database URL
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
