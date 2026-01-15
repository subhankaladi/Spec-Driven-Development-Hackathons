# Research: MCP Server & Todo Tooling

**Feature**: 005-mcp-todo-server
**Date**: 2026-01-10

## Q1: JWT Transport in MCP

**Decision**: JWT passed via MCP initialization context (stdio/websocket transport), extracted per tool call.

**Rationale**: MCP protocol supports authentication during session initialization. The JWT should be provided by the MCP client (AI agent runtime) when connecting. For the Python Official MCP SDK:

- Use `mcp.server.stdio` for stdio transport (JWT via environment or init params)
- JWT validation happens in a middleware/handler before tool execution
- Each tool receives `context` containing session authentication data

**Implementation Pattern**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("todo-mcp-server")

@server.list_tools()
async def list_tools():
    return [Tool(name="add_task", ...)]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Extract user_id from validated JWT in context
    user_id = context.session.authenticated_user_id
    # Proceed with tool logic...
```

**Alternatives Considered**:
- Header-based auth (HTTP transports only, not stdio)
- Per-call JWT parameter (pollutes tool schemas, less secure)

---

## Q2: MCP Tool Response Schema

**Decision**: Tools return structured JSON objects via `TextContent` responses.

**Rationale**: MCP SDK uses `TextContent` for tool results. For structured data:
- Return JSON as a text string in `TextContent.text`
- Use a standardized success/error envelope
- Client can parse and display appropriately

**Response Format**:
```python
{
    "success": true,
    "data": {
        "task": {
            "id": "uuid",
            "title": "Buy milk",
            "is_completed": false
        }
    }
}
```

**Error Format**:
```python
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "Task not found or access denied"
    }
}
```

---

## Q3: SQLModel + Neon Async Patterns

**Decision**: Use SQLModel with `AsyncSession` and `create_async_engine` for Neon.

**Rationale**: Neon Serverless PostgreSQL requires async drivers for efficient connection pooling. SQLModel supports async via `sqlmodel.ext.asyncio`.

**Connection Setup**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import create_engine, Session, select

# Async engine for Neon
DATABASE_URL = "postgresql+asyncpg://user:pass@host/neon_db"
async_engine = create_async_engine(DATABASE_URL, echo=False)

async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

**Tool Implementation Pattern**:
```python
async def add_task(title: str, description: str | None, user_id: uuid.UUID):
    async with AsyncSession(async_engine) as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
```

---

## Best Practices Summary

1. **JWT Validation**: Validate once per session, cache user_id in session context
2. **Ownership Enforcement**: Always filter queries by `user_id`; never rely on task existence alone
3. **Error Handling**: Return consistent error codes; never leak internal errors to client
4. **Async Operations**: Use context managers for session lifecycle; avoid long-held connections
5. **Testing**: Use `pytest-asyncio` for async test fixtures; mock database for unit tests
