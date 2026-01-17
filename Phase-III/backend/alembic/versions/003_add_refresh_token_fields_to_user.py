"""Add refresh token fields to user table.

Revision ID: 003
Revises: 002
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add refresh_token and refresh_token_expiry columns to user table."""
    # Add refresh_token column
    op.add_column(
        "user",
        sa.Column("refresh_token", sa.String(255), nullable=True)
    )

    # Add refresh_token_expiry column
    op.add_column(
        "user",
        sa.Column("refresh_token_expiry", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Remove refresh_token and refresh_token_expiry columns from user table."""
    op.drop_column("user", "refresh_token_expiry")
    op.drop_column("user", "refresh_token")