# Feature Specification: MCP Server & Todo Tooling

**Feature Branch**: `005-mcp-server-todo-tooling`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Spec-4: MCP Server & Todo Tooling - Specify the MCP server responsible for exposing Todo operations as tools."

## User Scenarios & Testing *(mandatory)*

**Context**: This feature provides a Model Context Protocol (MCP) server that exposes todo task operations as standardized tools. The "users" of this system are AI agents that will invoke these tools to perform task management operations on behalf of end users.

### User Story 1 - Add Task Tool (Priority: P1)

An AI agent needs to create a new task for a user based on natural language input. The agent invokes the `add_task` tool with task details (title, optional description) and user authentication context. The tool validates the user's identity, persists the task to the database, and returns the created task with its unique ID.

**Why this priority**: Task creation is the most fundamental operation. Without the ability to add tasks, the system provides no value. This is the core building block for all other operations.

**Independent Test**: Can be fully tested by having an AI agent invoke the `add_task` tool with valid user credentials and task data, then verifying the task appears in the database with correct user_id association and returns a valid task object with ID.

**Acceptance Scenarios**:

1. **Given** an authenticated user context with valid JWT token, **When** the AI agent calls `add_task` with title "Buy groceries" and no description, **Then** a task is created in the database with the user's ID, returns task object with generated UUID, title, empty description, and is_completed=false
2. **Given** an authenticated user context, **When** the AI agent calls `add_task` with title "Team meeting" and description "Discuss Q1 roadmap", **Then** both title and description are persisted and returned in the task object
3. **Given** an unauthenticated or invalid user context, **When** the AI agent attempts to call `add_task`, **Then** the tool rejects the request with authentication error before database access
4. **Given** a valid user context, **When** the AI agent calls `add_task` with an empty title, **Then** the tool rejects the request with validation error (title required, 1-255 chars)

---

### User Story 2 - List Tasks Tool (Priority: P1)

An AI agent needs to retrieve all tasks for a user to answer questions like "What are my tasks?" or "Show my incomplete tasks". The agent invokes the `list_tasks` tool with user authentication context and optional filters (completion status, pagination). The tool validates user identity, queries user-scoped tasks from the database, and returns a list of task objects.

**Why this priority**: Tied with task creation as P1 because viewing tasks is equally fundamental. Users need to see their tasks before they can update or complete them. This enables the AI to answer questions about existing tasks.

**Independent Test**: Can be fully tested by pre-populating the database with tasks for a specific user, having the AI agent invoke `list_tasks` with that user's credentials, and verifying only that user's tasks are returned in the expected format.

**Acceptance Scenarios**:

1. **Given** a user with 3 tasks in the database (2 incomplete, 1 complete), **When** the AI agent calls `list_tasks` with no filters, **Then** all 3 tasks are returned as an array of task objects with correct user_id
2. **Given** a user with multiple tasks, **When** the AI agent calls `list_tasks` with filter `completed=false`, **Then** only incomplete tasks are returned
3. **Given** a user with 25 tasks, **When** the AI agent calls `list_tasks` with `page=2, page_size=10`, **Then** tasks 11-20 are returned with pagination metadata (total count, page info)
4. **Given** User A's tasks exist in the database, **When** the AI agent calls `list_tasks` with User B's credentials, **Then** only User B's tasks are returned (User A's tasks are never exposed)
5. **Given** a user with no tasks, **When** the AI agent calls `list_tasks`, **Then** an empty array is returned (not an error)

---

### User Story 3 - Complete Task Tool (Priority: P2)

An AI agent needs to mark a task as complete when the user says "Mark task X as done" or "I finished the grocery shopping". The agent invokes the `complete_task` tool with the task ID and user context. The tool validates user identity, verifies task ownership, updates the task's completion status to true, and returns the updated task.

**Why this priority**: P2 because it's a specialized form of update. While important for task management workflows, it's technically covered by the more general `update_task` tool. However, it provides a simpler interface for the common "mark done" operation.

**Independent Test**: Can be fully tested by creating a task for a user, having the AI agent invoke `complete_task` with that task's ID and user's credentials, then verifying the task's `is_completed` field is set to true in the database and the updated task is returned.

**Acceptance Scenarios**:

1. **Given** an incomplete task owned by User A, **When** the AI agent calls `complete_task` with the task ID and User A's credentials, **Then** the task's `is_completed` field is set to true and updated_at timestamp is refreshed
2. **Given** a task that is already completed, **When** the AI agent calls `complete_task` on it, **Then** the operation succeeds idempotently (no error, task remains completed)
3. **Given** a task owned by User A, **When** the AI agent calls `complete_task` with User B's credentials, **Then** the tool rejects with authorization error (forbidden)
4. **Given** a non-existent task ID, **When** the AI agent calls `complete_task`, **Then** the tool returns a not found error

---

### User Story 4 - Update Task Tool (Priority: P2)

An AI agent needs to modify task details when the user says "Change the meeting title to Product Review" or "Add description to my grocery task". The agent invokes the `update_task` tool with the task ID, updated fields (title, description, completion status), and user context. The tool validates user identity and ownership, applies the updates, and returns the modified task.

**Why this priority**: P2 because it's essential for task management but builds on the foundation of add/list (P1). Users need to create and view tasks before they can update them.

**Independent Test**: Can be fully tested by creating a task, having the AI agent invoke `update_task` to change the title or description, then verifying the changes are persisted in the database and reflected in the returned task object.

**Acceptance Scenarios**:

1. **Given** a task with title "Meeting" owned by User A, **When** the AI agent calls `update_task` with new title "Product Review Meeting" and User A's credentials, **Then** only the title is updated, other fields remain unchanged, and updated_at timestamp is refreshed
2. **Given** a task with no description, **When** the AI agent calls `update_task` to add description "Discuss Q1 goals", **Then** the description is added while preserving other fields
3. **Given** a task owned by User A, **When** the AI agent calls `update_task` with User B's credentials, **Then** the tool rejects with authorization error
4. **Given** a task, **When** the AI agent calls `update_task` with an empty title, **Then** the tool rejects with validation error (title required)
5. **Given** a task, **When** the AI agent calls `update_task` with no fields to update, **Then** the tool returns the task unchanged (no database write)

---

### User Story 5 - Delete Task Tool (Priority: P3)

An AI agent needs to permanently remove a task when the user says "Delete the grocery task" or "Remove all my completed tasks". The agent invokes the `delete_task` tool with the task ID and user context. The tool validates user identity and ownership, removes the task from the database, and confirms deletion.

**Why this priority**: P3 because deletion is less frequently used than creation, viewing, and updating. Many users archive or complete tasks rather than delete them. It's important for data hygiene but not critical for MVP functionality.

**Independent Test**: Can be fully tested by creating a task, having the AI agent invoke `delete_task` with the task ID and user credentials, then verifying the task no longer exists in the database and subsequent attempts to retrieve it return not found.

**Acceptance Scenarios**:

1. **Given** a task owned by User A, **When** the AI agent calls `delete_task` with the task ID and User A's credentials, **Then** the task is permanently removed from the database and a success confirmation is returned
2. **Given** a task owned by User A, **When** the AI agent calls `delete_task` with User B's credentials, **Then** the tool rejects with authorization error (task not found or forbidden)
3. **Given** a non-existent task ID, **When** the AI agent calls `delete_task`, **Then** the tool returns a not found error
4. **Given** a task that was just deleted, **When** the AI agent calls `delete_task` again with the same ID, **Then** the tool returns a not found error (idempotent from caller perspective)

---

### Edge Cases

- What happens when a tool is invoked with a malformed JWT token? Tool must reject with authentication error before any database access.
- What happens when a tool is invoked without a JWT token? Tool must reject with authentication error.
- What happens when the JWT token is valid but the user_id doesn't exist in the database? Tool should still proceed if the operation is valid (e.g., adding a task for a valid JWT user who hasn't been explicitly created in the User table yet, assuming JWT validation is the source of truth).
- What happens when pagination parameters are invalid (negative page, page_size > 100)? Tool should return validation error with clear message.
- What happens when database connection fails during a tool invocation? Tool should return a 500-level error with generic message (no internal details leaked).
- What happens when two agents try to update the same task simultaneously? Last write wins (optimistic concurrency). No locking required for MVP.
- What happens when a task title exceeds 255 characters? Tool should reject with validation error.
- What happens when filter parameters for `list_tasks` are invalid (e.g., `completed="maybe"`)? Tool should return validation error or ignore invalid filters (use reasonable defaults).

## Requirements *(mandatory)*

### Functional Requirements

#### MCP Server Setup & Architecture

- **FR-001**: System MUST implement an MCP server using the Official MCP SDK (Python)
- **FR-002**: System MUST register all five required tools (`add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`) with the MCP server at startup
- **FR-003**: MCP server MUST expose tools via standard MCP protocol (stdio transport for local execution)
- **FR-004**: System MUST NOT maintain any in-memory state between tool invocations (fully stateless)
- **FR-005**: Each tool invocation MUST be independent and idempotent where applicable

#### Tool Authentication & Security

- **FR-006**: Every tool invocation MUST include a JWT token in the request context (passed via MCP protocol)
- **FR-007**: Every tool MUST validate the JWT token before any database operation
- **FR-008**: JWT validation MUST extract the user_id (from `sub` claim) and verify token signature and expiration
- **FR-009**: Tools MUST reject requests with missing, expired, or invalid JWT tokens with clear error messages
- **FR-010**: Every tool MUST enforce user isolation - operations can only access tasks owned by the authenticated user_id
- **FR-011**: Tools MUST NOT expose error details that could leak information about other users' data

#### Tool Schemas & Parameters

- **FR-012**: `add_task` tool MUST accept parameters: `title` (string, required, 1-255 chars), `description` (string, optional), and JWT token context
- **FR-013**: `add_task` tool MUST return: created task object with `id` (UUID), `user_id`, `title`, `description`, `is_completed` (false), `created_at`, `updated_at`
- **FR-014**: `list_tasks` tool MUST accept parameters: `completed` (boolean, optional filter), `page` (integer, default 1), `page_size` (integer, default 20, max 100), and JWT token context
- **FR-015**: `list_tasks` tool MUST return: array of task objects and pagination metadata (`total`, `page`, `page_size`, `total_pages`)
- **FR-016**: `update_task` tool MUST accept parameters: `task_id` (UUID, required), `title` (string, optional), `description` (string, optional), `is_completed` (boolean, optional), and JWT token context
- **FR-017**: `update_task` tool MUST return: updated task object with refreshed `updated_at` timestamp
- **FR-018**: `complete_task` tool MUST accept parameters: `task_id` (UUID, required) and JWT token context
- **FR-019**: `complete_task` tool MUST return: updated task object with `is_completed=true` and refreshed `updated_at`
- **FR-020**: `delete_task` tool MUST accept parameters: `task_id` (UUID, required) and JWT token context
- **FR-021**: `delete_task` tool MUST return: success confirmation (e.g., `{"deleted": true, "task_id": "..."}`)

#### Database Operations

- **FR-022**: All tools MUST interact with the database via SQLModel ORM (no raw SQL)
- **FR-023**: All tools MUST use the existing Task and User models from the current codebase
- **FR-024**: All database queries MUST filter by `user_id` from the validated JWT token
- **FR-025**: Tools MUST handle database errors gracefully and return appropriate error responses (not raw exceptions)
- **FR-026**: Task creation MUST generate UUIDs for task IDs (using UUID4)
- **FR-027**: Task creation and updates MUST automatically set/refresh `created_at` and `updated_at` timestamps

#### Error Handling & Validation

- **FR-028**: Tools MUST validate all input parameters before database operations
- **FR-029**: Tools MUST return structured error responses with: `error` (boolean), `code` (string), `message` (string)
- **FR-030**: Tools MUST distinguish between client errors (400-level: validation, authentication, authorization, not found) and server errors (500-level: database failures, unexpected errors)
- **FR-031**: Tools MUST NOT leak sensitive information in error messages (no stack traces, internal IDs, or SQL details)
- **FR-032**: Tools MUST handle these specific errors:
  - Authentication failure (invalid/missing JWT)
  - Authorization failure (user accessing another user's task)
  - Validation failure (invalid parameters)
  - Not found (task ID doesn't exist or doesn't belong to user)
  - Database errors (connection failures, constraint violations)

#### Tool Behavior & Consistency

- **FR-033**: All tools MUST be deterministic - same inputs produce same outputs
- **FR-034**: Tools MUST NOT depend on external services or APIs (only database)
- **FR-035**: Tool execution MUST complete within 5 seconds under normal conditions
- **FR-036**: Tools MUST be thread-safe (no shared mutable state)
- **FR-037**: `complete_task` and `delete_task` MUST be idempotent (repeating the same operation produces the same result)

### Key Entities

**Note**: This feature uses existing entities from the current codebase. No new database models are created.

- **Task**: Existing entity representing a todo item with attributes: `id` (UUID), `user_id` (UUID), `title` (string, 1-255 chars), `description` (optional string), `is_completed` (boolean), `created_at` (datetime), `updated_at` (datetime). Tools operate on this entity.
- **User**: Existing entity representing a user account. The `user_id` from JWT tokens references this entity. Tools do not create or modify users, only validate their existence via JWT.
- **MCP Tool**: Conceptual entity (not a database model) representing a callable function exposed via the MCP protocol. Each tool has a name, schema (parameters), and implementation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI agents can successfully create tasks through the MCP server with 100% success rate for valid inputs
- **SC-002**: AI agents can retrieve user-specific task lists with correct filtering and pagination in under 500ms for up to 100 tasks
- **SC-003**: Cross-user data access attempts are blocked 100% of the time (no data leakage between users)
- **SC-004**: Tool invocations with invalid authentication fail immediately (before database access) in under 50ms
- **SC-005**: All tool operations are deterministic - repeating the same operation 10 times produces identical results
- **SC-006**: MCP server remains stateless - server restart does not affect tool behavior or data consistency
- **SC-007**: Tool error messages are clear and actionable for AI agents (no cryptic codes or stack traces)
- **SC-008**: Tools handle 100 concurrent requests without data corruption or race conditions
- **SC-009**: All five required tools pass integration tests covering success and failure scenarios
- **SC-010**: MCP server startup completes in under 3 seconds and successfully registers all tools

## Assumptions

This specification makes the following assumptions based on industry standards and the existing codebase:

1. **JWT Token Format**: JWT tokens follow the existing application format with `sub` claim containing user_id, `email` claim, and standard `exp`/`iat` claims. The JWT secret is available via environment configuration.

2. **Database Connection**: The MCP server has access to the same Neon PostgreSQL database as the existing FastAPI backend. Database connection string is available via environment variables.

3. **MCP Transport**: The MCP server uses stdio transport (standard input/output) for local execution, which is the standard for MCP servers invoked by AI agents in development environments.

4. **Error Response Format**: Error responses follow the existing application convention with structured error objects containing `code`, `message`, and optional `details`.

5. **Pagination Defaults**: For `list_tasks`, reasonable defaults are `page=1`, `page_size=20`, `max_page_size=100`. These align with standard REST API pagination practices.

6. **Task Ownership Model**: Task ownership is determined solely by the `user_id` field in the Task table. The authenticated user_id from the JWT must match the task's user_id for update/delete operations.

7. **Tool Discovery**: AI agents will discover available tools through the MCP protocol's tool listing mechanism. No separate documentation or API endpoint is needed for tool discovery.

8. **Concurrent Access**: For MVP, optimistic concurrency (last write wins) is acceptable. No pessimistic locking or version fields required.

9. **Soft Delete**: Tasks are permanently deleted (hard delete). No soft delete or archive mechanism required for MVP.

10. **Tool Naming Convention**: Tool names use snake_case (`add_task`) as this is the Python convention and aligns with the MCP SDK examples.

## Out of Scope

Explicitly excluded from this feature:

- AI agent reasoning logic (handled by OpenAI Agents SDK in a separate component)
- Chat endpoint for user interaction (POST /api/{user_id}/chat - separate feature)
- Conversation state persistence in database (separate feature)
- Frontend UI for direct user interaction with MCP server (users interact via AI chat, not directly with MCP)
- User management tools (user creation, authentication handled by existing FastAPI backend)
- Task analytics or reporting tools (e.g., "get task statistics")
- Task search or advanced filtering (beyond completed/incomplete)
- Task sharing or collaboration features
- Task reminders or notifications
- Task categories, tags, or priorities
- Real-time updates or websockets
- Rate limiting or throttling (assumed to be handled at a higher level)
- Logging and monitoring infrastructure (use standard Python logging)
- Deployment configuration (Docker, K8s, etc.)
