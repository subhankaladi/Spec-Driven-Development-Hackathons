# Implementation Plan: AI Agent & Stateless Chat API

**Feature Branch**: `006-ai-agent-chat-api`
**Created**: 2026-01-16
**Status**: Ready for Implementation
**Input**: Specification from specs/006-ai-agent-chat-api/spec.md

---

## Phase 0: Research Findings

### OpenAI Agents SDK Configuration

**Decision**: Use OpenAI Agents SDK v0.2.9+ with native tool integration
**Rationale**:
- Official SDK with full feature support for tool registration and invocation
- Native async/await support for Python 3.11+
- Built-in error handling and structured logging
- Seamless integration with MCP tools via standard tool schema

**Key Findings**:
1. Agent configuration via `Agent` class with system prompt
2. Tools registered as structured definitions with input/output schemas
3. Tool invocation handled automatically via agent loop
4. Error handling via standard exception types with clear messages

**Alternatives Considered**:
- LangChain: More abstraction, heavier dependencies
- Anthropic API with tool_use: Different SDK, requires adapter
- Custom agent loop: High maintenance, error-prone

---

### MCP Tool Integration with OpenAI Agents

**Decision**: Register existing MCP tools as OpenAI Agent tools
**Rationale**:
- MCP tools already defined with JSON schemas in spec-4
- OpenAI Agents SDK accepts standard tool definitions
- No code duplication; tools are stateless and testable independently

**Pattern**:
```python
# Convert MCP tool definitions to Agent tools
# MCP tool → OpenAI Agent tool registration
# Agent handles orchestration, tools handle execution
```

---

### Conversation Persistence & State Reconstruction

**Decision**: Database-backed conversations with per-request history reconstruction
**Rationale**:
- Fully stateless: no in-memory session storage
- True resilience: server restart doesn't lose conversations
- Scalable: multiple servers can handle same user
- Constitutional requirement (Principle IX)

**Architecture**:
1. User sends message → API receives with JWT
2. Fetch full conversation history from DB for this user
3. Include history in agent system context
4. Agent reasons with full context
5. Agent invokes MCP tools as needed
6. Persist user message + agent response to DB
7. Return response to user

---

### Agent System Prompt & Behavior Rules

**Decision**: Structured system prompt with clear operational boundaries
**Rationale**:
- Constrains agent behavior to intended operations
- Prevents hallucinations or tool misuse
- Ensures consistent user experience

**System Prompt Structure**:
- Role: Task management AI assistant
- Capabilities: List 5 MCP tools available
- Constraints: Tools only, no direct data access
- Error handling: User-friendly messages
- Tone: Friendly, conversational, helpful

---

### JWT Token Validation in Tools

**Decision**: Validate JWT at chat API endpoint; pass user_id to all tool calls
**Rationale**:
- Single validation point (API layer) for efficiency
- User_id already extracted and trusted
- Tools receive pre-validated user_id
- Defense in depth: tools double-check anyway

---

## Technical Context

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | 0.128.0+ |
| AI Agent | OpenAI Agents SDK | 0.2.9+ |
| Database | PostgreSQL (Neon) | Latest |
| ORM | SQLModel | 0.0.14+ |
| Auth | JWT (Better Auth compatible) | 2.8.0+ |
| MCP Tools | OpenAI MCP SDK | 1.25.0+ |
| Runtime | Python | 3.11+ |

### Dependencies

**Upstream** (Must be complete):
- ✅ 005-mcp-server-todo-tooling (MCP tools: add_task, list_tasks, complete_task, update_task, delete_task)
- ✅ 002-auth-jwt (JWT token generation & validation)
- ✅ 001-task-api-backend (Task model, database schema)

**Downstream** (Enables):
- Phase III AI Chatbot Frontend (Next.js UI)
- Advanced agent features (summarization, recommendations)

### Project Structure

```
backend/src/
├── api/
│   ├── routes/
│   │   ├── chat.py                 # NEW: Stateless chat endpoint
│   │   ├── tasks.py                # Existing task CRUD
│   │   └── auth.py                 # Existing auth
│   ├── schemas/
│   │   ├── chat.py                 # NEW: Chat request/response
│   │   └── task.py                 # Existing task schemas
│   └── dependencies/
│       ├── auth.py                 # Existing JWT validation
│       └── chat.py                 # NEW: Chat-specific deps
├── services/
│   ├── agent_service.py            # NEW: OpenAI Agents SDK wrapper
│   ├── conversation_service.py     # NEW: Conversation persistence
│   ├── tool_adapter.py             # NEW: MCP → Agent tool bridge
│   └── auth_service.py             # Existing JWT handling
├── models/
│   ├── conversation.py             # NEW: Conversation, Message entities
│   ├── task.py                     # Existing Task entity
│   └── user.py                     # Existing User entity
└── main.py                         # Updated with chat route
```

### Constitution Check

**Principle I - Spec-Driven Development**: ✅ PASS
- Specification created before implementation
- Full workflow: Spec → Plan → Tasks → Implementation

**Principle II - Agentic Workflow Compliance**: ✅ PASS
- Using specialized agents (backend-core for FastAPI)
- All code generation via Claude Code

**Principle III - Security-First Design**: ✅ PASS
- JWT validation on chat endpoint (every request)
- MCP tools validate user_id from token
- User-scoped database queries for conversations

**Principle IV - Deterministic Behavior**: ✅ PASS
- Agent behavior constrained by system prompt
- Tool invocations deterministic (stateless functions)
- Errors explicit and documented

**Principle V - Full-Stack Coherence**: ✅ PASS
- API response matches schema
- Database queries properly scoped
- No secrets in code

**Principle VI - Traceability**: ✅ PASS
- PHR created for planning
- All decisions documented
- Converstion reconstructed from persistent history

**Principle VII - Natural Language as First-Class Interface**: ✅ PASS
- Chat endpoint accepts natural language
- Agent converts to tool calls
- All task operations accessible via conversation

**Principle VIII - Tool-Driven AI Architecture**: ✅ PASS
- Agent uses MCP tools exclusively
- No direct database access from agent
- Tools are stateless and testable

**Principle IX - Fully Stateless Server Architecture**: ✅ PASS
- Chat endpoint stores no in-memory state
- Conversation history in database
- Server restart doesn't lose context

**Principle X - User Identity Enforcement at Tool Level**: ✅ PASS
- JWT validated at API entry point
- User_id extracted and trusted
- MCP tools verify user_id in parameters

**Gate Evaluation**: ✅ ALL GATES PASS - No violations, no justifications needed

---

## Phase 1: Design & Contracts

### Data Model

**Entity: Conversation**
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (UUID, FK): Owner of conversation, indexed
- `title` (str, optional): User-provided conversation name
- `created_at` (datetime): When conversation started
- `updated_at` (datetime): Last message time
- Relationships: Messages (one-to-many), User (many-to-one)
- Validation: user_id must be valid User, title max 255 chars

**Entity: Message**
- `id` (UUID, PK): Unique message identifier
- `conversation_id` (UUID, FK): Parent conversation, indexed
- `user_id` (UUID, FK): Message sender (same as conversation user_id)
- `role` (enum: "user" | "assistant"): Message source
- `content` (str): Message text (1-50000 chars)
- `tool_calls` (JSON, optional): MCP tools invoked (agent messages only)
- `created_at` (datetime): When message was sent
- Relationships: Conversation (many-to-one), User (many-to-one)
- Validation: user_id matches conversation user_id, role valid enum, content non-empty

**State Transitions**:
- Conversation: Created → Active (receiving messages) → Archived (optional, >90 days)
- Message: Created → Persisted (immediately after creation)

### API Contracts

**Endpoint 1: Create Chat Message**

```
POST /api/chat
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",  (optional, create new if missing)
  "message": "Add a task to buy groceries"
}

Response (200 OK):
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_message": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "role": "user",
    "content": "Add a task to buy groceries",
    "created_at": "2026-01-16T12:00:00Z"
  },
  "agent_response": {
    "id": "e47ac10b-58cc-4372-a567-0e02b2c3d479",
    "role": "assistant",
    "content": "✓ I've added 'buy groceries' to your task list!",
    "tool_calls": [
      {
        "tool": "add_task",
        "parameters": { "title": "buy groceries", "description": null },
        "result": { "id": "123e4567-e89b-12d3-a456-426614174000", "title": "buy groceries", ... }
      }
    ],
    "created_at": "2026-01-16T12:00:01Z"
  }
}

Error (400 Bad Request):
{
  "error": "VALIDATION_ERROR",
  "message": "Message cannot be empty"
}

Error (401 Unauthorized):
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Invalid or expired JWT token"
}

Error (500 Internal Server Error):
{
  "error": "DATABASE_ERROR",
  "message": "Failed to persist conversation"
}
```

**Endpoint 2: Get Conversation History**

```
GET /api/chat/{conversation_id}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Tasks",
  "created_at": "2026-01-15T08:00:00Z",
  "messages": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "role": "user",
      "content": "Show me my tasks",
      "created_at": "2026-01-15T08:00:00Z"
    },
    {
      "id": "e47ac10b-58cc-4372-a567-0e02b2c3d479",
      "role": "assistant",
      "content": "You have 3 tasks: ...",
      "created_at": "2026-01-15T08:00:01Z"
    }
  ]
}
```

---

## Phase 2: Implementation Approach

### Module 1: Conversation Service
**File**: `backend/src/services/conversation_service.py`
- Create/fetch conversation
- Persist user messages
- Persist agent responses
- Retrieve conversation history with ordering
- Validate user authorization

### Module 2: Agent Service
**File**: `backend/src/services/agent_service.py`
- Initialize OpenAI Agent with system prompt
- Register MCP tools
- Process user message with context
- Handle tool invocations
- Format responses

### Module 3: Tool Adapter
**File**: `backend/src/services/tool_adapter.py`
- Convert MCP tool schemas to OpenAI Agent format
- Bridge tool call results back to agent
- Error handling and transformation

### Module 4: Chat Endpoint
**File**: `backend/src/api/routes/chat.py`
- JWT validation
- User_id extraction
- Request validation
- Call conversation_service to fetch history
- Call agent_service to process message
- Persist result
- Return formatted response

### Module 5: Data Models
**File**: `backend/src/models/conversation.py`
- Conversation SQLModel
- Message SQLModel
- Validation rules
- Relationships

---

## Success Metrics

1. **Correctness**: Agent invokes correct MCP tool 95% of the time for varied natural language inputs
2. **Latency**: Chat response within 3 seconds (median)
3. **Persistence**: Conversation history fully reconstructible after server restart
4. **Security**: 100% of unauthorized requests rejected with 401/403
5. **Statelessness**: Zero in-memory session storage; all state in database
6. **Scalability**: Multiple servers handle same user without conflicts

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Agent misinterprets natural language | User frustration, wrong actions | Clear system prompt, tool validation |
| Database connection loss during chat | User message lost | Transaction rollback, retry logic |
| Token expires mid-operation | Orphaned messages | Validate token per-request, handle gracefully |
| Rapid message flooding | Performance degradation | Rate limiting, queue management |
| Tool response timeout | Hung conversation | Timeout wrapper around tool calls |

---

## Next Phase

After this planning is approved:
1. Run `/sp.tasks` to break down into specific implementation tasks
2. Use backend-core agent to implement each module
3. Create comprehensive tests for each service
4. Integration test with MCP tools
