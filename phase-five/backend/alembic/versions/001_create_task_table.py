"""Create task table migration.

Revision ID: 001
Revises:
Create Date: 2026-01-07
"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel
from uuid import uuid4

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create task table."""
    op.create_table(
        "task",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid4),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_task"),
        sa.Index("ix_task_user_id", "user_id"),
    )


def downgrade() -> None:
    """Drop task table."""
    op.drop_table("task")
