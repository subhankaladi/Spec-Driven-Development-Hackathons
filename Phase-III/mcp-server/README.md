# MCP Server & Todo Tooling

**Phase III: AI-Powered Todo Chatbot - Foundation**

This MCP (Model Context Protocol) server exposes 5 stateless, JWT-authenticated tools that enable AI agents to manage user tasks through natural language.

## Overview

The MCP server implements the official MCP Python SDK to provide task management tools for AI agents. All operations are:
- **Stateless**: No in-memory conversation state
- **Database-backed**: All data persists in Neon Serverless PostgreSQL
- **User-isolated**: JWT authentication enforces user identity per tool invocation
- **Async-first**: Non-blocking database operations with connection pooling

## Tools Provided

| Tool | Priority | Description |
|------|----------|-------------|
| `add_task` | P1 | Create new task with title and optional description |
| `list_tasks` | P1 | Retrieve user tasks with filtering and pagination |
| `complete_task` | P2 | Mark task as completed (idempotent) |
| `update_task` | P2 | Modify task title, description, or status |
| `delete_task` | P3 | Permanently remove task from database |

## Quick Start

### Prerequisites

- Python 3.11+
- Neon PostgreSQL database (shared with backend)
- Backend application running (for shared models)

### Installation

```bash
# Navigate to MCP server directory
cd mcp-server

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET
```

### Running the Server

```bash
# Start MCP server (stdio transport)
python src/server.py
```

The server will:
1. Initialize database connection pool
2. Register all 5 tools with MCP protocol
3. Listen on stdin for tool invocation requests
4. Return responses on stdout

### Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Architecture

```
mcp-server/
├── src/
│   ├── server.py           # MCP server entry point
│   ├── tools/              # Tool handler implementations
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── update_task.py
│   │   ├── complete_task.py
│   │   └── delete_task.py
│   ├── schemas/            # JSON Schema definitions
│   ├── auth/               # JWT validation
│   ├── db/                 # Database session management
│   └── utils/              # Error handling
├── tests/
│   ├── unit/               # Unit tests per tool
│   ├── integration/        # End-to-end tests
│   └── conftest.py         # Pytest fixtures
├── requirements.txt
├── .env.example
└── README.md
```

## Key Patterns

### JWT Authentication
Every tool invocation requires a valid JWT token:
```python
{
  "jwt_token": "eyJhbGciOiJIUzI1NiIs...",
  "title": "Buy groceries"
}
```

### User Isolation
All database queries are scoped to the authenticated user:
```python
# Extract user_id from JWT
user_id = validate_jwt_token(jwt_token)

# Query only user's tasks
tasks = await session.exec(
    select(Task).where(Task.user_id == user_id)
)
```

### Stateless Operations
Each tool invocation:
1. Validates JWT token
2. Creates new database session
3. Executes database operation
4. Closes session
5. Returns structured response

No in-memory state maintained between invocations.

## Documentation

- **Specification**: `../specs/005-mcp-server-todo-tooling/spec.md`
- **Implementation Plan**: `../specs/005-mcp-server-todo-tooling/plan.md`
- **Task Breakdown**: `../specs/005-mcp-server-todo-tooling/tasks.md`
- **Developer Guide**: `../specs/005-mcp-server-todo-tooling/quickstart.md`
- **Tool Contracts**: `../specs/005-mcp-server-todo-tooling/contracts/*.json`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string (asyncpg) | `postgresql+asyncpg://user:pass@host/db` |
| `JWT_SECRET` | JWT signing secret (MUST match backend) | `your-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Token expiration | `15` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `development` |

## Error Handling

All tools return structured errors:

| Error Code | HTTP Equivalent | Description |
|------------|-----------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid/expired JWT token |
| `AUTHORIZATION_ERROR` | 403 | User not authorized for resource |
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `NOT_FOUND_ERROR` | 404 | Resource not found |
| `DATABASE_ERROR` | 500 | Database operation failed |

## Performance Requirements

- **Query Latency**: <500ms for list_tasks with 100 items
- **Auth Rejection**: <50ms for invalid JWT
- **Server Startup**: <3 seconds

## Contributing

See `../specs/005-mcp-server-todo-tooling/tasks.md` for implementation tasks organized by user story.

### Development Workflow

1. Read feature spec and user stories
2. Review tool contracts for input/output schemas
3. Implement tool handler following existing patterns
4. Write unit tests for tool handler
5. Register tool in MCP server
6. Write integration tests
7. Validate with MCP test client

## License

See project root for license information.

## Support

For issues or questions:
1. Review specification documents in `../specs/005-mcp-server-todo-tooling/`
2. Check quickstart guide for common patterns
3. Review existing tool implementations for examples
4. Run tests to identify specific failures

---

**Built with**: Official MCP Python SDK • SQLModel • Neon Serverless PostgreSQL • FastAPI Backend Integration
