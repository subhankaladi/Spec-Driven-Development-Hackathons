# Data Model: Task Entity

**Feature**: 005-mcp-todo-server
**Date**: 2026-01-10

## Task Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Auto-generated | Unique identifier for the task |
| `user_id` | UUID | FK, Indexed, NOT NULL | Owner of the task (enforces isolation) |
| `title` | String(255) | NOT NULL | Task title (required) |
| `description` | String(2000) | NULLABLE | Optional extended description |
| `is_completed` | Boolean | DEFAULT False | Completion status |
| `created_at` | DateTime | Auto-set | Timestamp of creation |
| `updated_at` | DateTime | Auto-update | Timestamp of last modification |

## Relationships

- **User** (1:N) → **Task**: Each task belongs to exactly one user; a user can have many tasks.

## SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(max_length=2000, default=None)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `pk_task` | `id` | Primary key lookup |
| `idx_task_user_id` | `user_id` | Fast user-owned task lookups |
| `idx_task_user_completed` | `user_id`, `is_completed` | Efficient list_tasks filtering |

## Validation Rules

- **Title**: 1-255 characters, required
- **Description**: 0-2000 characters, optional
- **User ID**: Must correspond to existing user in database (foreign key constraint)

## Ownership Enforcement

Every CRUD operation must:
1. Extract `user_id` from validated JWT
2. Query with `WHERE user_id = {extracted_id} AND id = {task_id}`
3. Reject if no row is affected (task doesn't exist or belongs to another user)
