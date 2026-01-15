# Implementation Plan: AI Agent & Stateless Chat API

**Branch**: `006-ai-chat-api` | **Date**: 2026-01-10 | **Spec**: [spec.md](../006-ai-chat-api/spec.md)
**Input**: Feature specification from `/specs/006-ai-chat-api/spec.md`

## Summary

Implement a stateless chat API endpoint (`POST /api/{user_id}/chat`) that authenticates via JWT, reconstructs conversation context from the database per request, runs an OpenAI Agents SDK agent that can invoke Todo MCP tools, persists both user and assistant messages, and returns a friendly confirmation response.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, SQLModel, jose (JWT)
**Storage**: PostgreSQL (Neon)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web application (backend)
**Performance Goals**: Return initial assistant response within 2 seconds for typical requests (excluding external tool latency)
**Constraints**:
- Fully stateless API (no in-memory conversation state)
- JWT auth required; authenticated user must match route user_id
- All task operations MUST happen through MCP tools (no direct DB task writes in chat layer)
- Persist and reload conversation history from DB on every request
**Scale/Scope**: Single chat endpoint + agent wiring; excludes frontend UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Tool-driven AI (MCP) | ✅ PASS | Agent will call MCP tools for task operations |
| Fully Stateless Server Architecture | ✅ PASS | Chat endpoint reconstructs state from DB each request |
| Database-backed Conversation Memory | ✅ PASS | Conversation messages persisted to PostgreSQL |
| Security & Statelessness | ✅ PASS | JWT middleware + user_id path match enforced |
| Stack & Logic (AI-Centric) | ✅ PASS | OpenAI Agents SDK mandated |

**Gate Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/006-ai-chat-api/
├── plan.md              # This file
├── research.md          # Phase 0 output (Agents SDK patterns, MCP client integration)
├── data-model.md        # Phase 1 output (Conversation/Message entities)
├── quickstart.md        # Phase 1 output (how to run and test chat)
├── contracts/           # Phase 1 output (request/response schemas)
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/src/
├── api/
│   ├── main.py
│   └── routes/
│       ├── auth.py
│       ├── tasks.py
│       └── chat.py                # NEW: /api/v1/{user_id}/chat
├── chat/
│   ├── agent.py                   # NEW: Agents SDK agent + system prompt
│   ├── mcp_client.py              # NEW: MCP client wrapper used by agent tools
│   ├── schemas.py                 # NEW: request/response models
│   └── persistence.py             # NEW: DB read/write for conversation history
└── models/
    ├── conversation.py            # NEW
    └── message.py                 # NEW

backend/tests/
└── chat/
    └── test_chat_api.py           # OPTIONAL (if tests added later)
```

**Structure Decision**: Add a dedicated `backend/src/chat/` module for agent + persistence logic, and a new FastAPI route `backend/src/api/routes/chat.py` registered in `backend/src/api/main.py`.

## Phase 0: Research & Unknown Resolution

### Open Questions (NEEDS CLARIFICATION)

| ID | Question | Research Required |
|----|----------|-------------------|
| Q1 | How to represent conversation history to OpenAI Agents SDK in a stateless request? | Agents SDK context/session patterns |
| Q2 | Best practice for tool calling determinism? | Prompting + tool schema stability |
| Q3 | How to invoke an MCP server from within FastAPI (local process vs network)? | Deployment and runtime integration patterns |

### Research Tasks

- R1: Review OpenAI Agents SDK patterns for tools + passing context (`RunContextWrapper`, `ToolContext`).
- R2: Identify deterministic mapping techniques: constrained tool schemas, strict system prompt, structured tool outputs.
- R3: Evaluate MCP client integration options (spawn stdio server process, connect to remote MCP server).

## Phase 1: Design & Contracts

*Prerequisites: research.md complete*

### Data Model Design (Conversation Memory)

- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, role, content, tool_calls_json (optional), created_at

### API Contract (Chat Endpoint)

- Route: `POST /api/v1/{user_id}/chat`
- Auth: Bearer JWT (existing middleware)
- Behavior:
  1) Validate `user_id` path matches authenticated user
  2) Load latest conversation (or create if none)
  3) Append user message
  4) Run agent with context reconstructed from DB
  5) Persist assistant response + tool calls
  6) Return assistant response payload

### Error Taxonomy

- 401 AUTH_001: missing/invalid JWT (middleware)
- 403 AUTH_002: user_id mismatch (dependency)
- 422 VALIDATION_ERROR: invalid request payload
- 500 SERVER_ERROR: unexpected errors

## Phase 2: Next Steps

- Run `/sp.tasks` to generate executable implementation tasks
- Implement chat persistence models and migrations
- Implement agent + MCP tool wiring
- Add new chat route and register router
- Add quickstart validation steps
