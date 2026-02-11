# Data Model & Tool Schemas: MCP Server & Todo Tooling

**Feature**: MCP Server & Todo Tooling
**Created**: 2026-01-16
**Status**: Design Phase

## Overview

This document defines the data model, tool schemas, and data flow for the MCP server. The server exposes 5 tools (`add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`) that AI agents invoke to perform todo task operations. All tools follow a consistent pattern: JWT authentication → validation → database operation → structured response.

## Entity Models

**Note**: The MCP server uses existing SQLModel entities from the backend. No new database models are created.

### Task (Existing Model)

**Source**: `backend/src/models/task.py`

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False, min_length=1)
    description: Optional[str] = Field(default=None, nullable=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Attributes**:
- `id`: Unique task identifier (UUID4)
- `user_id`: Owner user identifier (foreign key conceptually, not enforced)
- `title`: Task title (1-255 characters, required)
- `description`: Optional task description (text, nullable)
- `is_completed`: Completion status (boolean, defaults to false)
- `created_at`: Creation timestamp (auto-set)
- `updated_at`: Last modification timestamp (auto-updated)

**Relationships**: Task belongs to User (via user_id field, no explicit foreign key constraint)

**Validation Rules**:
- Title: Required, 1-255 characters
- Description: Optional, no length limit
- User_id: Must match JWT token user_id for all operations

**State Transitions**:
- Created → is_completed=false
- Marked complete → is_completed=true
- Updated → updated_at refreshed
- Deleted → record removed from database

### User (Existing Model)

**Source**: `backend/src/models/user.py`

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Usage in MCP Server**: User model is referenced only for user_id validation. MCP tools do not create or modify users - they only verify that the user_id from the JWT token exists (implicitly, via JWT validation).

## MCP Tool Schemas

All tools follow this structure:
- **Input Schema**: JSON Schema defining required/optional parameters
- **Output Schema**: JSON Schema defining success response structure
- **Error Responses**: Structured error objects for validation, authentication, authorization, and database errors

### Common Patterns

**Authentication Pattern** (all tools):
```json
{
  "jwt_token": {
    "type": "string",
    "description": "JWT authentication token with user identity"
  }
}
```

**Error Response Pattern** (all tools):
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object or null"
  }
}
```

**Error Codes**:
- `AUTHENTICATION_ERROR`: Missing, invalid, or expired JWT token
- `AUTHORIZATION_ERROR`: User attempting to access another user's data
- `VALIDATION_ERROR`: Invalid input parameters (empty title, bad UUID, etc.)
- `NOT_FOUND_ERROR`: Task ID doesn't exist or doesn't belong to user
- `DATABASE_ERROR`: Database connection or query failure

---

## Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "jwt_token": {
      "type": "string",
      "description": "JWT authentication token"
    },
    "title": {
      "type": "string",
      "description": "Task title (1-255 characters)",
      "minLength": 1,
      "maxLength": 255
    },
    "description": {
      "type": "string",
      "description": "Optional task description"
    }
  },
  "required": ["jwt_token", "title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "user_id": {"type": "string", "format": "uuid"},
    "title": {"type": "string"},
    "description": {"type": ["string", "null"]},
    "is_completed": {"type": "boolean"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"}
  },
  "required": ["id", "user_id", "title", "description", "is_completed", "created_at", "updated_at"]
}
```

**Data Flow**:
1. AI agent calls `add_task` with jwt_token, title, optional description
2. MCP server validates JWT → extracts user_id from `sub` claim
3. Server validates title (1-255 chars, not empty)
4. Server creates Task record with user_id, title, description, is_completed=false
5. Server commits to database, refreshes to get auto-generated id/timestamps
6. Server returns task object as structured JSON
7. On error: returns error object with appropriate code/message

**Example Success Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": null,
  "is_completed": false,
  "created_at": "2026-01-16T20:30:00Z",
  "updated_at": "2026-01-16T20:30:00Z"
}
```

---

## Tool 2: list_tasks

**Purpose**: Retrieve tasks for the authenticated user with optional filtering and pagination

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "jwt_token": {"type": "string", "description": "JWT authentication token"},
    "completed": {"type": "boolean", "description": "Filter by completion status (optional)"},
    "page": {"type": "integer", "description": "Page number (1-indexed)", "minimum": 1, "default": 1},
    "page_size": {"type": "integer", "description": "Items per page", "minimum": 1, "maximum": 100, "default": 20}
  },
  "required": ["jwt_token"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "format": "uuid"},
          "user_id": {"type": "string", "format": "uuid"},
          "title": {"type": "string"},
          "description": {"type": ["string", "null"]},
          "is_completed": {"type": "boolean"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    "total": {"type": "integer", "description": "Total number of tasks matching filter"},
    "page": {"type": "integer", "description": "Current page number"},
    "page_size": {"type": "integer", "description": "Items per page"},
    "total_pages": {"type": "integer", "description": "Total number of pages"}
  },
  "required": ["items", "total", "page", "page_size", "total_pages"]
}
```

**Data Flow**:
1. AI agent calls `list_tasks` with jwt_token and optional filters
2. MCP server validates JWT → extracts user_id
3. Server validates pagination parameters (page ≥ 1, page_size 1-100)
4. Server builds query: `SELECT * FROM task WHERE user_id = ? [AND is_completed = ?] ORDER BY created_at DESC`
5. Server counts total matching tasks
6. Server applies offset/limit for pagination
7. Server executes query, converts tasks to dict format
8. Server calculates total_pages and returns paginated response

**Example Success Response**:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": null,
      "is_completed": false,
      "created_at": "2026-01-16T20:30:00Z",
      "updated_at": "2026-01-16T20:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## Tool 3: update_task

**Purpose**: Modify task title, description, or completion status

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "jwt_token": {"type": "string", "description": "JWT authentication token"},
    "task_id": {"type": "string", "format": "uuid", "description": "Task ID to update"},
    "title": {"type": "string", "description": "New title (1-255 chars, optional)", "minLength": 1, "maxLength": 255},
    "description": {"type": "string", "description": "New description (optional)"},
    "is_completed": {"type": "boolean", "description": "New completion status (optional)"}
  },
  "required": ["jwt_token", "task_id"]
}
```

**Output Schema**: Same as add_task output (full task object)

**Data Flow**:
1. AI agent calls `update_task` with jwt_token, task_id, and fields to update
2. MCP server validates JWT → extracts user_id
3. Server validates task_id format (UUID)
4. Server queries task: `SELECT * FROM task WHERE id = ? AND user_id = ?`
5. If task not found or user_id mismatch → return NOT_FOUND or AUTHORIZATION error
6. Server applies updates to retrieved task object
7. Server validates updated title if provided (1-255 chars, not empty)
8. Server updates updated_at timestamp
9. Server commits changes, refreshes task
10. Server returns updated task object

**Example Success Response**: Same structure as add_task

---

## Tool 4: complete_task

**Purpose**: Mark a task as completed (specialized update operation)

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "jwt_token": {"type": "string", "description": "JWT authentication token"},
    "task_id": {"type": "string", "format": "uuid", "description": "Task ID to mark complete"}
  },
  "required": ["jwt_token", "task_id"]
}
```

**Output Schema**: Same as add_task output (full task object with is_completed=true)

**Data Flow**:
1. AI agent calls `complete_task` with jwt_token and task_id
2. MCP server validates JWT → extracts user_id
3. Server queries task: `SELECT * FROM task WHERE id = ? AND user_id = ?`
4. If task not found or user_id mismatch → return error
5. Server sets is_completed = true
6. Server updates updated_at timestamp
7. Server commits, refreshes, returns task (idempotent if already completed)

**Idempotency**: Calling complete_task on an already-completed task succeeds and returns the task unchanged.

---

## Tool 5: delete_task

**Purpose**: Permanently remove a task from the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "jwt_token": {"type": "string", "description": "JWT authentication token"},
    "task_id": {"type": "string", "format": "uuid", "description": "Task ID to delete"}
  },
  "required": ["jwt_token", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "deleted": {"type": "boolean", "description": "Always true on success"},
    "task_id": {"type": "string", "format": "uuid", "description": "ID of deleted task"}
  },
  "required": ["deleted", "task_id"]
}
```

**Data Flow**:
1. AI agent calls `delete_task` with jwt_token and task_id
2. MCP server validates JWT → extracts user_id
3. Server queries task: `SELECT * FROM task WHERE id = ? AND user_id = ?`
4. If task not found or user_id mismatch → return error
5. Server deletes task: `DELETE FROM task WHERE id = ?`
6. Server commits deletion
7. Server returns success confirmation

**Example Success Response**:
```json
{
  "deleted": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Note**: Calling delete_task on a non-existent task returns NOT_FOUND error (not idempotent from success perspective, but safe to retry).

---

## Authentication & Authorization Flow

### JWT Token Validation

**Process**:
1. Tool receives `jwt_token` parameter
2. Server calls `auth_service.decode_token(jwt_token)`
3. JWT library validates signature using `settings.jwt_secret`
4. JWT library checks expiration (`exp` claim vs current time)
5. If valid → extract `user_id` from `sub` claim
6. If invalid/expired → raise AUTHENTICATION_ERROR

**Token Structure** (from existing backend):
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "type": "access",
  "exp": 1705437600,
  "iat": 1705437000
}
```

### User Isolation Enforcement

**Query Pattern** (all read/write operations):
```python
# Always filter by user_id from JWT
task = await session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()

# Never query without user_id filter:
task = await session.exec(select(Task).where(Task.id == task_id)).first()  # ❌ WRONG
```

**Authorization Checks**:
- Task retrieval: If `task.user_id != user_id` from JWT → NOT_FOUND (never reveal existence)
- Task update: If task not found with user_id filter → AUTHORIZATION or NOT_FOUND
- Task delete: If task not found with user_id filter → AUTHORIZATION or NOT_FOUND

**Defense in Depth**: User isolation enforced at:
1. **Tool Layer**: JWT validation before any logic
2. **Query Layer**: All queries scoped to user_id from JWT
3. **Response Layer**: Never expose tasks from other users

---

## Error Handling Matrix

| Error Type | HTTP Equivalent | Code | When Triggered | User-Facing Message |
|------------|-----------------|------|----------------|---------------------|
| Missing JWT | 401 | AUTHENTICATION_ERROR | jwt_token not in arguments | "Authentication required" |
| Invalid JWT | 401 | AUTHENTICATION_ERROR | Token signature invalid | "Invalid authentication token" |
| Expired JWT | 401 | AUTHENTICATION_ERROR | Token exp < now | "Authentication token expired" |
| Invalid UUID | 400 | VALIDATION_ERROR | task_id not valid UUID | "Invalid task ID format" |
| Empty Title | 400 | VALIDATION_ERROR | title is empty or whitespace | "Task title is required" |
| Title Too Long | 400 | VALIDATION_ERROR | title > 255 chars | "Task title must be 255 characters or less" |
| Task Not Found | 404 | NOT_FOUND_ERROR | No task with ID for user | "Task not found" |
| Wrong User | 403 | AUTHORIZATION_ERROR | Task belongs to different user | "Task not found" (intentionally vague) |
| DB Connection | 500 | DATABASE_ERROR | Cannot connect to database | "An error occurred, please try again" |
| DB Query Error | 500 | DATABASE_ERROR | SQL error during query | "An error occurred, please try again" |

**Error Response Format** (consistent across all tools):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Task title is required",
    "details": null
  }
}
```

**Security Principle**: Never leak information about other users' data. Return "Task not found" for both non-existent tasks and tasks belonging to other users.

---

## Data Flow Diagrams

### Add Task Flow
```
AI Agent → MCP Tool (add_task)
         ↓ jwt_token, title, description
     JWT Validation (extract user_id)
         ↓
     Input Validation (title 1-255 chars)
         ↓
     Create Task(user_id, title, description, is_completed=false)
         ↓
     Database INSERT
         ↓
     Refresh (get id, timestamps)
         ↓
     Return Task Object
         ↓
     AI Agent (receives created task)
```

### List Tasks Flow
```
AI Agent → MCP Tool (list_tasks)
         ↓ jwt_token, completed?, page, page_size
     JWT Validation (extract user_id)
         ↓
     Validate Pagination (page ≥ 1, size 1-100)
         ↓
     Build Query (WHERE user_id = ? [AND is_completed = ?])
         ↓
     Count Total Matching Tasks
         ↓
     Apply Offset/Limit (pagination)
         ↓
     Database SELECT
         ↓
     Convert Tasks to Dict List
         ↓
     Calculate total_pages
         ↓
     Return {items, total, page, page_size, total_pages}
         ↓
     AI Agent (receives paginated task list)
```

### Update/Complete/Delete Task Flow
```
AI Agent → MCP Tool (update/complete/delete)
         ↓ jwt_token, task_id, [updates]
     JWT Validation (extract user_id)
         ↓
     Validate task_id (UUID format)
         ↓
     Query Task (WHERE id = ? AND user_id = ?)
         ↓
     If Not Found → Return NOT_FOUND Error
         ↓
     Apply Operation (update fields / set completed / delete)
         ↓
     Database UPDATE/DELETE
         ↓
     Commit Changes
         ↓
     Return Updated Task / Success Confirmation
         ↓
     AI Agent (receives result)
```

---

## Database Schema (Existing - No Changes)

**Tables Used**:
- `task` (existing) - All 5 tools interact with this table
- `user` (existing) - Referenced implicitly via JWT user_id validation

**Indexes Used**:
- `task.id` (primary key) - Used by update/complete/delete lookups
- `task.user_id` (index) - Used by all queries for user isolation
- `user.id` (primary key) - Used by JWT validation (implicitly)

**No Schema Migrations Required**: MCP server uses existing schema without modifications.

---

## Concurrency & State Management

**Stateless Operation**:
- MCP server maintains zero in-memory state between tool invocations
- Each tool call is independent (new database session)
- Server restart does not affect tool behavior
- Connection pool managed by lifespan context (not per-invocation state)

**Concurrency Model**:
- Optimistic concurrency (last write wins)
- No pessimistic locks or version fields required for MVP
- Database handles concurrent writes via transaction isolation
- Risk: Simultaneous updates to same task may result in lost updates (acceptable for MVP)

**Thread Safety**:
- All tool handlers are async (no shared mutable state)
- Database sessions are request-scoped (not shared)
- No global variables or caches

---

## Performance Considerations

**Query Optimization**:
- All queries filter by `user_id` (uses existing index)
- List tasks: Single query with LIMIT/OFFSET (efficient pagination)
- Task lookups: Primary key + user_id filter (fast indexed lookup)

**Expected Performance** (from success criteria):
- List tasks (100 items): < 500ms
- Add/update/delete single task: < 200ms
- JWT validation (rejection): < 50ms

**No Caching**: MCP server does not cache task data (stateless requirement). AI agents may implement caching if needed.

---

## Summary

The MCP server data model is straightforward: 5 tools operating on existing Task/User entities with consistent JWT authentication, validation, and error handling patterns. All tools enforce user isolation at both the authentication and query layers, providing defense in depth. The stateless architecture ensures deterministic behavior and horizontal scalability.

**Key Design Principles**:
1. **Reuse Existing Models**: No new entities, import from backend
2. **Consistent Auth**: JWT validation on every tool call
3. **User Isolation**: All queries scoped to user_id from JWT
4. **Structured I/O**: JSON schemas for inputs/outputs
5. **Graceful Errors**: Structured error responses, never leak info
6. **Stateless Operation**: No in-memory state, session-per-invocation
