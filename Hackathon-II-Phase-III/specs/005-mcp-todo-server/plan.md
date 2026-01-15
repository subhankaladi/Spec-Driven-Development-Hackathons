# Implementation Plan: MCP Server & Todo Tooling

**Branch**: `005-mcp-todo-server` | **Date**: 2026-01-10 | **Spec**: [spec.md](../005-mcp-todo-server/spec.md)
**Input**: Feature specification from `/specs/005-mcp-todo-server/spec.md`

## Summary

This plan defines the implementation of an MCP (Model Context Protocol) server that exposes Todo CRUD operations as tools for AI agents. The server follows the constitution's "Tool-driven AI" and "Fully Stateless Server Architecture" principles, ensuring all tool calls are authenticated via JWT and enforce strict user-task ownership. The implementation uses the Official MCP SDK and SQLModel for database interactions with Neon PostgreSQL.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP SDK, SQLModel, FastAPI (for optional health endpoints)
**Storage**: Neon Serverless PostgreSQL (via SQLModel)
**Testing**: pytest, MCP testing utilities
**Target Platform**: Linux server (stateless MCP server process)
**Project Type**: MCP Server (backend service exposing tools)
**Performance Goals**: Tool execution under 50ms (excluding DB latency)
**Constraints**: Stateless, JWT-verified per call, PostgreSQL-backed, no in-memory session state
**Scale/Scope**: 5 tools, single-tenant data isolation via user_id

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec-Driven Development | ✅ PASS | Spec complete, following plan→tasks→implementation |
| Tool-driven AI (MCP) | ✅ PASS | MCP server will expose exactly 5 tools per spec |
| Fully Stateless Server Architecture | ✅ PASS | No in-memory state; all data via PostgreSQL |
| Database-backed Conversation Memory | ✅ PASS | Task data persisted in Neon PostgreSQL |
| Security & Statelessness | ✅ PASS | JWT validation enforced per tool call |
| Stack & Logic (AI-Centric) | ✅ PASS | Using Official MCP SDK and SQLModel |

**Gate Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-todo-server/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (MCP SDK patterns, JWT transport)
├── data-model.md        # Phase 1 output (Task entity schema)
├── quickstart.md        # Phase 1 output (server startup and testing)
├── contracts/           # Phase 1 output (MCP tool schemas)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py           # MCP server initialization
│       ├── tools/              # Tool implementations
│       │   ├── __init__.py
│       │   ├── add_task.py
│       │   ├── list_tasks.py
│       │   ├── update_task.py
│       │   ├── complete_task.py
│       │   └── delete_task.py
│       ├── auth.py             # JWT validation per call
│       └── models/             # SQLModel entities
│           ├── __init__.py
│           └── task.py
└── tests/
    ├── mcp/
    │   └── test_tools.py       # MCP tool tests
    └── conftest.py
```

**Structure Decision**: MCP server lives in `backend/src/mcp_server/` following the existing Python package structure. Tools are modularized for independent testing.

## Phase 0: Research & Unknown Resolution

### Open Questions (NEEDS CLARIFICATION)

| ID | Question | Research Required |
|----|----------|-------------------|
| Q1 | How is JWT passed to MCP tools? | MCP SDK authentication context patterns |
| Q2 | MCP tool response schema format? | Official MCP SDK tool result specifications |
| Q3 | Neon connection pooling strategy? | SQLModel + asyncpg with Neon Serverless |

### Research Tasks

- **R1**: "Research MCP SDK authentication and context passing for JWT tokens in Python"
- **R2**: "Research MCP tool response schema format for structured data returns"
- **R3**: "Research SQLModel async patterns with Neon Serverless PostgreSQL connection handling"

---

## Phase 1: Design

*Prerequisites: research.md complete*

### Data Model Design

**Task Entity**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table, indexed)
- `title`: String(255), not null
- `description`: String(2000), nullable
- `is_completed`: Boolean, default False
- `created_at`: DateTime, auto-set on creation
- `updated_at`: DateTime, auto-update on modification

**Indexes**:
- Primary key: `id`
- User lookup: `idx_task_user_id` on `user_id`
- List filter: `idx_task_user_completed` on `(user_id, is_completed)`

### Tool Schemas (MCP Protocol)

**add_task**:
```json
{
  "name": "add_task",
  "description": "Create a new task for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "maxLength": 255, "description": "Task title (required)"},
      "description": {"type": "string", "maxLength": 2000, "description": "Optional task description"}
    },
    "required": ["title"]
  }
}
```

**list_tasks**:
```json
{
  "name": "list_tasks",
  "description": "List all tasks for the authenticated user, optionally filtered by completion status",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter_completed": {"type": "boolean", "description": "If true, return only completed tasks; if false, only incomplete; if omitted, return all"}
    }
  }
}
```

**update_task**:
```json
{
  "name": "update_task",
  "description": "Update the title or description of a task owned by the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string", "format": "uuid", "description": "Task UUID to update"},
      "title": {"type": "string", "maxLength": 255, "description": "New task title (optional)"},
      "description": {"type": "string", "maxLength": 2000, "description": "New task description (optional)"}
    },
    "required": ["task_id"]
  }
}
```

**complete_task**:
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string", "format": "uuid", "description": "Task UUID to complete"}
    },
    "required": ["task_id"]
  }
}
```

**delete_task**:
```json
{
  "name": "delete_task",
  "description": "Delete a task owned by the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string", "format": "uuid", "description": "Task UUID to delete"}
    },
    "required": ["task_id"]
  }
}
```

### Error Response Format

All tools return errors in standardized format:
```json
{
  "success": false,
  "error": {
    "code": "AUTH_ERROR | NOT_FOUND | VALIDATION_ERROR | INTERNAL_ERROR",
    "message": "Human-readable error message"
  }
}
```

### Authentication Flow

1. MCP client connects with JWT in initialization context
2. Server extracts and validates JWT on each tool call
3. `user_id` extracted from JWT claims
4. All database queries filtered by `user_id` for ownership enforcement

---

## Phase 2: Next Steps

- Run `/sp.tasks` to generate implementation tasks
- Implement SQLModel Task entity and database setup
- Implement JWT validation utility
- Implement each MCP tool with ownership enforcement
- Write pytest tests for each tool
- Validate with MCP inspector

---

*Plan created 2026-01-10. Next: /sp.tasks*
