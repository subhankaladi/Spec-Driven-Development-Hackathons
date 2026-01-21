# Chat API Documentation

## Overview

The Chat API provides a natural language interface for task management through an AI agent. Users can create, list, update, complete, and delete tasks using conversational language instead of structured API calls. The agent automatically invokes the appropriate MCP (Model Context Protocol) tools based on user intent and maintains conversation context across multiple messages.

**Key Features:**
- Natural language task management
- Multi-turn conversations with context retention
- Automatic tool invocation and chaining
- User-friendly error messages
- Rate limiting for abuse prevention
- Full conversation history persistence

## Getting Started

### Prerequisites

1. **Environment Variables** (create a `.env` file in the backend directory):
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini

# MCP Server Configuration
MCP_BASE_URL=http://localhost:8001  # Optional, defaults to localhost:8001

# Rate Limiting
CHAT_RATE_LIMIT=10  # Requests per minute per user (0 to disable)

# Database Configuration
DATABASE_URL=your_neon_postgres_url_here

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

2. **Dependencies**: Install required Python packages:
```bash
pip install -r requirements.txt
```

3. **Database**: Ensure PostgreSQL database is running and migrations are applied:
```bash
alembic upgrade head
```

4. **MCP Server**: The backend MCP server must be running on the configured port (default: 8001).

### Starting the Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with auto-generated documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. POST /api/chat

Send a message to the AI agent for task management.

**Request Body:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "optional-uuid-for-existing-conversation"
}
```

**Response (200 OK):**
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_message": {
    "id": "234e5678-e89b-12d3-a456-426614174001",
    "role": "user",
    "content": "Add a task to buy groceries",
    "tool_calls": null,
    "created_at": "2024-01-17T12:00:00Z"
  },
  "agent_response": {
    "id": "345e6789-e89b-12d3-a456-426614174002",
    "role": "assistant",
    "content": "I've added 'Buy groceries' to your task list!",
    "tool_calls": [
      {
        "tool": "add_task",
        "parameters": {"title": "Buy groceries"},
        "result": {"success": true, "task_id": "456e7890-e89b-12d3-a456-426614174003"}
      }
    ],
    "created_at": "2024-01-17T12:00:01Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Empty or too long message (max 5000 characters)
- `401 Unauthorized`: Missing or invalid authentication token
- `429 Too Many Requests`: Rate limit exceeded (10 requests/minute)
- `500 Internal Server Error`: Server processing error

### 2. GET /api/chat/conversations

List all conversations for the authenticated user with pagination.

**Query Parameters:**
- `limit` (optional): Maximum conversations to return (1-100, default: 50)
- `offset` (optional): Number of conversations to skip (default: 0)

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Add a task to buy groceries...",
      "created_at": "2024-01-17T12:00:00Z",
      "updated_at": "2024-01-17T12:05:00Z",
      "message_count": 4
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### 3. GET /api/chat/{conversation_id}

Retrieve full conversation history with all messages.

**Path Parameters:**
- `conversation_id` (required): UUID of the conversation

**Query Parameters:**
- `limit` (optional): Maximum messages to return (1-500, default: 100)
- `offset` (optional): Number of messages to skip (default: 0)

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Add a task to buy groceries...",
  "created_at": "2024-01-17T12:00:00Z",
  "updated_at": "2024-01-17T12:05:00Z",
  "messages": [
    {
      "id": "234e5678-e89b-12d3-a456-426614174001",
      "role": "user",
      "content": "Add a task to buy groceries",
      "tool_calls": null,
      "created_at": "2024-01-17T12:00:00Z"
    },
    {
      "id": "345e6789-e89b-12d3-a456-426614174002",
      "role": "assistant",
      "content": "I've added 'Buy groceries' to your task list!",
      "tool_calls": [
        {
          "tool": "add_task",
          "parameters": {"title": "Buy groceries"},
          "result": {"success": true}
        }
      ],
      "created_at": "2024-01-17T12:00:01Z"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: User doesn't own the conversation
- `404 Not Found`: Conversation doesn't exist

## Authentication

The Chat API uses JWT tokens for authentication via Better Auth. Tokens must be provided in one of two ways:

### 1. Cookie (Preferred)
Better Auth automatically sets the `better-auth-session` cookie upon login. The API reads this cookie for authentication.

### 2. Authorization Header
Alternatively, include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

**How to get authenticated:**
1. Sign up: `POST /api/auth/sign-up`
2. Sign in: `POST /api/auth/sign-in`
3. Better Auth sets the session cookie automatically
4. Use the cookie for all subsequent chat API requests

**Token expiration**: JWT tokens expire after 24 hours. You'll receive a `401 Unauthorized` error if your token expires. Sign in again to get a new token.

## Usage Examples

### Example 1: Adding a Task

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"message": "Add a task to buy groceries"}'
```

**Response:**
```json
{
  "conversation_id": "...",
  "user_message": {...},
  "agent_response": {
    "content": "I've added 'Buy groceries' to your task list!",
    "tool_calls": [
      {
        "tool": "add_task",
        "parameters": {"title": "Buy groceries"},
        "result": {"success": true, "task_id": "..."}
      }
    ]
  }
}
```

### Example 2: Listing Tasks

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"message": "Show me my important tasks"}'
```

**Response:**
```json
{
  "conversation_id": "...",
  "agent_response": {
    "content": "Here are your tasks: ...",
    "tool_calls": [
      {
        "tool": "list_tasks",
        "parameters": {},
        "result": {
          "tasks": [
            {"id": "...", "title": "Buy groceries", "is_completed": false}
          ]
        }
      }
    ]
  }
}
```

### Example 3: Tool Chaining (List and Delete)

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"message": "List my tasks and delete all completed ones"}'
```

**Response:**
The agent will:
1. Call `list_tasks` to get all tasks
2. Filter for completed tasks
3. Call `delete_task` for each completed task
4. Return a summary: "I've deleted 3 completed tasks. You have 7 tasks remaining."

### Example 4: Error Handling

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"message": "Delete task abc123"}'
```

**Response (if task not found):**
```json
{
  "agent_response": {
    "content": "I couldn't find the task you're looking for.",
    "tool_calls": [
      {
        "tool": "delete_task",
        "parameters": {"task_id": "abc123"},
        "result": {
          "error": "I couldn't find the task you're looking for.",
          "success": false
        }
      }
    ]
  }
}
```

## Response Format

All successful chat responses follow this schema:

```typescript
{
  conversation_id: string (UUID),
  user_message: {
    id: string (UUID),
    role: "user",
    content: string,
    tool_calls: null,
    created_at: string (ISO 8601)
  },
  agent_response: {
    id: string (UUID),
    role: "assistant",
    content: string,
    tool_calls: Array<{
      tool: string,
      parameters: object,
      result: object
    }> | null,
    created_at: string (ISO 8601)
  }
}
```

**Key Fields:**
- `conversation_id`: Use this ID for subsequent messages in the same conversation
- `tool_calls`: Array of all MCP tools invoked by the agent
- `result`: Contains the output from each tool (may include `success` and `error` fields)

## Error Handling

The Chat API provides user-friendly error messages that can be displayed directly in the UI. Technical error codes are translated to natural language.

**Common Error Scenarios:**

| Scenario | Error Message | Status Code |
|----------|---------------|-------------|
| Authentication expired | "Your authentication token expired. Please log in again." | 401 |
| Task not found | "I don't see that task in your list." | 200* |
| Invalid request | "That doesn't seem right. Can you try again?" | 200* |
| Database connection | "I'm having trouble reaching the database. Please try again in a moment." | 200* |
| Empty message | "I didn't catch that. What would you like to do with your tasks?" | 400 |
| Rate limit exceeded | "Too many requests. Please try again in a moment." | 429 |

*Note: MCP tool errors return 200 OK but include the error in the `tool_calls[].result.error` field for graceful error handling in the UI.

## Tool Chaining

The AI agent can chain multiple tools together to handle complex requests. Tool chaining enables the agent to:
1. List tasks to find a specific task ID
2. Perform operations on multiple tasks sequentially
3. Continue processing even if one tool fails
4. Aggregate results from multiple operations

**Example Workflow: "List and delete completed tasks"**

1. Agent calls `list_tasks` to retrieve all tasks
2. Agent filters tasks where `is_completed = true`
3. Agent calls `delete_task` for each completed task ID
4. Agent returns summary: "Deleted 3 tasks. 7 tasks remaining."

**Error Handling in Tool Chains:**
- If one tool fails, the agent continues with remaining operations
- Failed operations are reported in the final response
- Agent provides contextual explanation of partial success

## Rate Limiting

To prevent abuse and ensure fair resource allocation, the Chat API enforces rate limits:

**Default Limits:**
- 10 requests per minute per authenticated user
- Applies only to `POST /api/chat` endpoint
- Read-only endpoints (GET) are not rate-limited

**Configuration:**
Set the `CHAT_RATE_LIMIT` environment variable to adjust limits:
```env
CHAT_RATE_LIMIT=10  # Requests per minute (0 to disable)
```

**Rate Limit Exceeded Response (429):**
```json
{
  "detail": "Too many requests. Please try again in a moment."
}
```

**Best Practices:**
- Implement exponential backoff in client applications
- Display rate limit errors gracefully in the UI
- Cache conversation history to minimize API calls

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Missing or expired JWT token

**Solution:**
1. Verify the token is included in cookies or Authorization header
2. Check token expiration (24-hour validity)
3. Sign in again to get a fresh token

### Issue: 500 Internal Server Error

**Cause**: Database connection failure or OpenAI API error

**Solution:**
1. Check `DATABASE_URL` is correctly configured
2. Verify OpenAI API key is valid and has credits
3. Check MCP server is running on configured port
4. Review server logs for detailed error messages

### Issue: Agent gives unexpected responses

**Cause**: Ambiguous or unclear user input

**Solution:**
1. Use clear, specific language ("Add task X" instead of "Do this")
2. Reference task IDs explicitly when available
3. Break complex requests into smaller steps

### Issue: Slow response times (> 3 seconds)

**Cause**: OpenAI API latency or complex tool chains

**Solution:**
1. Optimize MCP tool performance
2. Consider using a faster OpenAI model (gpt-4o-mini is fastest)
3. Implement client-side loading indicators for better UX

### Issue: Tool calls fail silently

**Cause**: MCP server not running or authentication issues

**Solution:**
1. Verify MCP server is accessible at `MCP_BASE_URL`
2. Check JWT token is being forwarded to MCP server
3. Review MCP server logs for authentication errors

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │────────▶│  Chat API    │────────▶│   OpenAI    │
│   (Web UI)  │         │  (FastAPI)   │         │   Agent     │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                         │
                               │                         ▼
                        ┌──────▼──────┐         ┌─────────────┐
                        │  Database   │         │ MCP Server  │
                        │ (Postgres)  │         │  (FastAPI)  │
                        └─────────────┘         └─────────────┘
```

**Flow:**
1. Client sends natural language message to Chat API
2. Chat API creates/retrieves conversation from database
3. Chat API forwards message to OpenAI agent with conversation context
4. OpenAI agent determines which MCP tools to invoke
5. Chat API executes MCP tools via HTTP requests to MCP server
6. MCP server performs task operations and returns results
7. OpenAI agent synthesizes results into natural language response
8. Chat API persists both user message and agent response
9. Client receives complete conversation exchange

## Performance Considerations

**Target Latencies:**
- Chat message processing: < 3 seconds (p95)
- Conversation retrieval: < 200ms
- Conversation list: < 200ms

**Optimization Tips:**
1. Use connection pooling for database connections
2. Cache conversation context to minimize database queries
3. Implement proper indexes on conversation and message tables
4. Use async operations throughout the stack
5. Consider implementing Redis for rate limiting in production

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Authorization**: Users can only access their own conversations
3. **Input Validation**: Messages limited to 5000 characters
4. **Rate Limiting**: Prevents abuse and DoS attacks
5. **SQL Injection**: Prevented via SQLModel ORM and parameterized queries
6. **Secrets Management**: Never expose API keys or tokens in responses

## Next Steps

- Integrate the Chat API into your frontend application
- Implement conversation selection UI for resuming previous chats
- Add typing indicators during agent processing
- Display tool calls in a developer/debug mode for transparency
- Implement conversation search and filtering
- Add support for file attachments or rich media

## Support

For issues, questions, or feature requests:
- Review server logs at `LOG_LEVEL=DEBUG`
- Check OpenAPI documentation at `/docs`
- Verify all environment variables are set correctly
- Ensure MCP server and database are accessible
