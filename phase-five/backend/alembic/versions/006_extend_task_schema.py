"""Extend Task schema with Phase V features: recurring tasks, reminders, priorities, tags.

Revision ID: 006
Revises: 005
Create Date: 2026-02-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new columns to task table for Phase V features."""
    # Add columns to task table
    op.add_column(
        "task",
        sa.Column("due_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "task",
        sa.Column("remind_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "task",
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
    )
    op.add_column(
        "task",
        sa.Column("tags", postgresql.JSON(), nullable=True, server_default="[]"),
    )
    op.add_column(
        "task",
        sa.Column("recurrence_rule", postgresql.JSON(), nullable=True),
    )
    op.add_column(
        "task",
        sa.Column("next_occurrence_at", sa.DateTime(), nullable=True),
    )

    # Create indexes for efficient filtering and sorting
    op.create_index(
        "ix_task_user_id_due_at",
        "task",
        ["user_id", "due_at"],
        unique=False,
    )
    op.create_index(
        "ix_task_user_id_priority",
        "task",
        ["user_id", "priority"],
        unique=False,
    )
    op.create_index(
        "ix_task_user_id_created_at",
        "task",
        ["user_id", "created_at"],
        unique=False,
    )

    # Create AuditLog table
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),  # created, updated, deleted, completed
        sa.Column("task_id", postgresql.UUID(), nullable=False),
        sa.Column("change_data", postgresql.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("service_name", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log"),
    )

    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"], unique=False)
    op.create_index("ix_audit_log_task_id", "audit_log", ["task_id"], unique=False)
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"], unique=False)

    # Create Reminder table
    op.create_table(
        "reminder",
        sa.Column("id", postgresql.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", postgresql.UUID(), nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("remind_at", sa.DateTime(), nullable=False),
        sa.Column("notification_method", sa.String(50), nullable=True, server_default="default"),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),  # scheduled, triggered, cancelled
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("triggered_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_reminder"),
    )

    op.create_index("ix_reminder_task_id", "reminder", ["task_id"], unique=False)
    op.create_index("ix_reminder_user_id", "reminder", ["user_id"], unique=False)
    op.create_index("ix_reminder_remind_at", "reminder", ["remind_at"], unique=False)


def downgrade() -> None:
    """Revert Phase V schema changes."""
    # Drop Reminder table
    op.drop_index("ix_reminder_remind_at", table_name="reminder")
    op.drop_index("ix_reminder_user_id", table_name="reminder")
    op.drop_index("ix_reminder_task_id", table_name="reminder")
    op.drop_table("reminder")

    # Drop AuditLog table
    op.drop_index("ix_audit_log_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_task_id", table_name="audit_log")
    op.drop_index("ix_audit_log_user_id", table_name="audit_log")
    op.drop_table("audit_log")

    # Drop indexes on task table
    op.drop_index("ix_task_user_id_created_at", table_name="task")
    op.drop_index("ix_task_user_id_priority", table_name="task")
    op.drop_index("ix_task_user_id_due_at", table_name="task")

    # Drop columns from task table
    op.drop_column("task", "next_occurrence_at")
    op.drop_column("task", "recurrence_rule")
    op.drop_column("task", "tags")
    op.drop_column("task", "priority")
    op.drop_column("task", "remind_at")
    op.drop_column("task", "due_at")
