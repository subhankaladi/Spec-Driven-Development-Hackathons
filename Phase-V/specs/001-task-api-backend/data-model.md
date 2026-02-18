# Data Model: Task API Backend

## Overview

This document describes the database schema for the Task API Backend using SQLModel with Neon Serverless PostgreSQL.

## Entity Relationship

```
User (referenced by user_id)
  │
  └── One-to-Many ───> Task
```

Each task belongs to exactly one user. Users can have many tasks.

## Task Entity

### SQLModel Definition

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False, min_length=1)
    description: Optional[str] = Field(default=None, nullable=True)
    is_completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Auto-generated | Unique task identifier |
| user_id | UUID | Foreign Key, Not Null, Indexed | Owning user identifier |
| title | String(255) | Not Null, Min 1 char | Task title |
| description | Text | Nullable | Optional task details |
| is_completed | Boolean | Default: False | Completion status |
| created_at | DateTime | Auto-generated | Creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |

### Indexes

1. **Primary Key**: `id` (clustered index)
2. **Foreign Key**: `user_id` (for join performance)
3. **Composite**: `(user_id, created_at)` (for list queries with sorting)
4. **Composite**: `(user_id, is_completed)` (for filtered lists)

### Validation Rules

- `title` must be 1-255 characters, non-empty
- `description` is optional, can be NULL
- `is_completed` defaults to False
- `user_id` must reference a valid user (future constraint)

## Pydantic Schemas (API Layer)

### TaskCreate (Request)

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
```

### TaskUpdate (Request)

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
```

### TaskResponse (Response)

```python
class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
```

### TaskListResponse (Paginated)

```python
class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Database Operations

### Create Task

```python
task = Task(user_id=user_id, title=data.title, description=data.description)
session.add(task)
session.commit()
session.refresh(task)
```

### Read Tasks (User-Scoped)

```python
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .offset((page - 1) * page_size)
    .limit(page_size)
    .order_by(Task.created_at.desc())
).all()
```

### Read Single Task (User-Scoped)

```python
task = session.exec(
    select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
).first()
```

### Update Task (User-Scoped)

```python
task = ...  # Query with user_id filter
task.title = data.title
task.description = data.description
task.is_completed = data.is_completed
task.updated_at = datetime.utcnow()
session.commit()
```

### Delete Task (User-Scoped)

```python
task = ...  # Query with user_id filter
session.delete(task)
session.commit()
```

## Migration Strategy

Using Alembic for database migrations:

1. Initial migration creates `task` table
2. Future migrations can add indexes or constraints
3. Always backward-compatible for zero-downtime deployments
