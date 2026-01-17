# Implementation Plan: MCP Server & Todo Tooling

**Branch**: `005-mcp-server-todo-tooling` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-mcp-server-todo-tooling/spec.md`

## Summary

Build an MCP (Model Context Protocol) server that exposes 5 stateless, JWT-authenticated tools for AI agents to perform todo task operations. The server uses the Official MCP Python SDK with low-level API for precise control over tool schemas and validation. Tools interact with the existing Neon PostgreSQL database via SQLModel ORM, enforcing user isolation at both the tool invocation and database query layers. Authentication is handled via JWT token validation on every tool call, with user_id extraction from the `sub` claim. The server runs using stdio transport for local AI agent communication and maintains zero in-memory state between invocations.

**Technical Approach**: Implement MCP server in `/mcp-server/` directory using `mcp.server.lowlevel.Server` class with async tool handlers, lifespan context manager for database connection pooling, structured input/output schemas with JSON Schema validation, and comprehensive error handling following existing FastAPI error response patterns.

## Technical Context

**Language/Version**: Python 3.11+ (matching existing backend)
**Primary Dependencies**:
- `mcp` (modelcontextprotocol Python SDK) - Official MCP SDK for server implementation
- `sqlmodel` - Existing ORM for database operations
- `pyjwt` - JWT token validation (from existing auth service)
- `bcrypt` - Password hashing utilities (existing)
- `python-dotenv` - Environment configuration (existing)
- `asyncio` - Async runtime for MCP server

**Storage**: Neon Serverless PostgreSQL (shared with existing FastAPI backend)
**Testing**: pytest with async support (pytest-asyncio), integration tests with test database
**Target Platform**: Local development (stdio transport), deployable to Linux server
**Project Type**: Standalone MCP server (separate from web backend)
**Performance Goals**:
- Tool invocation: < 500ms for list operations (100 tasks)
- Authentication rejection: < 50ms
- Server startup: < 3 seconds
- Concurrent requests: 100 without data corruption

**Constraints**:
- Fully stateless (no in-memory state between tool calls)
- JWT validation before every database operation
- User-scoped queries only (no cross-user data access)
- Compatible with existing Task and User models
- Stdio transport for AI agent communication

**Scale/Scope**:
- 5 MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
- Single MCP server process
- Shared database with FastAPI backend (no schema changes)
- MVP focus: no caching, no rate limiting, optimistic concurrency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status | Notes |
|-----------|-------|--------|-------|
| **I. Spec-Driven Development** | Implementation follows approved spec | ✅ PASS | Spec.md defines all 5 tools with acceptance criteria |
| **II. Agentic Workflow Compliance** | Code generation via Claude Code agents | ✅ PASS | Will use Backend Agent for MCP server implementation |
| **III. Security-First Design** | JWT validation, user isolation enforced | ✅ PASS | JWT validation at tool layer, user_id scoped queries |
| **IV. Deterministic Behavior** | Tools are stateless and deterministic | ✅ PASS | No in-memory state, same input → same output |
| **V. Full-Stack Coherence** | Integrates with existing database/models | ✅ PASS | Uses existing SQLModel Task/User models, shared DB |
| **VI. Traceability** | PHRs for all iterations | ✅ PASS | Plan, tasks, implementation PHRs will be created |
| **VII. Natural Language Interface** | Enables AI conversational task management | ✅ PASS | MCP tools provide foundation for AI chat feature |
| **VIII. Tool-Driven AI Architecture** | AI acts via MCP tools, not direct DB access | ✅ PASS | This feature IS the tool layer for Phase III |
| **IX. Stateless Server Architecture** | No in-memory state, DB-backed persistence | ✅ PASS | MCP server is fully stateless by design |
| **X. User Identity at Tool Level** | JWT validation per tool invocation | ✅ PASS | Every tool validates JWT before DB operations |

**Constitution Compliance**: ✅ **ALL GATES PASSED** - No violations or justifications needed.

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-server-todo-tooling/
├── plan.md              # This file (Phase 1 output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 research findings (to be created)
├── data-model.md        # Tool schemas and data flow (Phase 1 output)
├── quickstart.md        # Developer guide for MCP server (Phase 1 output)
├── contracts/           # Tool interface definitions (Phase 1 output)
│   ├── add_task.json       # add_task tool schema
│   ├── list_tasks.json     # list_tasks tool schema
│   ├── update_task.json    # update_task tool schema
│   ├── complete_task.json  # complete_task tool schema
│   └── delete_task.json    # delete_task tool schema
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec validation (completed)
└── tasks.md             # Implementation tasks (Phase 2 - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
mcp-server/              # New standalone MCP server directory
├── src/
│   ├── server.py        # Main MCP server entry point
│   ├── tools/           # Tool handler implementations
│   │   ├── __init__.py
│   │   ├── add_task.py      # add_task tool handler
│   │   ├── list_tasks.py    # list_tasks tool handler
│   │   ├── update_task.py   # update_task tool handler
│   │   ├── complete_task.py # complete_task tool handler
│   │   └── delete_task.py   # delete_task tool handler
│   ├── schemas/         # Tool input/output JSON schemas
│   │   ├── __init__.py
│   │   └── tool_schemas.py  # Centralized schema definitions
│   ├── auth/            # Authentication and validation
│   │   ├── __init__.py
│   │   └── jwt_validator.py # JWT token validation
│   ├── db/              # Database connection and session management
│   │   ├── __init__.py
│   │   └── session.py   # SQLModel session factory
│   └── utils/           # Error handling and utilities
│       ├── __init__.py
│       └── errors.py    # Structured error responses
├── tests/               # MCP server tests
│   ├── __init__.py
│   ├── conftest.py      # Pytest fixtures (test DB, JWT tokens)
│   ├── unit/            # Unit tests for individual components
│   │   ├── test_jwt_validator.py
│   │   ├── test_add_task.py
│   │   ├── test_list_tasks.py
│   │   ├── test_update_task.py
│   │   ├── test_complete_task.py
│   │   └── test_delete_task.py
│   └── integration/     # End-to-end tool invocation tests
│       └── test_mcp_server.py
├── .env.example         # Environment variable template
├── requirements.txt     # Python dependencies
└── README.md            # MCP server documentation

backend/                 # Existing FastAPI backend (NO CHANGES)
├── src/
│   ├── models/          # Shared Task and User models (REUSED by MCP server)
│   │   ├── task.py      # Task SQLModel (used by MCP tools)
│   │   └── user.py      # User SQLModel (referenced for user_id validation)
│   ├── services/
│   │   └── auth_service.py  # JWT utilities (REUSED by MCP server)
│   └── config.py        # Settings (JWT secret, DB URL - REUSED)
└── ...                  # Other existing backend code (unchanged)
```

**Structure Decision**: Create new standalone `mcp-server/` directory at repository root, separate from the existing `backend/` FastAPI application. This separation follows the single responsibility principle - the MCP server serves AI agents via stdio transport, while FastAPI serves HTTP clients. The MCP server imports shared code (models, auth utilities, config) from the backend directory to avoid duplication. No changes to existing backend code are required.

**Rationale**:
- **Separation**: MCP server and FastAPI backend have different transport mechanisms (stdio vs HTTP), startup procedures, and lifecycles
- **Reusability**: Shared models and auth logic imported from backend ensures consistency
- **Independence**: MCP server can be developed, tested, and deployed separately
- **Scalability**: Future Phase III features (AI agent, chat endpoint) can coexist without coupling

## Complexity Tracking

> **No violations detected - this section intentionally left empty**

## Phase 0: Research & Unknowns

**Objective**: Resolve all technical unknowns and establish MCP SDK implementation patterns

###  Research Tasks

#### R1: MCP SDK Low-Level Server API

**Question**: How to implement MCP server using low-level API with precise control over tool schemas and async execution?

**Research Findings** (from Context7 MCP Python SDK docs):

**Decision**: Use `mcp.server.lowlevel.Server` class with decorator-based handler registration

**Implementation Pattern**:
```python
from mcp.server.lowlevel import Server
import mcp.types as types

server = Server("todo-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Register all available tools with input/output schemas."""
    return [types.Tool(...), ...]

@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> dict | list[types.TextContent]:
    """Route tool calls to appropriate handlers."""
    if name == "add_task":
        return await add_task_handler(arguments)
    # ... other tools
```

**Key Insights**:
- Low-level API provides fine-grained control over tool definitions
- Async handlers support database I/O without blocking
- Structured `outputSchema` validates return data against JSON Schema
- Server runs with stdio transport for AI agent communication

**Alternatives Considered**:
- FastMCP (high-level API): Rejected - less control over schemas, validation, and error handling
- Custom protocol: Rejected - MCP is standardized, no need to reinvent

---

#### R2: Lifespan Context for Database Connection Pooling

**Question**: How to manage database connections across multiple tool invocations without maintaining in-memory state?

**Research Findings** (from MCP SDK lifespan example):

**Decision**: Use lifespan context manager to initialize database connection pool at server startup

**Implementation Pattern**:
```python
from contextlib import asynccontextmanager
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

@asynccontextmanager
async def server_lifespan(_server: Server):
    """Initialize DB pool on startup, cleanup on shutdown."""
    engine = create_async_engine(settings.database_url, echo=False)
    try:
        yield {"db_engine": engine}
    finally:
        await engine.dispose()

server = Server("todo-mcp-server", lifespan=server_lifespan)

@server.call_tool()
async def handle_tool(name: str, arguments: dict):
    # Access lifespan context for each tool invocation
    ctx = server.request_context
    engine = ctx.lifespan_context["db_engine"]
    async with AsyncSession(engine) as session:
        # Perform database operations
        ...
```

**Key Insights**:
- Lifespan context initializes resources once at startup (not per-invocation)
- Each tool invocation creates a new database session (stateless)
- Connection pool is shared but sessions are request-scoped
- Cleanup happens automatically on server shutdown

**Alternatives Considered**:
- Global database connection: Rejected - not compatible with async context
- Per-invocation engine creation: Rejected - inefficient, slow startup

---

#### R3: JWT Token Validation from MCP Request Context

**Question**: How to pass and validate JWT tokens in MCP tool invocations?

**Research Findings** (from MCP SDK and existing backend auth service):

**Decision**: Pass JWT token as part of tool arguments, validate using existing `BetterAuthIntegration` class

**Implementation Pattern**:
```python
# In tool schema (inputSchema):
{
    "type": "object",
    "properties": {
        "jwt_token": {"type": "string", "description": "JWT authentication token"},
        "title": {"type": "string"},
        # ... other parameters
    },
    "required": ["jwt_token", ...]
}

# In tool handler:
from backend.src.services.auth_service import BetterAuthIntegration

auth_service = BetterAuthIntegration()

async def add_task_handler(arguments: dict):
    # Validate JWT and extract user_id
    token = arguments.get("jwt_token")
    if not token:
        raise ValueError("Missing jwt_token")

    token_data = auth_service.decode_token(token)
    if not token_data:
        raise ValueError("Invalid or expired token")

    user_id = token_data.user_id  # From 'sub' claim

    # Proceed with database operation scoped to user_id
    ...
```

**Key Insights**:
- JWT token passed as regular tool argument (not MCP protocol-level auth)
- Existing backend auth service can be reused for token validation
- User identity enforcement happens before any database access
- Token validation errors return structured error responses

**Alternatives Considered**:
- MCP protocol-level authentication: Rejected - not supported in current spec
- API key authentication: Rejected - JWT is already implemented and secure

---

#### R4: Structured Error Responses Following Existing Patterns

**Question**: How to return structured errors from MCP tools matching existing FastAPI error format?

**Research Findings** (from existing backend error schemas and MCP SDK):

**Decision**: Return structured error objects compatible with existing error response format

**Implementation Pattern**:
```python
# Existing FastAPI error format (from backend/src/api/schemas/errors.py):
{
    "error": {
        "code": "AUTHENTICATION_ERROR",
        "message": "Invalid or expired JWT token",
        "details": null
    }
}

# MCP tool error response:
from mcp.types import TextContent

async def handle_tool(name: str, arguments: dict):
    try:
        # Tool logic
        return {"result": "success", ...}  # Structured output
    except ValueError as e:
        # Return error as TextContent with JSON
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                    "details": None
                }
            })
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": None
                }
            })
        )]
```

**Key Insights**:
- MCP tools can return either structured data (dict) or TextContent (string)
- Error responses encoded as JSON strings in TextContent
- Maintain consistency with existing FastAPI error format
- AI agents can parse error JSON to understand failures

**Alternatives Considered**:
- Raise exceptions: Rejected - MCP protocol prefers graceful error responses
- Custom error schema: Rejected - consistency with existing backend is valuable

---

#### R5: Async SQLModel with Existing Models

**Question**: How to use existing SQLModel Task/User models with async database operations in MCP server?

**Research Findings** (from SQLModel docs and existing backend):

**Decision**: Import existing models, use `AsyncSession` with async queries

**Implementation Pattern**:
```python
from backend.src.models.task import Task
from backend.src.models.user import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

async def add_task_handler(arguments: dict, session: AsyncSession, user_id: UUID):
    # Create new task with existing Task model
    new_task = Task(
        user_id=user_id,
        title=arguments["title"],
        description=arguments.get("description"),
        is_completed=False
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # Return task as dict (for structured output)
    return {
        "id": str(new_task.id),
        "user_id": str(new_task.user_id),
        "title": new_task.title,
        "description": new_task.description,
        "is_completed": new_task.is_completed,
        "created_at": new_task.created_at.isoformat(),
        "updated_at": new_task.updated_at.isoformat()
    }
```

**Key Insights**:
- Existing models work with async sessions (no changes required)
- Use `await` for commit, refresh, and query execution
- Convert UUIDs and datetimes to strings for JSON serialization
- User-scoped queries use `.where(Task.user_id == user_id)`

**Alternatives Considered**:
- Synchronous SQLModel: Rejected - would block async MCP server event loop
- Copy models to MCP server: Rejected - violates DRY, creates drift

---

### Research Summary

All technical unknowns resolved. Implementation approach validated with official MCP SDK documentation and existing codebase patterns. Ready to proceed to Phase 1 design.

**Key Technologies**:
- MCP Python SDK (low-level API)
- Async SQLModel with existing models
- JWT validation via existing auth service
- Lifespan context for connection pooling
- Structured tool schemas with JSON Schema

**No Blockers**: All patterns are proven and documented.

## Phase 1: Design & Contracts

**Objective**: Define tool schemas, data flow, and developer documentation

*Phase 1 artifacts will be generated in the following sections*

---

This plan establishes the foundation for MCP server implementation. Next steps:
1. Generate `research.md` with consolidated findings ✅ (embedded above)
2. Generate `data-model.md` with tool schemas and data flow
3. Generate tool contract files in `contracts/` directory
4. Generate `quickstart.md` for developer onboarding
5. Run `/sp.tasks` to create implementation task breakdown
