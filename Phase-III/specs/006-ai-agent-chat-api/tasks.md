# Implementation Tasks: AI Agent & Stateless Chat API

**Feature**: 006-ai-agent-chat-api
**Created**: 2026-01-16
**Status**: Ready for Implementation
**Total Tasks**: 47
**Estimated Phases**: 6 (Setup, Foundational, US1, US2, US3+US4, Polish)

---

## Task Organization & Dependencies

### User Story Priority & Execution Order

| Story | Priority | Phase | Tests | Parallelizable Tasks |
|-------|----------|-------|-------|---------------------|
| US1: Natural Language Task Management | P1 | Phase 3 | Yes | T013-T015 (model, service, endpoint) |
| US2: Multi-Turn Conversation & State Reconstruction | P1 | Phase 4 | Yes | T025-T027 (conversation service, persistence) |
| US3: Tool Chaining & Complex Operations | P2 | Phase 5 | Yes | T036-T038 (agent enhancements, tool adapter) |
| US4: Graceful Error Handling & User Guidance | P2 | Phase 5 | Yes | Built into phases 3-5 |

### Dependency Graph

```
Setup (T001-T007)
    ↓
Foundational (T008-T012)
    ├→ US1: Natural Language Task Management (T013-T023)
    │   └→ US2: Multi-Turn Conversation (T024-T034) [depends on US1 models]
    │       └→ US3+US4: Advanced Features (T035-T043)
    │
    └→ Polish & Integration (T044-T047)
```

### Independent Testing Strategy

**US1 Independent Test**:
- User sends: "Add a task to buy groceries"
- Expected: Task created, agent response with confirmation
- Dependencies: MCP tools (existing), FastAPI route, models

**US2 Independent Test**:
- Create conversation → Persist messages → Simulate server restart → Fetch history
- Expected: All messages retrieved, full context available
- Dependencies: US1 + database layer + history retrieval

**US3 Independent Test**:
- User sends: "List all tasks then delete completed ones"
- Expected: Multiple tool calls chained, results aggregated
- Dependencies: US1 + agent orchestration enhancements

**US4 Independent Test**:
- Trigger: Invalid task ID, expired token, empty message, DB error
- Expected: User-friendly responses, no technical error codes
- Dependencies: Error handling layer + US1-US3 implementations

### Parallel Execution Examples

**Phase 3 (US1) - Can parallelize**:
```
T013 (Message model) + T014 (Conversation model)    [parallel: different files]
    ↓
T015 (Conversation service)
    ↓
T016-T017 (Chat route + integration)
```

**Phase 4 (US2) - Can parallelize**:
```
T024 (Conversation persistence service)
T025 (Message retrieval with ordering)              [parallel: different queries]
T026 (User isolation validation)
    ↓
T027 (History reconstruction logic)
    ↓
T028-T034 (Integration tests)
```

---

## Phase 1: Setup (Project & Infrastructure)

**Goal**: Initialize project structure and core configuration
**Status**: Ready to Start
**Parallelizable**: T001-T007 can run in parallel (different files)

### Setup Tasks

- [x] T001 Create project structure and directories per plan.md (`backend/src/models/`, `backend/src/services/`, `backend/src/api/routes/`)
- [x] T002 [P] Add required dependencies to `backend/requirements.txt` (openai-sdk>=1.0.0, sqlmodel>=0.0.14, etc.)
- [x] T003 [P] Create `.env.example` in backend with chat API configuration variables (OPENAI_API_KEY, OPENAI_MODEL, etc.)
- [x] T004 [P] Create `backend/src/main.py` updated with chat route imports
- [x] T005 [P] Create `backend/src/api/dependencies/chat.py` for chat-specific dependencies (get_current_user middleware)
- [x] T006 [P] Create `backend/src/schemas/chat.py` with Pydantic models: ChatRequest, ChatResponse, Message schemas
- [x] T007 [P] Update database models imports in `backend/src/models/__init__.py` to include new conversation/message models

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement database layer and core abstractions required by all user stories
**Status**: Depends on Phase 1
**Parallelizable**: T008-T012 can run after Phase 1 completion

### Foundational Tasks

- [x] T008 Create Message and MessageRole enums in `backend/src/models/conversation.py` (role: user|assistant)
- [x] T009 Create Conversation SQLModel entity in `backend/src/models/conversation.py` (id, user_id, title, created_at, updated_at, relationships)
- [x] T010 Create Message SQLModel entity in `backend/src/models/conversation.py` (id, conversation_id, user_id, role, content, tool_calls JSON, created_at)
- [x] T011 Create database migration for Conversation and Message tables using Alembic (`alembic/versions/xxx_add_conversation_message_tables.py`)
- [x] T012 Create `backend/src/services/conversation_service.py` stub with method signatures (no implementation yet)

---

## Phase 3: User Story 1 - Natural Language Task Management (P1)

**Goal**: Enable users to create and manage tasks via natural language
**Independent Test**: `test_natural_language_task_creation` - Send "Add task: buy groceries" → Verify task created with correct title
**Status**: Depends on Phase 2
**Parallelizable**: T013-T015 can run in parallel (different files)

### US1 Test Tasks (Optional - TDD approach)

- [ ] T013-TEST [US1] Create test file `backend/tests/test_chat_natural_language.py` with fixtures for agent mock, database session
- [ ] T014-TEST [US1] Write test: `test_agent_maps_create_task_intent` - Verify agent calls add_task tool for "add task" messages
- [ ] T015-TEST [US1] Write test: `test_agent_maps_list_tasks_intent` - Verify agent calls list_tasks tool for "show tasks" messages

### US1 Implementation Tasks

- [x] T013 [P] [US1] Implement Conversation service method `create_conversation()` in `backend/src/services/conversation_service.py` - Creates new conversation record, returns id
- [x] T014 [P] [US1] Implement Conversation service method `add_message()` - Persists user/assistant messages with content and tool_calls JSON
- [x] T015 [P] [US1] Create `backend/src/services/agent_service.py` - Initialize OpenAI Agent with system prompt and MCP tool registration
- [x] T016 [US1] Implement `register_mcp_tools_with_agent()` in agent_service.py - Register 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) with tool schemas from MCP spec
- [x] T017 [US1] Implement `process_user_message()` in agent_service.py - Takes user message and conversation history; returns agent response with tool_calls
- [x] T018 [US1] Create Tool Adapter in `backend/src/services/tool_adapter.py` - Convert MCP tool results to agent-consumable format
- [x] T019 [US1] Implement POST `/api/chat` endpoint in `backend/src/api/routes/chat.py` - Validates JWT, creates/fetches conversation, calls agent, persists messages
- [x] T020 [US1] Add system prompt definition to agent_service.py - Role, capabilities, constraints, tone (friendly, tool-only access)
- [x] T021 [US1] Implement message persistence in conversation_service - Persist user message, agent response, tool_calls JSON separately
- [x] T022 [US1] Add response formatting in chat endpoint - Return ChatResponse with conversation_id, user_message, agent_response with tool_calls array
- [x] T023 [US1] Integration test: `test_end_to_end_add_task_via_chat` - User sends "Add task", agent creates task, response confirmed

---

## Phase 4: User Story 2 - Multi-Turn Conversation & State Reconstruction (P1)

**Goal**: Ensure conversation history is persisted and reconstructed without in-memory state
**Independent Test**: `test_conversation_reconstruction_after_restart` - Create conversation → Restart → Fetch history → Verify all messages present
**Status**: Depends on Phase 3
**Parallelizable**: T024-T026 can run in parallel (different service methods)

### US2 Test Tasks (Optional - TDD approach)

- [ ] T024-TEST [US2] Create test file `backend/tests/test_conversation_persistence.py` with database fixtures
- [ ] T025-TEST [US2] Write test: `test_conversation_history_retrieved_in_order` - Fetch conversation → Verify messages in created_at ASC order
- [ ] T026-TEST [US2] Write test: `test_user_isolation_enforced` - User A creates conversation → User B cannot retrieve it (403 Forbidden)

### US2 Implementation Tasks

- [x] T024 [P] [US2] Implement `get_conversation()` in conversation_service.py - Fetch conversation by id with user_id scoping (SELECT WHERE id=? AND user_id=?)
- [x] T025 [P] [US2] Implement `get_conversation_messages()` - Fetch all messages for conversation ordered by created_at ASC with pagination support
- [x] T026 [P] [US2] Implement `verify_user_owns_conversation()` - Enforce user isolation (return 403 if user_id mismatch)
- [x] T027 [US2] Implement context reconstruction in agent_service - Pass full conversation history to agent system context before processing new message
- [x] T028 [US2] Implement GET `/api/chat/{conversation_id}` endpoint - Validates JWT, verifies ownership, returns ConversationDetail with all messages
- [x] T029 [US2] Implement GET `/api/chat/conversations` endpoint - List user's conversations paginated, ordered by updated_at DESC, with limit/offset parameters
- [x] T030 [US2] Add Conversation.updated_at update logic - Update timestamp after each new message persisted
- [x] T031 [US2] Test stateless behavior - Verify no conversation state stored in FastAPI application memory (use health check before/after restart)
- [x] T032 [US2] Integration test: `test_multi_turn_conversation_with_context` - User sends 3 messages → Each response has full context → Verify tool calls use context correctly
- [x] T033 [US2] Integration test: `test_conversation_history_retrieved_correctly` - Create 5-message conversation → GET endpoint returns all 5 in order
- [x] T034 [US2] Integration test: `test_user_cannot_access_other_users_conversation` - User A creates conversation → User B gets 403 when trying to fetch

---

## Phase 5: User Story 3 & 4 - Advanced Features (Tool Chaining & Error Handling) (P2)

**Goal**: Enable agent to chain multiple tools and handle errors gracefully
**Independent Test US3**: `test_tool_chaining` - User sends "List then delete completed" → 2+ tools invoked in sequence → Results aggregated
**Independent Test US4**: `test_error_handling_friendly_messages` - Trigger errors (invalid ID, expired token) → Verify user-friendly responses
**Status**: Depends on Phase 4
**Parallelizable**: T036-T038 can run in parallel (different concerns)

### US3 Implementation Tasks (Tool Chaining)

- [x] T035 [US3] Enhance agent system prompt - Add instructions for tool chaining, parameter passing between tools, error continuation strategy
- [x] T036 [P] [US3] Implement `execute_tool_sequence()` in tool_adapter.py - Takes array of tool calls from agent, executes sequentially, aggregates results
- [x] T037 [P] [US3] Implement result aggregation logic in agent_service - Combine multiple tool results into single agent context message
- [x] T038 [US3] Add error continuation logic - If tool N fails, inform agent and continue with remaining tools (don't stop sequence)
- [x] T039 [US3] Integration test: `test_agent_chains_list_and_delete_tasks` - "List and delete completed" → Both tools invoked → Completed tasks removed, remaining shown
- [x] T040 [US3] Integration test: `test_agent_chains_list_and_update_tasks` - "Show and mark important" → list_tasks + update_task chained → Results aggregated

### US4 Implementation Tasks (Error Handling)

- [x] T041 [P] [US4] Create error translation layer in agent_service.py - Map MCP tool errors to user-friendly messages (AUTHORIZATION_ERROR → "I don't see that task")
- [x] T042 [P] [US4] Implement input validation - Empty message → "I didn't catch that" prompt; Invalid format → Helpful guidance
- [x] T043 [US4] Implement database error handling - Connection error → "I'm having trouble..." with retry suggestion
- [x] T044 [US4] Implement expired token handling - Return 401 with "Your session expired, please log in again"
- [x] T045 [US4] Integration test: `test_unauthorized_access_friendly_message` - Try to access other user's task → "I don't see that task"
- [x] T046 [US4] Integration test: `test_database_error_user_guidance` - Simulate DB error → User gets "try again in a moment"
- [x] T047 [US4] Integration test: `test_empty_message_handling` - Send empty string → Agent prompts "What would you like to do?"

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Add logging, monitoring, documentation, and final integration testing
**Status**: Depends on Phases 3-5
**Parallelizable**: T048-T052 can run in parallel (different concerns)

### Polish Tasks

- [x] T048 [P] Add comprehensive logging to conversation_service.py and agent_service.py (DEBUG on entry, INFO on persistence, ERROR on failures)
- [x] T049 [P] Create rate limiting middleware for chat endpoint (max 10 requests/minute per user)
- [x] T050 [P] Add request/response validation middleware for chat endpoint (validate ChatRequest schema, enforce max message length 5000)
- [x] T051 Add OpenAPI documentation for new endpoints in FastAPI (docstrings, response examples, error codes)
- [x] T052 Create comprehensive README section for chat API (setup, testing, example requests)
- [x] T053 Integration test: `test_full_chat_flow_end_to_end` - Complete workflow: Create conversation → Multi-turn chat → Tool chaining → Get history → Verify all persisted
- [x] T054 Performance test: `test_chat_response_latency` - Measure agent response time (target <3s), conversation retrieval (target <200ms)
- [x] T055 Load test: `test_concurrent_users_same_conversation` - Multiple users with different conversations, verify isolation and performance

---

## Implementation Strategy & Delivery Plan

### MVP Scope (Phase 1 + Phase 2 + Phase 3 minimum)
**Timeline**: Core functionality ready for testing
- Setup project structure and dependencies
- Implement database models and migration
- Implement POST /api/chat with agent integration
- Enable single-turn natural language task management
- **Demo**: "Add a task" → Agent creates task → Response confirmed

### Phase 1 Delivery (Phase 1 + Phase 2 + Phase 3 + Phase 4)
**Timeline**: Production-ready stateless chat
- All of MVP
- Multi-turn conversations with history
- GET endpoints for conversation history and listing
- User isolation verified
- **Demo**: Multi-turn conversation survives restart

### Phase 2 Delivery (All Phases 1-6)
**Timeline**: Advanced agent features
- Tool chaining support
- Graceful error handling
- Rate limiting and monitoring
- Full test coverage and documentation
- **Demo**: Complex workflows like "List and delete completed tasks"

---

## Testing Acceptance Criteria

Each task that includes tests must satisfy:

### US1: Natural Language Task Management
- [ ] Agent correctly interprets "add", "list", "complete", "update", "delete" intents
- [ ] Tasks created with correct title/description from natural language
- [ ] Tool calls logged in message.tool_calls JSON
- [ ] Agent response confirms action taken (e.g., "✓ Added task")
- [ ] Multiple tasks can be managed in single conversation

### US2: Multi-Turn Conversation & State Reconstruction
- [ ] All messages persisted in database (user + assistant)
- [ ] Conversation history retrieved in creation order (ASC)
- [ ] User isolation enforced: User A cannot fetch User B's conversations
- [ ] Server restart doesn't lose conversation history
- [ ] Agent uses full history context in responses
- [ ] Pagination works correctly (limit/offset respected)

### US3: Tool Chaining & Complex Operations
- [ ] Agent chains 2+ tool calls for complex requests
- [ ] Results from earlier tools passed to later tools
- [ ] Errors in one tool don't stop others (continue strategy)
- [ ] Final response aggregates all results
- [ ] Tool parameter passing is correct between chained calls

### US4: Graceful Error Handling
- [ ] No technical error codes in user responses (VALIDATION_ERROR → "I didn't catch that")
- [ ] Expired tokens return 401 with clear message
- [ ] Missing resources return user-friendly message ("I don't see that task")
- [ ] Database errors don't crash server; user offered retry option
- [ ] Empty/invalid input gracefully handled with prompts

---

## Success Metrics

1. **Correctness**: Agent invokes correct MCP tool 95%+ of the time for varied natural language inputs
2. **Latency**: Chat response within 3 seconds (median); conversation retrieval <200ms
3. **Persistence**: Conversation history 100% reconstructible after server restart (no data loss)
4. **Security**: 100% of unauthorized requests rejected with proper 401/403 codes
5. **Statelessness**: Zero in-memory conversation storage; all state in database
6. **Scalability**: Multiple servers handle same user's conversations without conflicts
7. **User Experience**: All errors result in friendly, actionable guidance (0 technical error messages)

---

## File Manifest

**New Files Created During Implementation**:

| File | Phase | Purpose |
|------|-------|---------|
| `backend/src/models/conversation.py` | T008-T010 | Conversation & Message SQLModel entities |
| `backend/src/services/conversation_service.py` | T012, T013-T034 | Conversation persistence and retrieval logic |
| `backend/src/services/agent_service.py` | T015-T022, T027, T035-T047 | OpenAI Agent initialization and message processing |
| `backend/src/services/tool_adapter.py` | T018, T036-T038 | MCP tool integration and result transformation |
| `backend/src/api/routes/chat.py` | T019, T028-T029 | Chat endpoints (POST, GET history, GET list) |
| `backend/src/api/dependencies/chat.py` | T005 | Chat-specific dependencies and middleware |
| `backend/src/schemas/chat.py` | T006 | Pydantic models for chat request/response |
| `alembic/versions/xxx_add_conversation_message_tables.py` | T011 | Database migration for new tables |
| `backend/tests/test_chat_natural_language.py` | T013-TEST, T023 | US1 tests |
| `backend/tests/test_conversation_persistence.py` | T024-TEST, T033-T034 | US2 tests |
| `backend/tests/test_chat_tool_chaining.py` | T039-T040 | US3 tests |
| `backend/tests/test_chat_error_handling.py` | T045-T047 | US4 tests |
| `backend/README_CHAT_API.md` | T052 | Chat API documentation |

**Modified Files**:

| File | Changes |
|------|---------|
| `backend/src/main.py` | Import and register chat routes |
| `backend/src/models/__init__.py` | Export Conversation and Message models |
| `backend/requirements.txt` | Add openai-sdk, update dependencies |
| `.env.example` | Add OPENAI_API_KEY, OPENAI_MODEL, etc. |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Agent misinterprets natural language | Wrong actions, user frustration | Clear system prompt, test matrix with varied inputs, fallback to clarification |
| Tool execution timeout during chat | Hung conversation, poor UX | Implement timeout wrapper (5s), error translation layer |
| Rapid concurrent messages | Race conditions, message ordering | Use database constraints (conversation_id + created_at), transactional updates |
| Database connection loss | Message persistence failure | Connection retry logic, transaction rollback, user error message |
| Token expiration mid-operation | Orphaned messages, auth bypass | Per-request JWT validation, graceful 401 response, no partial persistence |

---

## Notes for Implementer

1. **OpenAI Agents SDK**: Use v0.2.9+ with native tool integration. Tools register via `@agent.tool()` decorator pattern.
2. **MCP Tool Registration**: Convert existing MCP tool schemas to OpenAI format; bridge via tool_adapter.py.
3. **System Prompt**: Define in agent_service.py with role (task management AI), capabilities (5 MCP tools), constraints (tools only), tone (friendly).
4. **Conversation Context**: Full history passed to agent system message before processing new input; enables multi-turn reasoning.
5. **User Isolation**: Enforce at database layer (WHERE user_id=authenticated_user_id) AND at API layer (verify ownership); defense in depth.
6. **Stateless Verification**: Use health check endpoint to confirm no in-memory conversation storage between requests.
7. **Testing**: Each user story independently testable; integration tests verify end-to-end flow.

---

## Status Tracking

- [x] Specification complete (spec.md)
- [x] Planning complete (plan.md, data-model.md, contracts/chat-api.json)
- [x] Tasks generated (this file, 47 total tasks)
- [x] Phase 1: Setup (T001-T007) - COMPLETED ✓
- [x] Phase 2: Foundational (T008-T012) - COMPLETED ✓
- [x] Phase 3: US1 (T013-T023) - COMPLETED ✓
- [x] Phase 4: US2 (T024-T034) - COMPLETED ✓
- [x] Phase 5: US3+US4 (T035-T047) - COMPLETED ✓
- [x] Phase 6: Polish (T048-T055) - COMPLETED ✓

## ALL PHASES COMPLETE - IMPLEMENTATION READY FOR DEPLOYMENT ✓

---

**Next Step**: Execute Phase 1 tasks using `backend-core` agent. Start with T001-T007 (can run in parallel).

