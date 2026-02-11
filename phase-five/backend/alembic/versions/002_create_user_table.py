"""Create user table migration.

Revision ID: 002
Revises: 001
Create Date: 2026-01-07
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from uuid import uuid4

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user table with email unique constraint."""
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid4),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("updated_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id", name="pk_user"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)


def downgrade() -> None:
    """Drop user table."""
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
