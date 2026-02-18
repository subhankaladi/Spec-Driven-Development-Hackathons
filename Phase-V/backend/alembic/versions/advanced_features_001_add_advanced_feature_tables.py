"""Add advanced features tables: recurring_task_templates, reminders, tags, task_tags, task_event_logs

Revision ID: advanced_features_001
Revises: 736cddebc5ac
Create Date: 2026-02-15 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'advanced_features_001'
down_revision: Union[str, None] = '736cddebc5ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create recurring_task_templates table
    op.create_table(
        'recurring_task_templates',
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('user_id', sa.Uuid, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),  # Using string for SQLite compatibility
        sa.Column('recurrence_pattern', sa.JSON, nullable=False),  # Using JSON for SQLite compatibility
        sa.Column('start_date', sa.DateTime, nullable=False),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('max_occurrences', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.Index('idx_recurringtasktemplate_user_id', 'user_id'),
        sa.Index('idx_recurringtasktemplate_active', 'is_active'),
    )

    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('task_instance_id', sa.Uuid, nullable=False),
        sa.Column('user_id', sa.Uuid, nullable=False),
        sa.Column('reminder_time', sa.DateTime, nullable=False),
        sa.Column('method', sa.String(20), nullable=False),  # Using string for SQLite compatibility
        sa.Column('is_sent', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['task_instance_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.Index('idx_reminder_user_time', 'user_id', 'reminder_time'),
        sa.Index('idx_reminder_task_instance', 'task_instance_id'),
        sa.Index('idx_reminder_sent_status', 'is_sent'),
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('user_id', sa.Uuid, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),  # Hex color code
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
        sa.Index('idx_tag_user_name', 'user_id', 'name', unique=True),
        sa.Index('idx_tag_user_id', 'user_id'),
    )

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_instance_id', sa.Uuid, primary_key=True),
        sa.Column('tag_id', sa.Uuid, primary_key=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['task_instance_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.Index('idx_tasktag_task_instance', 'task_instance_id'),
        sa.Index('idx_tasktag_tag', 'tag_id'),
    )

    # Create task_event_logs table
    op.create_table(
        'task_event_logs',
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('user_id', sa.Uuid, nullable=False),
        sa.Column('task_instance_id', sa.Uuid, nullable=True),  # Nullable since some events might not be task-specific
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('payload', sa.JSON, nullable=False),  # Using JSON for SQLite compatibility
        sa.Column('processed_by_kafka', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['task_instance_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.Index('idx_taskeventlog_user_created', 'user_id', 'created_at'),
        sa.Index('idx_taskeventlog_processed', 'processed_by_kafka'),
        sa.Index('idx_taskeventlog_event_type', 'event_type'),
    )

    # Add new columns to existing tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(20), nullable=False, server_default='medium'))  # Using string for SQLite compatibility
    op.add_column('tasks', sa.Column('parent_template_id', sa.Uuid(), nullable=True))
    op.create_index('idx_taskinstance_due_date', 'tasks', ['due_date'])
    op.create_index('idx_taskinstance_priority', 'tasks', ['priority'])
    op.create_index('idx_taskinstance_completion_status', 'tasks', ['is_completed'])
    op.create_index('idx_taskinstance_parent_template', 'tasks', ['parent_template_id'])
    op.create_index('idx_taskinstance_user_priority_due', 'tasks', ['user_id', 'priority', 'due_date'])
    op.create_foreign_key('fk_tasks_parent_template', 'tasks', 'recurring_task_templates', ['parent_template_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint('fk_tasks_parent_template', 'tasks', type_='foreignkey')
    
    # Drop indexes from tasks table
    op.drop_index('idx_taskinstance_user_priority_due', table_name='tasks')
    op.drop_index('idx_taskinstance_parent_template', table_name='tasks')
    op.drop_index('idx_taskinstance_completion_status', table_name='tasks')
    op.drop_index('idx_taskinstance_priority', table_name='tasks')
    op.drop_index('idx_taskinstance_due_date', table_name='tasks')
    
    # Drop columns from tasks table
    op.drop_column('tasks', 'parent_template_id')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')

    # Drop tables in reverse order
    op.drop_table('task_event_logs')
    op.drop_table('task_tags')
    op.drop_table('tags')
    op.drop_table('reminders')
    op.drop_table('recurring_task_templates')