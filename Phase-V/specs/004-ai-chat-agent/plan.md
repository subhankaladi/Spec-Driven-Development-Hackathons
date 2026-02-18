# Implementation Plan: AI Chat Agent & Integration

**Branch**: `004-ai-chat-agent` | **Date**: 2026-01-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chat-agent/spec.md`

## Summary

Implement an AI-powered chat interface for natural language todo management. Users send conversational messages to an AI agent that interprets intent and executes task operations (create, read, update, delete) through MCP tools. The system maintains stateless architecture with conversation history persisted in database, enabling seamless conversation resumption after application restart.

**Technical Approach**: Extend existing FastAPI backend with a chat endpoint that integrates OpenAI Agents SDK. Agent processes user messages, invokes MCP tools for task operations, and returns responses. All conversation messages and tool invocations persist to Neon PostgreSQL. Frontend adds chat UI component that communicates with the chat API using existing JWT authentication.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, OpenAI Agents SDK (latest), MCP SDK (official), SQLModel 0.0.14+
- Frontend: Next.js 16.1+, React 19+, Axios 1.13+

**Storage**: Neon Serverless PostgreSQL (existing connection from Phase-II)
**Testing**: pytest (backend contract tests), Jest (frontend component tests)
**Target Platform**: Web application (localhost development, cloud deployment ready)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- Agent response time: <3s for simple commands, <5s for complex commands
- Conversation history load: <1s
- Database operations: <500ms per query

**Constraints**:
- Stateless agent operation (no in-memory conversation state)
- MCP tools only for task operations (no direct database access by agent)
- JWT authentication from Phase-II required for all chat requests
- All conversation data must persist immediately
- User isolation enforced (users see only their own conversations)

**Scale/Scope**:
- Single conversation per user initially
- Support up to 100 messages per conversation
- Agent handles 4 task operation types: create, read, update, delete
- 10-20 concurrent chat sessions expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
**Status**: ✅ PASS
- Feature specification complete at `specs/004-ai-chat-agent/spec.md`
- Implementation follows approved spec with 5 prioritized user stories

### Principle II: Agentic Workflow Compliance
**Status**: ✅ PASS
- All code generation via Claude Code using specialized agents
- Backend Agent for FastAPI chat endpoint and MCP tools
- Database Agent for Conversation and Message models
- Frontend Agent for chat UI components

### Principle III: Security-First Design
**Status**: ✅ PASS
- JWT authentication enforced on chat endpoint (reusing Phase-II auth)
- User isolation: conversations scoped to authenticated user from JWT
- MCP tools validate user_id matches JWT claims
- No direct database access by agent or frontend

### Principle IV: Deterministic Behavior
**Status**: ✅ PASS
- Chat API follows REST semantics (POST /chat for message submission)
- Agent responses deterministic for given conversation context
- Explicit error handling for all failure modes (timeout, validation, tool errors)
- Conversation state fully determined by database content

### Principle V: Full-Stack Coherence
**Status**: ✅ PASS
- Frontend consumes chat API with exact schema defined in contracts/
- Database queries user-scoped via JWT user_id
- Environment variables for OpenAI API key, database URL
- Frontend and backend share consistent message/conversation models

### Principle VI: Traceability
**Status**: ✅ PASS
- All agent tool invocations logged to ToolInvocation table
- Conversation history provides full audit trail
- PHRs created for all implementation phases

### Principle VII: AI Agent Statelessness
**Status**: ✅ PASS
- Agent rebuilds conversation context from database on every request
- No in-memory conversation state cached between requests
- All messages persist immediately after processing
- Conversation resumption verified through server restart testing

### Principle VIII: MCP Tool-First Execution
**Status**: ✅ PASS
- Agent uses MCP tools exclusively for task operations
- Agent NEVER accesses database directly
- MCP tools defined with explicit schemas and validation
- Architecture: Frontend → Chat API → Agent → MCP Tools → Database

**Overall**: ✅ ALL GATES PASS - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chat-agent/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 database schema
├── contracts/           # Phase 1 API contracts
│   ├── chat-api.yaml    # Chat endpoint OpenAPI spec
│   └── mcp-tools.json   # MCP tool schemas
└── quickstart.md        # Phase 1 setup guide
```

### Source Code (repository root: phase-III/)

```text
backend/
├── src/
│   ├── models/
│   │   ├── database.py       # Existing database connection
│   │   ├── user.py           # Existing User model
│   │   ├── task.py           # Existing Task model
│   │   ├── conversation.py   # NEW: Conversation model
│   │   └── message.py        # NEW: Message model
│   ├── services/
│   │   ├── auth_service.py   # Existing JWT validation
│   │   ├── task_service.py   # Existing task CRUD operations
│   │   ├── mcp_tools.py      # NEW: MCP tool definitions
│   │   ├── agent_service.py  # NEW: OpenAI agent integration
│   │   └── conversation_service.py  # NEW: Conversation/message CRUD
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py       # Existing authentication routes
│   │   │   ├── tasks.py      # Existing task routes
│   │   │   └── chat.py       # NEW: Chat endpoint
│   │   ├── schemas/
│   │   │   └── chat.py       # NEW: Chat request/response schemas
│   │   └── dependencies/
│   │       └── auth.py       # Existing JWT dependency
│   ├── config.py             # Existing settings
│   └── main.py               # Main FastAPI app (updated)
└── tests/
    ├── contract/
    │   └── test_chat_api.py  # NEW: Chat endpoint contract tests
    └── integration/
        └── test_agent_flow.py  # NEW: End-to-end agent tests

frontend/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── chat/
│   │   │       └── page.tsx  # NEW: Chat UI page
│   │   └── layout.tsx        # Existing layout
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx   # NEW: Main chat component
│   │   │   ├── MessageList.tsx     # NEW: Message display
│   │   │   ├── MessageInput.tsx    # NEW: Input field
│   │   │   └── MessageBubble.tsx   # NEW: Individual message
│   │   └── ui/               # Existing UI components
│   ├── hooks/
│   │   └── useChat.ts        # NEW: Chat API integration hook
│   ├── lib/
│   │   └── api/
│   │       └── chat.ts       # NEW: Chat API client
│   └── types/
│       └── chat.ts           # NEW: Chat type definitions
└── tests/
    └── components/
        └── chat/
            └── ChatInterface.test.tsx  # NEW: Chat component tests
```

**Structure Decision**: Web application structure (backend + frontend) selected based on existing Phase-II architecture. Chat feature adds new routes, models, and components to existing codebase without restructuring. MCP tools implemented as Python service layer (not separate server) for simplicity.

## Complexity Tracking

No constitution violations requiring justification. All principles satisfied by design.

## Phase 0: Research

Research tasks completed:

### R001: OpenAI Agents SDK Integration Patterns

**Decision**: Use OpenAI Agents SDK in stateless mode with conversation history passed as context

**Rationale**:
- SDK supports loading conversation history from external storage
- Agent can be instantiated per-request without maintaining state
- SDK provides built-in tool calling mechanism compatible with MCP tools

**Alternatives Considered**:
- LangChain: More complex, overkill for single-agent use case
- Custom agent implementation: Reinventing wheel, less reliable than official SDK

**Best Practices**:
- Pass full conversation history on each request (last N messages for performance)
- Use system prompt to define agent behavior and tool usage
- Validate tool responses before persisting to database
- Handle SDK errors gracefully with fallback responses

### R002: MCP Tool Definition and Integration

**Decision**: Implement MCP tools as Python functions with JSON schema validation, registered with OpenAI agent

**Rationale**:
- Official MCP SDK provides schema definition and validation
- Python functions integrate naturally with existing FastAPI codebase
- Agent SDK supports function calling with JSON schemas
- No separate MCP server needed for simple use case

**Alternatives Considered**:
- Separate MCP server: Over-engineered for 4 simple tools
- Direct database access: Violates constitution Principle VIII
- REST API calls: Unnecessary network overhead for in-process calls

**Best Practices**:
- Define explicit input/output schemas for each tool
- Tools should be pure functions (stateless, deterministic given inputs)
- Each tool validates user_id matches authenticated user
- Log all tool invocations to ToolInvocation table for traceability

### R003: Conversation Persistence Strategy

**Decision**: Store conversations and messages in PostgreSQL with immediate write-through on every message

**Rationale**:
- Guarantees data durability and enables stateless architecture
- Existing Neon PostgreSQL connection from Phase-II
- Simple schema extension (2 new tables: conversations, messages)
- Query performance acceptable for <100 messages per conversation

**Alternatives Considered**:
- Redis cache: Adds complexity, risk of data loss on crash
- Event sourcing: Over-engineered for MVP
- Lazy persistence: Violates Principle VII (immediate persistence required)

**Best Practices**:
- Conversation loaded once per request with all messages
- Messages inserted immediately after agent response
- Use database transactions to ensure atomicity
- Index on user_id and created_at for efficient queries

### R004: Frontend Chat UI Integration

**Decision**: Build custom chat component using existing Next.js/React patterns from Phase-II frontend

**Rationale**:
- Consistent with existing Phase-II UI architecture
- Full control over UI/UX and API integration
- Reuse existing authentication and API client patterns
- Simple MVP requirements (no streaming, rich media, or real-time updates)

**Alternatives Considered**:
- Pre-built chat UI library (e.g., ChatKit, Stream Chat): Overkill, vendor lock-in
- WebSocket real-time updates: Not required for MVP, adds complexity
- Server-sent events (SSE): Not needed without streaming responses

**Best Practices**:
- Display messages in chronological order with user/agent distinction
- Show loading state while agent processes message
- Handle API errors with user-friendly messages
- Auto-scroll to latest message on new message arrival
- Load conversation history on page load

## Phase 1: Design

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Summary**:
- **Conversation**: Represents chat session (id, user_id, title, created_at, updated_at)
- **Message**: Individual message (id, conversation_id, role, content, created_at)
- **ToolInvocation**: Audit log for agent actions (id, message_id, tool_name, input, output, success, created_at)

**Relationships**:
- User 1:N Conversation (user can have multiple conversations)
- Conversation 1:N Message (conversation contains multiple messages)
- Message 1:N ToolInvocation (message can trigger multiple tool calls)

**Validation Rules**:
- Conversation.user_id must match authenticated JWT user
- Message.role must be 'user' or 'agent'
- Message.content required, max 5000 characters
- ToolInvocation.tool_name must be one of [create_task, list_tasks, update_task, delete_task]

### API Contracts

See [contracts/](./contracts/) for complete OpenAPI specifications.

**Chat Endpoint Summary**:

```
POST /chat
Headers: Authorization: Bearer <JWT>
Request:
  {
    "conversation_id": "uuid or null (creates new conversation)",
    "message": "string (user message content)"
  }
Response:
  {
    "conversation_id": "uuid",
    "message_id": "uuid",
    "agent_response": "string",
    "tool_invocations": [
      {
        "tool_name": "string",
        "success": boolean,
        "result": "string"
      }
    ]
  }
```

**MCP Tools Summary**:
- `create_task(title: str, description: str | null, user_id: UUID) -> Task`
- `list_tasks(user_id: UUID, is_completed: bool | null) -> List[Task]`
- `update_task(task_id: UUID, user_id: UUID, title: str | null, description: str | null, is_completed: bool | null) -> Task`
- `delete_task(task_id: UUID, user_id: UUID) -> bool`

### Quickstart

See [quickstart.md](./quickstart.md) for complete setup instructions.

**Summary**:
1. Install OpenAI Agents SDK and MCP SDK: `pip install openai-agents mcp-sdk`
2. Add OpenAI API key to backend/.env: `OPENAI_API_KEY=sk-...`
3. Run database migrations to create conversation, message, tool_invocation tables
4. Start backend: `uvicorn src.main:app --reload`
5. Navigate to chat page: http://localhost:3000/chat
6. Send message to agent and verify response

## Re-Evaluation: Constitution Check (Post-Design)

All gates still PASS after Phase 1 design. No changes to initial assessment.

**Design Highlights**:
- Stateless chat endpoint confirmed (conversation loaded from DB per request)
- MCP tools implemented as service layer functions (no direct DB access by agent)
- Full traceability via ToolInvocation audit log
- User isolation enforced at API boundary (JWT validation) and tool layer (user_id checks)

## Next Steps

1. ✅ Phase 0 complete: Research findings documented
2. ✅ Phase 1 complete: Data model, contracts, quickstart defined
3. ⏭️ Run `/sp.tasks` to generate task breakdown
4. ⏭️ Implement Phase 3 using specialized agents (Backend, Database, Frontend)
5. ⏭️ Validate end-to-end flow and conversation resumption

## Architectural Decision Records (ADRs)

**Significant Decisions Requiring Documentation**:

1. **ADR-001: Stateless Agent with Database-Backed Context**
   - Decision: Agent rebuilds conversation context from database on every request
   - Alternatives: In-memory session cache, Redis distributed cache
   - Rationale: Simplicity, durability, horizontal scaling, crash recovery
   - Impact: Slight latency increase (<500ms) but guaranteed consistency

2. **ADR-002: MCP Tools as In-Process Python Functions**
   - Decision: Implement MCP tools as Python service layer functions
   - Alternatives: Separate MCP server, REST API, direct DB access
   - Rationale: Simplicity, performance, type safety, constitution compliance
   - Impact: Tight coupling to Python backend, but acceptable for MVP

3. **ADR-003: Single Conversation Per User**
   - Decision: Users have one active conversation at a time
   - Alternatives: Multi-conversation support, conversation switching
   - Rationale: Simplifies MVP, reduces complexity, can extend later
   - Impact: Limits use cases but meets Phase-III goals

**Recommendation**: Document these decisions with:
```bash
/sp.adr "Stateless Agent with Database-Backed Context"
/sp.adr "MCP Tools as In-Process Python Functions"
/sp.adr "Single Conversation Per User"
```

## Notes

- Agent system prompt should emphasize task management domain and available tools
- Consider rate limiting chat endpoint to prevent abuse (not in MVP scope)
- Future enhancements: multi-conversation support, message search, conversation export
- Performance optimization: load last N messages instead of full history if conversation grows large
