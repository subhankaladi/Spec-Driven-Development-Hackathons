# Feature Specification: MCP Server & Todo Tooling

**Feature Branch**: `005-mcp-todo-server`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description: "Spec-5: MCP Server & Todo Tooling. Specify the MCP server responsible for exposing Todo operations as tools. Define: Official MCP SDK server setup, Stateless MCP tool architecture, Tool schemas, parameters, and return formats, Database-backed task operations via SQLModel, JWT-authenticated user identity enforcement. Required MCP tools: add_task, list_tasks, update_task, complete_task, delete_task. Tool rules: Tools must be stateless, Tools must not rely on in-memory state, User ID must be validated for every tool call, All operations must enforce task ownership. Out of scope: AI agent reasoning logic, Chat endpoint, Frontend UI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Tasks via MCP Tools (Priority: P1)

As an AI agent, I want to manage a user's tasks using high-level MCP tools so that I can accurately fulfill natural language requests like "Add a grocery shopping task" or "Show my pending todos."

**Why this priority**: Core functionality of the Phase III chatbot depends on the AI being able to interact with the task database through a standardized tool interface.

**Independent Test**: Can be fully tested by invoking the MCP tools via an MCP inspector or test client and verifying that the database state changes correctly for the authenticated user.

**Acceptance Scenarios**:

1. **Given** a valid JWT for user A, **When** the `add_task` tool is called with title "Buy milk", **Then** a new task is created in the database owned by user A.
2. **Given** tasks exist for user A and user B, **When** user A calls `list_tasks`, **Then** only user A's tasks are returned.
3. **Given** user A's task ID, **When** user B attempts to `delete_task` using that ID, **Then** the operation is rejected with an "Unauthorized" or "Not Found" error.

---

### User Story 2 - Automated Task Completion (Priority: P2)

As an AI agent, I want to quickly mark tasks as complete via an MCP tool so that I can respond to "Check off my meeting task" without manual database manipulation.

**Why this priority**: Frequently requested action that must be handled safely and efficiently by the agent.

**Independent Test**: Invoke `complete_task` with a specific ID and verify the `is_completed` flag is set to true in the DB.

**Acceptance Scenarios**:

1. **Given** an incomplete task owned by user A, **When** `complete_task` is called with its ID and user A's credentials, **Then** the task status is updated to completed.

---

## Edge Cases

- **Invalid JWT**: What happens when a tool is called with a malformed or expired token? (Should return standardized auth error)
- **Non-existent IDs**: How does system handle `update_task` with an ID that doesn't exist? (Should return 404/Not Found)
- **Concurrent Updates**: How are race conditions handled if two tool calls update the same task? (SQLModel/PostgreSQL default transaction isolation)
- **Extreme Input**: What happens when `add_task` is called with a massive title string? (Validate length constraints)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement an MCP server using the Official MCP SDK.
- **FR-002**: System MUST expose exactly five tools: `add_task`, `list_tasks`, `update_task`, `complete_task`, and `delete_task`.
- **FR-003**: System MUST validate the user identity from a JWT provided in the context of every tool call.
- **FR-004**: System MUST enforce strict task ownership; tools must only operate on tasks belonging to the authenticated user.
- **FR-005**: MCP tools MUST be fully stateless, retrieving/persisting all data via Neon PostgreSQL using SQLModel.
- **FR-006**: Tools MUST return standardized success/error payloads compatible with the MCP protocol.

### Key Entities

- **Task**: Represents a todo item. Attributes: `id` (UUID), `user_id` (Owner), `title` (String), `description` (Optional String), `is_completed` (Boolean), `created_at` (Timestamp).
- **UserContext**: Derived from JWT. Attributes: `user_id`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of tool calls must fail if provided with an invalid or missing user identifier.
- **SC-002**: 0 instances of cross-user data leakage (User A accessing User B's tasks) during automated test suites.
- **SC-003**: Tool execution time (excluding DB latency) should be under 50ms.
- **SC-004**: MCP server correctly registers all 5 tools with descriptions and JSON schemas upon startup.

## Assumptions

- **JWT Validation**: The MCP server will receive the JWT via a standardized transport header or context property (to be defined in plan).
- **Database Connection**: Neon PostgreSQL connection details are provided via environment variables as per constitution.
- **Schema**: The `Task` table already exists or will be managed via SQLModel migrations.
