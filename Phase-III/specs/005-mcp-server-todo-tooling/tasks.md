---
description: "Task list for MCP Server & Todo Tooling implementation"
---

# Tasks: MCP Server & Todo Tooling

**Input**: Design documents from `/specs/005-mcp-server-todo-tooling/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, quickstart.md

**Tests**: Tests are OPTIONAL for this feature. Include test tasks only if explicitly requested during implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Each user story represents an MCP tool that can be developed, tested, and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **MCP Server**: `mcp-server/src/` at repository root
- **Backend (reused)**: `backend/src/` for shared models and utilities
- **Tests**: `mcp-server/tests/` for MCP server tests
- All paths are relative to repository root (`/mnt/c/Users/a/Desktop/phase-3/`)

---

## Phase 1: Setup (MCP Server Project Initialization)

**Purpose**: Initialize MCP server project structure and dependencies

**Duration**: Can be completed in single session

- [ ] T001 Create mcp-server/ directory at repository root
- [ ] T002 Initialize Python project with mcp-server/requirements.txt (mcp, sqlmodel, pyjwt, python-dotenv, pytest, pytest-asyncio)
- [ ] T003 Create mcp-server/src/ directory structure (tools/, schemas/, auth/, db/, utils/ subdirectories)
- [ ] T004 [P] Create mcp-server/tests/ directory structure (unit/, integration/, conftest.py)
- [ ] T005 [P] Create mcp-server/.env.example with DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, LOG_LEVEL
- [ ] T006 [P] Create mcp-server/README.md with project overview and setup instructions
- [ ] T007 [P] Create all __init__.py files in mcp-server/src/ subdirectories

**Checkpoint**: Project structure ready for foundational code

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story (tool) can be implemented

**⚠️ CRITICAL**: No tool implementation can begin until this phase is complete

- [ ] T008 Implement error classes in mcp-server/src/utils/errors.py (AuthenticationError, ValidationError, NotFoundError, AuthorizationError, DatabaseError)
- [ ] T009 [P] Implement JWT validator in mcp-server/src/auth/jwt_validator.py (validate_jwt_token function using backend auth service)
- [ ] T010 [P] Implement database session factory in mcp-server/src/db/session.py (async engine creation, session management)
- [ ] T011 Implement tool schemas in mcp-server/src/schemas/tool_schemas.py (JSON schemas for all 5 tools: add_task, list_tasks, update_task, complete_task, delete_task)
- [ ] T012 Create pytest fixtures in mcp-server/tests/conftest.py (test_db_session, test_jwt_token, expired_jwt_token, invalid_jwt_token, test_user, test_tasks)
- [ ] T013 Implement MCP server entry point skeleton in mcp-server/src/server.py (Server instance, lifespan context, empty tool handlers)

**Checkpoint**: Foundation ready - tool implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create new tasks with JWT authentication

**Independent Test**: AI agent invokes add_task with valid JWT and task data → task created in database with correct user_id → structured task object returned with UUID

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement add_task handler in mcp-server/src/tools/add_task.py (JWT validation, input validation, Task creation, structured response)
- [ ] T015 [US1] Register add_task tool in mcp-server/src/server.py (add to list_tools handler, route in call_tool handler)
- [ ] T016 [US1] Add add_task input/output validation logic (title 1-255 chars, optional description, user_id from JWT)
- [ ] T017 [US1] Add error handling for add_task (authentication errors, validation errors, database errors)

**Checkpoint**: At this point, add_task tool should be fully functional - AI agents can create tasks via MCP protocol

---

## Phase 4: User Story 2 - List Tasks Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to retrieve user tasks with filtering and pagination

**Independent Test**: Pre-populate database with tasks → AI agent invokes list_tasks with JWT → only that user's tasks returned with pagination metadata

### Implementation for User Story 2

- [ ] T018 [P] [US2] Implement list_tasks handler in mcp-server/src/tools/list_tasks.py (JWT validation, query with filters, pagination logic, structured response)
- [ ] T019 [US2] Register list_tasks tool in mcp-server/src/server.py (add to list_tools handler, route in call_tool handler)
- [ ] T020 [US2] Add list_tasks pagination validation (page ≥ 1, page_size 1-100, default values)
- [ ] T021 [US2] Add list_tasks filtering logic (completed filter, user_id scoping, ORDER BY created_at DESC)
- [ ] T022 [US2] Add list_tasks response formatting (items array, total count, page metadata, total_pages calculation)

**Checkpoint**: At this point, User Stories 1 AND 2 (add_task, list_tasks) both work independently - this is the MVP!

---

## Phase 5: User Story 3 - Complete Task Tool (Priority: P2)

**Goal**: Enable AI agents to mark tasks as completed (idempotent operation)

**Independent Test**: Create task with add_task → AI agent invokes complete_task with task_id → task.is_completed set to true → updated task returned

### Implementation for User Story 3

- [ ] T023 [P] [US3] Implement complete_task handler in mcp-server/src/tools/complete_task.py (JWT validation, task lookup with user_id check, set is_completed=true, refresh updated_at)
- [ ] T024 [US3] Register complete_task tool in mcp-server/src/server.py (add to list_tools handler, route in call_tool handler)
- [ ] T025 [US3] Add complete_task authorization check (task.user_id must match JWT user_id, return NOT_FOUND if mismatch)
- [ ] T026 [US3] Add complete_task idempotency logic (calling on already-completed task succeeds with no error)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work independently

---

## Phase 6: User Story 4 - Update Task Tool (Priority: P2)

**Goal**: Enable AI agents to modify task title, description, or completion status

**Independent Test**: Create task → AI agent invokes update_task with changes → only specified fields updated → updated_at timestamp refreshed

### Implementation for User Story 4

- [ ] T027 [P] [US4] Implement update_task handler in mcp-server/src/tools/update_task.py (JWT validation, task lookup, apply updates, validate title if provided)
- [ ] T028 [US4] Register update_task tool in mcp-server/src/server.py (add to list_tools handler, route in call_tool handler)
- [ ] T029 [US4] Add update_task partial update logic (only update provided fields, preserve others, refresh updated_at)
- [ ] T030 [US4] Add update_task authorization check (task.user_id must match JWT user_id)
- [ ] T031 [US4] Add update_task validation (if title provided, must be 1-255 chars and not empty)

**Checkpoint**: At this point, User Stories 1-4 work independently

---

## Phase 7: User Story 5 - Delete Task Tool (Priority: P3)

**Goal**: Enable AI agents to permanently remove tasks from database

**Independent Test**: Create task → AI agent invokes delete_task with task_id → task removed from database → success confirmation returned

### Implementation for User Story 5

- [ ] T032 [P] [US5] Implement delete_task handler in mcp-server/src/tools/delete_task.py (JWT validation, task lookup, DELETE operation, confirmation response)
- [ ] T033 [US5] Register delete_task tool in mcp-server/src/server.py (add to list_tools handler, route in call_tool handler)
- [ ] T034 [US5] Add delete_task authorization check (task.user_id must match JWT user_id)
- [ ] T035 [US5] Add delete_task response formatting ({"deleted": true, "task_id": "..."})

**Checkpoint**: All 5 user stories (tools) are now independently functional

---

## Phase 8: Integration & Testing

**Purpose**: Validate MCP server integration and tool behavior

- [ ] T036 Create MCP test client in mcp-server/tests/test_client.py (stdio client for manual testing)
- [ ] T037 [P] Write integration test for add_task in mcp-server/tests/integration/test_mcp_server.py (test tool invocation via MCP protocol)
- [ ] T038 [P] Write integration test for list_tasks in mcp-server/tests/integration/test_mcp_server.py (test filtering and pagination)
- [ ] T039 [P] Write integration test for complete_task in mcp-server/tests/integration/test_mcp_server.py (test idempotency)
- [ ] T040 [P] Write integration test for update_task in mcp-server/tests/integration/test_mcp_server.py (test partial updates)
- [ ] T041 [P] Write integration test for delete_task in mcp-server/tests/integration/test_mcp_server.py (test permanent deletion)
- [ ] T042 Test JWT authentication failures across all tools (invalid token, expired token, missing token)
- [ ] T043 Test user isolation across all tools (User A cannot access User B's tasks)
- [ ] T044 Run all integration tests and verify 100% pass rate

**Checkpoint**: All integration tests pass - MCP server is production-ready

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [ ] T045 [P] Add comprehensive docstrings to all tool handlers (mcp-server/src/tools/*.py)
- [ ] T046 [P] Add logging statements to server.py and tool handlers (INFO level for tool invocations, ERROR for failures)
- [ ] T047 [P] Create MCP server startup script in mcp-server/run.sh (activate venv, run server with proper error handling)
- [ ] T048 [P] Update mcp-server/README.md with usage examples, testing guide, troubleshooting section
- [ ] T049 Run performance benchmark (verify <500ms for list_tasks with 100 items, <50ms auth rejection)
- [ ] T050 Run security audit (verify JWT validation on every tool, user isolation enforced, no SQL injection)
- [ ] T051 Validate all tool schemas match contracts in specs/005-mcp-server-todo-tooling/contracts/*.json

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Integration (Phase 8)**: Depends on all desired user stories being complete
- **Polish (Phase 9)**: Depends on Integration completion

### User Story Dependencies

- **User Story 1 (add_task)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (list_tasks)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 3 (complete_task)**: Can start after Foundational (Phase 2) - No dependencies (uses Task model from backend)
- **User Story 4 (update_task)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 5 (delete_task)**: Can start after Foundational (Phase 2) - No dependencies

**Key Insight**: All 5 user stories (tools) are FULLY INDEPENDENT after Phase 2. They can be developed in parallel by different team members.

### Within Each User Story

- Implementation tasks can often be parallelized ([P] marker)
- Tool handler → Registration in server.py → Validation logic → Error handling (sequential within story)
- Different user stories don't block each other

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T004, T005, T006, T007)
- All Foundational tasks marked [P] can run in parallel (T009, T010, T011)
- Once Foundational phase completes, all 5 user stories can start in parallel
- Within Integration phase, all test-writing tasks [P] can run in parallel (T037-T041, T045-T048)

---

## Parallel Example: After Foundational Phase

```bash
# All 5 tools can be implemented simultaneously:

# Developer A: User Story 1
Task: "Implement add_task handler in mcp-server/src/tools/add_task.py"
Task: "Register add_task tool in mcp-server/src/server.py"

# Developer B: User Story 2
Task: "Implement list_tasks handler in mcp-server/src/tools/list_tasks.py"
Task: "Register list_tasks tool in mcp-server/src/server.py"

# Developer C: User Story 3
Task: "Implement complete_task handler in mcp-server/src/tools/complete_task.py"
Task: "Register complete_task tool in mcp-server/src/server.py"

# Developer D: User Story 4
Task: "Implement update_task handler in mcp-server/src/tools/update_task.py"

# Developer E: User Story 5
Task: "Implement delete_task handler in mcp-server/src/tools/delete_task.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (add_task)
4. Complete Phase 4: User Story 2 (list_tasks)
5. **STOP and VALIDATE**: Test both tools independently with MCP test client
6. Deploy/demo if ready (basic task creation + listing works!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (add_task) → Test independently → Demo (can create tasks!)
3. Add User Story 2 (list_tasks) → Test independently → Demo (MVP: create + list!)
4. Add User Story 3 (complete_task) → Test independently → Demo (can mark done!)
5. Add User Story 4 (update_task) → Test independently → Demo (can edit tasks!)
6. Add User Story 5 (delete_task) → Test independently → Demo (full CRUD complete!)
7. Each tool adds value without breaking previous tools

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (serial work, ~1-2 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (add_task) - Priority P1
   - Developer B: User Story 2 (list_tasks) - Priority P1
   - Developer C: User Story 3 (complete_task) - Priority P2
   - Developer D: User Story 4 (update_task) - Priority P2
   - Developer E: User Story 5 (delete_task) - Priority P3
3. Tools complete and integrate independently (no conflicts!)
4. Integration phase: Test all tools together

---

## Task Execution Guidelines

### For Each Task

1. **Read Contracts**: Check `specs/005-mcp-server-todo-tooling/contracts/<tool>.json` for schema
2. **Check Data Model**: Review `specs/005-mcp-server-todo-tooling/data-model.md` for patterns
3. **Follow Patterns**: Use research findings from `specs/005-mcp-server-todo-tooling/plan.md` Phase 0
4. **Write Tests First** (if TDD requested): Ensure test fails before implementation
5. **Implement**: Follow the exact file path in task description
6. **Validate**: Run tests, check against acceptance scenarios in spec.md
7. **Commit**: Create focused commit with task ID reference

### File Path Examples

- Tool handlers: `mcp-server/src/tools/add_task.py`
- Schemas: `mcp-server/src/schemas/tool_schemas.py`
- Server: `mcp-server/src/server.py`
- Auth: `mcp-server/src/auth/jwt_validator.py`
- Database: `mcp-server/src/db/session.py`
- Errors: `mcp-server/src/utils/errors.py`
- Tests: `mcp-server/tests/unit/test_add_task.py`
- Integration: `mcp-server/tests/integration/test_mcp_server.py`

### Testing Commands

```bash
# Run all tests
cd mcp-server && pytest

# Run specific test file
pytest tests/unit/test_add_task.py -v

# Run integration tests only
pytest tests/integration/ -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### MCP Server Commands

```bash
# Start server (stdio transport)
cd mcp-server && python src/server.py

# Test with client
python tests/test_client.py
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate tool independently
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence
- **No schema changes**: MCP server reuses existing Task/User models from backend
- **No backend changes**: All code goes in new mcp-server/ directory
- **Import shared code**: Import Task, User, auth_service, settings from backend/src/

---

## Summary

**Total Tasks**: 51 tasks
**MVP Scope**: Phases 1-4 (Tasks T001-T022) = 22 tasks for add_task + list_tasks tools
**Full Feature**: All phases = 51 tasks for complete MCP server with all 5 tools

**Task Distribution by User Story**:
- Setup (Phase 1): 7 tasks
- Foundational (Phase 2): 6 tasks (blocks all stories)
- User Story 1 (add_task - P1): 4 tasks 🎯 MVP
- User Story 2 (list_tasks - P1): 5 tasks 🎯 MVP
- User Story 3 (complete_task - P2): 4 tasks
- User Story 4 (update_task - P2): 5 tasks
- User Story 5 (delete_task - P2): 4 tasks
- Integration (Phase 8): 9 tasks
- Polish (Phase 9): 7 tasks

**Parallel Opportunities**:
- Phase 1: 4 tasks can run in parallel
- Phase 2: 3 tasks can run in parallel
- Phases 3-7: All 5 user stories can run in parallel after Phase 2
- Phase 8: 9 test tasks can run in parallel
- Phase 9: 6 polish tasks can run in parallel

**Critical Path**: Setup → Foundational → Pick any user story (all independent!) → Integration → Polish

**Estimated Timeline** (single developer):
- MVP (US1 + US2): 1-2 days
- Full Feature (all 5 tools): 3-4 days
- With team of 5: 1-2 days for full feature (parallel execution)
