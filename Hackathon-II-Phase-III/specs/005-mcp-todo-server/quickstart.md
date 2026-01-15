# Quickstart: MCP Server & Todo Tooling

**Feature**: 005-mcp-todo-server
**Date**: 2026-01-10

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database with `Task` table
- Valid JWT for testing (or mock token generator)

## Installation

```bash
cd backend
pip install mcp sqlmodel sqlalchemy[asyncio] asyncpg
```

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host/neon_db
JWT_SECRET=your_jwt_secret_key

# Optional
MCP_SERVER_NAME=todo-mcp-server
MCP_LOG_LEVEL=INFO
```

## Running the Server

**Stdio Transport** (default):
```bash
python -m mcp_server.server
```

**With Custom JWT Secret**:
```bash
JWT_SECRET=secret python -m mcp_server.server
```

## Testing with MCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Connect to running server
mcpInspector --command "python" --args "-m", "mcp_server.server"
```

## Example Tool Calls

### Add Task

```json
{
  "tool": "add_task",
  "arguments": {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_completed": false,
      "created_at": "2026-01-10T12:00:00Z"
    }
  }
}
```

### List Tasks

```json
{
  "tool": "list_tasks",
  "arguments": {
    "filter_completed": false
  }
}
```

### Complete Task

```json
{
  "tool": "complete_task",
  "arguments": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Running Tests

```bash
cd backend
pytest tests/mcp/ -v
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] All 5 tools registered and visible
- [ ] `add_task` creates task with correct ownership
- [ ] `list_tasks` returns only authenticated user's tasks
- [ ] `update_task` fails on other user's task
- [ ] `complete_task` updates status correctly
- [ ] `delete_task` removes task and returns success
- [ ] Invalid JWT returns AUTH_ERROR
