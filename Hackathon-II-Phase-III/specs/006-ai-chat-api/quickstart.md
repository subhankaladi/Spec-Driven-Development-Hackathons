# Quickstart: AI Agent & Stateless Chat API

**Feature**: 006-ai-chat-api
**Date**: 2026-01-10

## Prerequisites

- Backend API running (FastAPI)
- PostgreSQL reachable (Neon)
- JWT available for a test user
- OpenAI API credentials configured
- MCP Todo server (feature 005) available

## Environment Variables

```bash
OPENAI_API_KEY=...
DATABASE_URL=...
JWT_SECRET=...

# MCP connection (exact form decided in plan/tasks)
MCP_TODO_SERVER_URL=...
```

## Run Backend

```bash
cd backend
python -m src.api.main
```

## Call Chat Endpoint

```bash
curl -X POST \
  "http://localhost:8000/api/v1/<user_id>/chat" \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}'
```

Expected response:
```json
{
  "conversation_id": "...",
  "assistant_message": "I've added 'buy milk' to your task list."
}
```

## Statelessness Validation

1) Send a message: "Add task: Buy milk".
2) Restart backend server.
3) Send: "List my tasks".
4) Confirm response still includes the new task (history + DB-backed continuity).

## Security Validation

- Call without JWT → expect 401
- Call with JWT for user A but route user_id = user B → expect 403
