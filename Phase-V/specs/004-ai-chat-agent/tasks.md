---

description: "Task list for AI Chat Agent & Integration implementation"
---

# Tasks: AI Chat Agent & Integration

**Input**: Design documents from `/specs/004-ai-chat-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks included - not explicitly requested in feature specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths relative to phase-III/ repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install OpenAI SDK in backend/requirements.txt (add openai>=1.0.0)
- [x] T002 Install MCP SDK in backend/requirements.txt (add mcp-sdk>=0.1.0)
- [x] T003 [P] Add OpenAI configuration to backend/src/config.py (OPENAI_API_KEY, OPENAI_MODEL, AGENT_MAX_TOKENS)
- [x] T004 [P] Update backend/.env.example with OpenAI environment variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Conversation model in backend/src/models/conversation.py with SQLModel schema
- [x] T006 Create Message model in backend/src/models/message.py with SQLModel schema
- [x] T007 Create ToolInvocation model in backend/src/models/tool_invocation.py with SQLModel schema
- [x] T008 Generate Alembic migration for conversation, message, tool_invocation tables
- [x] T009 Apply database migration (alembic upgrade head)
- [x] T010 [P] Create conversation service CRUD operations in backend/src/services/conversation_service.py
- [x] T011 [P] Create chat request/response schemas in backend/src/api/schemas/chat.py
- [x] T012 [P] Create chat type definitions in frontend/src/types/chat.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Task via Chat (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through natural language chat messages

**Independent Test**: Send message "Create a task to buy milk" and verify task appears in task list with agent confirmation

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement create_task MCP tool in backend/src/services/mcp_tools.py
- [x] T014 [P] [US1] Create agent service with OpenAI SDK integration in backend/src/services/agent_service.py
- [x] T015 [US1] Implement chat endpoint POST /chat in backend/src/api/routes/chat.py (depends on T013, T014)
- [x] T016 [US1] Register chat route in backend/src/main.py
- [x] T017 [US1] Add conversation context loading logic to agent service (load messages from DB)
- [x] T018 [US1] Add message persistence logic to chat endpoint (save user and agent messages)
- [x] T019 [US1] Add tool invocation logging to chat endpoint (save to ToolInvocation table)
- [x] T020 [P] [US1] Create chat API client in frontend/src/lib/api/chat.ts
- [x] T021 [P] [US1] Create useChat hook in frontend/src/hooks/useChat.ts
- [x] T022 [P] [US1] Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx
- [x] T023 [US1] Create MessageList component in frontend/src/components/chat/MessageList.tsx (depends on T022)
- [x] T024 [P] [US1] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx
- [x] T025 [US1] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (depends on T021, T023, T024)
- [x] T026 [US1] Create chat page in frontend/src/app/(dashboard)/chat/page.tsx (depends on T025)
- [x] T027 [US1] Add error handling for agent failures in chat endpoint
- [x] T028 [US1] Add loading states to ChatInterface component

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - List Tasks via Chat (Priority: P2)

**Goal**: Enable users to view their tasks through natural language queries

**Independent Test**: Send message "Show me my tasks" and verify agent returns formatted task list

### Implementation for User Story 2

- [x] T029 [US2] Implement list_tasks MCP tool in backend/src/services/mcp_tools.py
- [x] T030 [US2] Register list_tasks tool with agent service in backend/src/services/agent_service.py
- [x] T031 [US2] Update agent system prompt to handle list queries
- [x] T032 [US2] Add task formatting logic to agent responses for readable task lists

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 5 - Resume Conversation After Restart (Priority: P2)

**Goal**: Enable conversation persistence and resumption across application restarts

**Independent Test**: Create conversation with 5 messages, restart application, verify all messages load correctly

### Implementation for User Story 5

- [x] T033 [US5] Add conversation history loading on chat page mount in frontend/src/hooks/useChat.ts (implemented via useEffect on mount)
- [x] T034 [US5] Implement GET conversation history endpoint in backend/src/api/routes/chat.py (GET /{conversation_id})
- [x] T035 [US5] Add conversation ID persistence to chat interface with localStorage (chat_conversation_id key)
- [x] T036 [US5] Add auto-scroll to latest message in MessageList component (already implemented in useChat hook)
- [x] T037 [US5] Test stateless operation: Stop/start backend server and verify conversation resumption works (documented in quickstart.md Step 10)

**Checkpoint**: At this point, User Stories 1, 2, AND 5 should all work independently

---

## Phase 6: User Story 3 - Update Task via Chat (Priority: P3)

**Goal**: Enable users to modify existing tasks through conversational commands

**Independent Test**: Create task, send "Mark 'Buy milk' as complete", verify task updated

### Implementation for User Story 3

- [x] T038 [US3] Implement update_task MCP tool in backend/src/services/mcp_tools.py
- [x] T039 [US3] Register update_task tool with agent service in backend/src/services/agent_service.py
- [x] T040 [US3] Update agent system prompt to handle update commands with task identification
- [x] T041 [US3] Add ambiguity handling logic to agent (ask for clarification when task unclear)

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 5 should all work independently

---

## Phase 7: User Story 4 - Delete Task via Chat (Priority: P4)

**Goal**: Enable users to remove tasks through natural language commands

**Independent Test**: Create task, send "Delete 'Old task'", verify task removed from list

### Implementation for User Story 4

- [x] T042 [US4] Implement delete_task MCP tool in backend/src/services/mcp_tools.py
- [x] T043 [US4] Register delete_task tool with agent service in backend/src/services/agent_service.py
- [x] T044 [US4] Update agent system prompt to handle delete commands with confirmation
- [x] T045 [US4] Add deletion confirmation logic to agent responses

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T046 [P] Add input validation to chat endpoint (message length, content sanitization)
- [x] T047 [P] Add comprehensive error messages for all agent failure modes
- [x] T048 [P] Add logging for all MCP tool invocations in backend/src/services/mcp_tools.py
- [x] T049 [P] Add user isolation validation to all MCP tools (verify user_id matches JWT)
- [x] T050 [P] Add API documentation comments to chat endpoint and schemas
- [x] T051 [P] Add TypeScript type safety improvements to frontend chat components
- [x] T052 [P] Add responsive design improvements to chat interface for mobile
- [x] T053 Run quickstart.md validation end-to-end
- [x] T054 Verify constitution compliance (statelessness, MCP tool-first, user isolation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US2 (P2): Can start after Foundational - Builds on US1 agent infrastructure but independently testable
  - US5 (P2): Can start after Foundational - Builds on US1 persistence infrastructure but independently testable
  - US3 (P3): Can start after Foundational - Builds on US1 agent and US2 tools but independently testable
  - US4 (P4): Can start after Foundational - Builds on US1 agent and US2 tools but independently testable
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP COMPLETE**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Leverages US1 agent service but independently testable
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Leverages US1 persistence but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Leverages US1 agent and US2 tools but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Leverages US1 agent and US2 tools but independently testable

### Within Each User Story

- Models before services (Foundational phase ensures all models ready)
- Services before endpoints (MCP tools and agent service before chat endpoint)
- Backend before frontend (chat endpoint before chat UI)
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story:
  - MCP tools, agent service updates, and frontend components can be worked on in parallel if files don't conflict
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch these tasks together (different files, no dependencies):
Task: "T013 [P] [US1] Implement create_task MCP tool in backend/src/services/mcp_tools.py"
Task: "T014 [P] [US1] Create agent service with OpenAI SDK in backend/src/services/agent_service.py"
Task: "T020 [P] [US1] Create chat API client in frontend/src/lib/api/chat.ts"
Task: "T021 [P] [US1] Create useChat hook in frontend/src/hooks/useChat.ts"
Task: "T022 [P] [US1] Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx"
Task: "T024 [P] [US1] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx"

# Then launch these (depend on above tasks):
Task: "T015 [US1] Implement chat endpoint in backend/src/api/routes/chat.py"
Task: "T023 [US1] Create MessageList component (depends on T022)"
Task: "T025 [US1] Create ChatInterface component (depends on T021, T023, T024)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install dependencies, configure OpenAI)
2. Complete Phase 2: Foundational (database models, migrations, schemas) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (create task via chat)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send "Create a task to buy milk"
   - Verify task appears in /tasks page
   - Verify agent confirms creation
   - Verify conversation persists to database
5. Deploy/demo if ready - **MVP ACHIEVED**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (**MVP!**)
3. Add User Story 2 → Test independently → Deploy/Demo (enhanced with list capability)
4. Add User Story 5 → Test independently → Deploy/Demo (conversation resumption validated)
5. Add User Story 3 → Test independently → Deploy/Demo (update capability)
6. Add User Story 4 → Test independently → Deploy/Demo (full CRUD via chat)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (P1) - Create task via chat
   - Developer B: User Story 2 (P2) - List tasks via chat
   - Developer C: User Story 5 (P2) - Conversation resumption
3. Stories complete and integrate independently
4. Proceed to P3 and P4 as needed

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4, US5)
- Each user story should be independently completable and testable
- User Story 1 (P1) represents the MVP - functional chat agent that can create tasks
- User Story 5 (P2) validates stateless architecture requirement (conversation persistence)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (US1 - Create Task)**: 16 tasks
- **Phase 4 (US2 - List Tasks)**: 4 tasks
- **Phase 5 (US5 - Resume Conversation)**: 5 tasks
- **Phase 6 (US3 - Update Task)**: 4 tasks
- **Phase 7 (US4 - Delete Task)**: 4 tasks
- **Phase 8 (Polish)**: 9 tasks
- **TOTAL**: 54 tasks

**Parallel Opportunities**: 22 tasks marked [P] can run in parallel within their phase
**MVP Scope**: Phases 1-3 (28 tasks) deliver User Story 1 - fully functional chat agent for task creation
