---

description: "Task list for AI Agent & Stateless Chat API feature"
---

# Tasks: AI Agent & Stateless Chat API

**Input**: Design documents from `/specs/006-ai-chat-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL and not explicitly requested in the spec; include only smoke/manual validation steps.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Backend app: `backend/src/`
- API routes: `backend/src/api/routes/`
- Chat module: `backend/src/chat/`
- Models: `backend/src/models/`
- Tests (optional): `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create chat module directories per plan in `backend/src/chat/` and `backend/src/api/routes/chat.py`
- [x] T002 [P] Add required dependencies for agent runtime in `backend/pyproject.toml` (OpenAI Agents SDK)
- [x] T003 [P] Add required dependencies for persistence/models in `backend/pyproject.toml` (SQLModel / SQLAlchemy)
- [x] T004 [P] Add required dependencies for schema/validation in `backend/pyproject.toml` (Pydantic)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Conversation model in `backend/src/models/conversation.py` (per specs/006-ai-chat-api/data-model.md)
- [x] T006 Create Message model in `backend/src/models/message.py` (per specs/006-ai-chat-api/data-model.md)
- [x] T007 Update DB startup migration/creation logic to include Conversation + Message tables in `backend/src/database/session.py`
- [x] T008 Implement conversation persistence helpers in `backend/src/chat/persistence.py` (load/create conversation, append message, list recent messages)
- [x] T009 Define request/response schemas in `backend/src/chat/schemas.py` matching `specs/006-ai-chat-api/contracts/chat-api.json`
- [x] T010 Implement MCP client wrapper skeleton in `backend/src/chat/mcp_client.py` (configuration + call interface, no business logic)
- [x] T011 Implement agent system prompt and agent factory in `backend/src/chat/agent.py` (tools wired, behavior rules embedded)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Chat with AI to Manage Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can send natural language messages and the agent uses MCP tools to manage tasks, returning friendly confirmations

**Independent Test**: Call `POST /api/v1/{user_id}/chat` with JWT and verify:
- tool invocation happens for task operations
- tasks are modified via MCP server
- response includes a user-friendly confirmation

### Implementation for User Story 1

- [x] T012 [US1] Create chat route in `backend/src/api/routes/chat.py` with `POST /{user_id}/chat`
- [x] T013 [US1] Enforce user_id match using existing dependency `get_user_id_from_path` in `backend/src/auth/dependencies.py`
- [x] T014 [US1] Register chat router in `backend/src/api/main.py` (include_router under `/api/v1`)
- [x] T015 [US1] Implement request handling flow in `backend/src/api/routes/chat.py`: load conversation → persist user message → run agent → persist assistant message → return response
- [x] T016 [US1] Implement tool invocation plumbing in `backend/src/chat/agent.py` so the agent calls MCP tools for add/list/update/complete/delete
- [x] T017 [US1] Implement deterministic intent-to-tool mapping constraints in the agent system prompt in `backend/src/chat/agent.py`
- [x] T018 [US1] Implement graceful error handling + friendly explanations in `backend/src/api/routes/chat.py` (tool errors, MCP unavailable)

**Checkpoint**: User Story 1 complete - chat endpoint supports task operations via MCP tools

---

## Phase 4: User Story 2 - Resume Conversation After Restart (Priority: P2)

**Goal**: Conversation context persists and is reconstructed from DB on each request (no in-memory state)

**Independent Test**: Send message → restart server → send follow-up message → response reflects prior conversation

### Implementation for User Story 2

- [x] T019 [US2] Implement history reconstruction in `backend/src/chat/persistence.py` (fetch last N messages ordered by timestamp)
- [x] T020 [US2] Pass reconstructed history into agent run context in `backend/src/chat/agent.py`
- [x] T021 [US2] Ensure every request is stateless: no module-level conversation caches in `backend/src/chat/*`
- [x] T022 [US2] Add manual quickstart validation steps to `specs/006-ai-chat-api/quickstart.md` if missing (restart flow)

**Checkpoint**: User Story 2 complete - conversation resumes after restart

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T023 [P] Add structured logging for chat requests and tool invocations in `backend/src/api/routes/chat.py`
- [x] T024 [P] Add configuration validation for required env vars (OPENAI_API_KEY, MCP endpoint) in `backend/src/chat/agent.py` and/or `backend/src/chat/mcp_client.py`
- [x] T025 Add standardized error response formatting aligned with `backend/src/api/main.py:create_error_response`
- [x] T026 Run quickstart.md validation steps manually and record results in `specs/006-ai-chat-api/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational and builds on Story 1 patterns
- **Polish (Phase 5)**: Depends on Stories 1-2

### Parallel Opportunities

- T002-T004 can run in parallel (dependency additions)
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: Foundational

```bash
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/message.py"
Task: "Define request/response schemas in backend/src/chat/schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE with manual curl calls

### Incremental Delivery

1. Build US1 (chat + tool invocation)
2. Add US2 (history reconstruction)
3. Polish (logging/config validation)
