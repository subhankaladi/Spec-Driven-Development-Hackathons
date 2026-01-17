"""Remove refresh token fields from user table.

Revision ID: 004
Revises: 003
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove refresh_token and refresh_token_expiry columns from user table."""
    op.drop_column("user", "refresh_token_expiry")
    op.drop_column("user", "refresh_token")


def downgrade() -> None:
    """Add refresh_token and refresh_token_expiry columns to user table."""
    op.add_column(
        "user",
        sa.Column("refresh_token", sa.String(255), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("refresh_token_expiry", sa.DateTime(), nullable=True)
    )