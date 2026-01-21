"""Add conversation and message tables for AI Agent Chat API.

Revision ID: 005
Revises: 004
Create Date: 2026-01-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create conversation and message tables with indexes."""
    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", postgresql.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="pk_conversation"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_conversation_user_id",
            ondelete="CASCADE"
        ),
    )

    # Create indexes for conversation table
    op.create_index("idx_conversation_user_id", "conversation", ["user_id"])
    op.create_index(
        "idx_conversation_user_updated",
        "conversation",
        ["user_id", sa.text("updated_at DESC")],
        postgresql_using="btree"
    )

    # Create message table
    op.create_table(
        "message",
        sa.Column("id", postgresql.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(), nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_calls", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="pk_message"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversation.id"],
            name="fk_message_conversation_id",
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_message_user_id",
            ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_message_role"
        ),
    )

    # Create indexes for message table
    op.create_index("idx_message_conversation_id", "message", ["conversation_id"])
    op.create_index("idx_message_user_id", "message", ["user_id"])
    op.create_index(
        "idx_message_conv_created",
        "message",
        ["conversation_id", sa.text("created_at ASC")],
        postgresql_using="btree"
    )


def downgrade() -> None:
    """Drop conversation and message tables."""
    # Drop message table and indexes
    op.drop_index("idx_message_conv_created", table_name="message")
    op.drop_index("idx_message_user_id", table_name="message")
    op.drop_index("idx_message_conversation_id", table_name="message")
    op.drop_table("message")

    # Drop conversation table and indexes
    op.drop_index("idx_conversation_user_updated", table_name="conversation")
    op.drop_index("idx_conversation_user_id", table_name="conversation")
    op.drop_table("conversation")
