# MCP Server & Todo Tooling - Quick Start Guide

**Feature**: MCP Server & Todo Tooling
**Branch**: `005-mcp-server-todo-tooling`
**Created**: 2026-01-16

## Overview

This guide provides everything you need to develop, test, and run the MCP (Model Context Protocol) server for todo task operations. The server exposes 5 stateless, JWT-authenticated tools that AI agents can invoke to manage user tasks.

## Prerequisites

- Python 3.11+ installed
- Existing backend running (for shared database and auth utilities)
- Neon PostgreSQL database accessible
- Git repository cloned and on correct branch

## Installation

### 1. Navigate to MCP Server Directory

```bash
cd mcp-server
```

### 2. Create Python Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `mcp` - Official Model Context Protocol Python SDK
- `sqlmodel` - Async ORM for database operations
- `pyjwt` - JWT token validation
- `python-dotenv` - Environment configuration
- `pytest` + `pytest-asyncio` - Testing framework

### 4. Configure Environment Variables

Create `.env` file in `mcp-server/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Connection (shared with backend)
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/database

# JWT Configuration (must match backend)
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

**Important**: JWT secret MUST match the backend's secret for token validation to work.

## Project Structure

```
mcp-server/
├── src/
│   ├── server.py              # MCP server entry point
│   ├── tools/                 # Tool handler implementations
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── update_task.py
│   │   ├── complete_task.py
│   │   └── delete_task.py
│   ├── schemas/               # JSON Schema definitions
│   │   └── tool_schemas.py
│   ├── auth/                  # JWT validation
│   │   └── jwt_validator.py
│   ├── db/                    # Database session management
│   │   └── session.py
│   └── utils/                 # Error handling
│       └── errors.py
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests per tool
│   ├── integration/           # End-to-end tests
│   └── conftest.py            # Pytest fixtures
├── .env                       # Environment config (not committed)
├── .env.example               # Example config (committed)
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## Running the MCP Server

### Local Development (stdio transport)

The MCP server uses stdio (standard input/output) transport for communication with AI agents:

```bash
cd mcp-server
source venv/bin/activate
python src/server.py
```

**Expected Output**:
```
INFO: MCP Server started: todo-mcp-server
INFO: Registered 5 tools: add_task, list_tasks, update_task, complete_task, delete_task
INFO: Server ready on stdio transport
```

The server will:
1. Initialize database connection pool (lifespan context)
2. Register all 5 tools with MCP protocol
3. Listen on stdin for tool invocation requests
4. Process requests asynchronously
5. Return responses on stdout

### Testing with MCP Client

You can test the server using an MCP client (AI agent simulator):

```python
# test_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["src/server.py"],
    env={}
)

async def test_add_task():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # Call add_task tool
            result = await session.call_tool(
                "add_task",
                arguments={
                    "jwt_token": "your-jwt-token-here",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread"
                }
            )

            print(f"Result: {result.content}")

if __name__ == "__main__":
    asyncio.run(test_add_task())
```

Run the test client:
```bash
python test_client.py
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run Specific Test File

```bash
pytest tests/unit/test_add_task.py -v
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Test Fixtures

The test suite uses fixtures defined in `tests/conftest.py`:

- `test_db_session`: Test database session (isolated from production)
- `test_jwt_token`: Valid JWT token for testing
- `expired_jwt_token`: Expired JWT token for auth testing
- `invalid_jwt_token`: Malformed JWT token for error testing
- `test_user`: Test user with known UUID
- `test_tasks`: Pre-populated test tasks

**Example Test**:
```python
# tests/unit/test_add_task.py
import pytest
from src.tools.add_task import add_task_handler

@pytest.mark.asyncio
async def test_add_task_success(test_db_session, test_jwt_token):
    """Test successful task creation."""
    result = await add_task_handler(
        arguments={
            "jwt_token": test_jwt_token,
            "title": "Test task",
            "description": "Test description"
        },
        session=test_db_session
    )

    assert result["title"] == "Test task"
    assert result["description"] == "Test description"
    assert result["is_completed"] is False
    assert "id" in result
```

## Development Workflow

### 1. Understand the Spec

Read the feature specification:
```bash
cat specs/005-mcp-server-todo-tooling/spec.md
```

Key sections:
- User stories with acceptance scenarios
- Functional requirements (FR-001 through FR-037)
- Success criteria

### 2. Review the Plan

Read the implementation plan:
```bash
cat specs/005-mcp-server-todo-tooling/plan.md
```

Key sections:
- Technical context
- Constitution check
- Phase 0 research findings
- Project structure

### 3. Check Tool Schemas

Review tool contracts:
```bash
cat specs/005-mcp-server-todo-tooling/contracts/add_task.json
```

Each tool has:
- `inputSchema`: JSON Schema for parameters
- `outputSchema`: JSON Schema for return value
- `errors`: Possible error codes and messages

### 4. Implement Tool Handler

Follow this pattern for each tool:

```python
# src/tools/add_task.py
from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.models.task import Task
from src.auth.jwt_validator import validate_jwt_token
from src.utils.errors import ValidationError, AuthenticationError

async def add_task_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Handle add_task tool invocation.

    Args:
        arguments: Tool input parameters (jwt_token, title, description)
        session: Async database session

    Returns:
        Task object as dictionary

    Raises:
        AuthenticationError: Invalid/expired JWT token
        ValidationError: Invalid input parameters
    """
    # 1. Validate JWT and extract user_id
    user_id = await validate_jwt_token(arguments.get("jwt_token"))

    # 2. Validate input parameters
    title = arguments.get("title", "").strip()
    if not title or len(title) > 255:
        raise ValidationError("Title must be 1-255 characters")

    description = arguments.get("description")

    # 3. Create task
    new_task = Task(
        user_id=user_id,
        title=title,
        description=description,
        is_completed=False
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # 4. Return structured response
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

### 5. Write Tests

Write unit tests for the tool handler:

```python
# tests/unit/test_add_task.py
import pytest
from src.tools.add_task import add_task_handler
from src.utils.errors import ValidationError, AuthenticationError

@pytest.mark.asyncio
async def test_add_task_success(test_db_session, test_jwt_token):
    """Test successful task creation."""
    result = await add_task_handler(
        arguments={
            "jwt_token": test_jwt_token,
            "title": "Test task",
            "description": "Test description"
        },
        session=test_db_session
    )

    assert result["title"] == "Test task"
    assert "id" in result

@pytest.mark.asyncio
async def test_add_task_missing_jwt(test_db_session):
    """Test authentication error when JWT missing."""
    with pytest.raises(AuthenticationError):
        await add_task_handler(
            arguments={"title": "Test task"},
            session=test_db_session
        )

@pytest.mark.asyncio
async def test_add_task_empty_title(test_db_session, test_jwt_token):
    """Test validation error for empty title."""
    with pytest.raises(ValidationError):
        await add_task_handler(
            arguments={"jwt_token": test_jwt_token, "title": ""},
            session=test_db_session
        )
```

### 6. Register Tool in Server

Add tool to MCP server registration:

```python
# src/server.py
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="add_task",
            description="Create a new task for the authenticated user",
            inputSchema=ADD_TASK_INPUT_SCHEMA,
            outputSchema=ADD_TASK_OUTPUT_SCHEMA
        ),
        # ... other tools
    ]

@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> dict:
    ctx = server.request_context
    engine = ctx.lifespan_context["db_engine"]

    async with AsyncSession(engine) as session:
        if name == "add_task":
            return await add_task_handler(arguments, session)
        # ... other tools

        raise ValueError(f"Unknown tool: {name}")
```

### 7. Run and Test

```bash
# Run tests
pytest tests/unit/test_add_task.py -v

# Run server
python src/server.py

# Test with client
python test_client.py
```

## Common Issues and Solutions

### Issue: Database Connection Error

**Symptom**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
1. Check DATABASE_URL in `.env` is correct
2. Verify Neon PostgreSQL is accessible
3. Ensure database exists
4. Test connection with `psql` or `pgcli`:
   ```bash
   psql $DATABASE_URL
   ```

### Issue: JWT Validation Fails

**Symptom**: `AuthenticationError: Invalid authentication token`

**Solution**:
1. Verify JWT_SECRET in `.env` matches backend
2. Check token hasn't expired (15-minute default)
3. Ensure token format is correct (Bearer token)
4. Test JWT decode:
   ```python
   import jwt
   token = "your-token-here"
   secret = "your-secret-here"
   payload = jwt.decode(token, secret, algorithms=["HS256"])
   print(payload)
   ```

### Issue: Import Errors from Backend

**Symptom**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
1. Ensure you're running from project root (not mcp-server/)
2. Add backend to PYTHONPATH:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```
3. Or use absolute imports in code:
   ```python
   import sys
   sys.path.append("../backend")
   from src.models.task import Task
   ```

### Issue: Async Session Errors

**Symptom**: `RuntimeError: Task attached to a different loop`

**Solution**:
1. Ensure all database operations use `await`
2. Create new session per tool invocation (don't reuse)
3. Use async context manager:
   ```python
   async with AsyncSession(engine) as session:
       # operations here
   ```

## API Reference

### MCP Server Entry Point

**File**: `src/server.py`

**Function**: `run()`

**Description**: Initialize and run MCP server with stdio transport

**Lifecycle**:
1. Load environment configuration
2. Initialize lifespan context (database pool)
3. Register tools with MCP protocol
4. Start stdio server loop
5. Process tool invocations
6. Cleanup on shutdown (dispose database engine)

### Tool Handler Pattern

All tool handlers follow this signature:

```python
async def <tool>_handler(
    arguments: Dict[str, Any],
    session: AsyncSession
) -> Dict[str, Any] | List[TextContent]:
    """
    Handle <tool> tool invocation.

    Args:
        arguments: Tool input parameters from AI agent
        session: Async SQLModel database session

    Returns:
        Structured response dict or error TextContent list

    Raises:
        AuthenticationError: JWT validation failed
        ValidationError: Input validation failed
        NotFoundError: Resource not found
        AuthorizationError: User not authorized
        DatabaseError: Database operation failed
    """
    pass
```

### Error Classes

**File**: `src/utils/errors.py`

```python
class AuthenticationError(Exception):
    """Raised when JWT token is missing, invalid, or expired."""
    pass

class ValidationError(Exception):
    """Raised when input parameters fail validation."""
    pass

class NotFoundError(Exception):
    """Raised when requested resource doesn't exist."""
    pass

class AuthorizationError(Exception):
    """Raised when user not authorized to access resource."""
    pass

class DatabaseError(Exception):
    """Raised when database operation fails."""
    pass
```

## Next Steps

1. **Read the Spec**: Familiarize yourself with user stories and requirements
2. **Review Contracts**: Understand tool input/output schemas
3. **Run Tests**: Ensure existing tests pass
4. **Implement Tools**: Follow TDD approach (test first, then implement)
5. **Test Integration**: Verify tools work with MCP client
6. **Document Changes**: Update README with any new patterns

## Resources

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [SQLModel Async Documentation](https://sqlmodel.tiangolo.com/)
- [JWT Documentation](https://pyjwt.readthedocs.io/)
- [Pytest Async Testing](https://pytest-asyncio.readthedocs.io/)

## Support

For issues or questions:
1. Check this quickstart guide
2. Review spec.md and plan.md in `specs/005-mcp-server-todo-tooling/`
3. Run tests to identify specific failures
4. Check backend logs for database/auth issues
5. Review MCP SDK examples and documentation

Happy coding! 🚀
