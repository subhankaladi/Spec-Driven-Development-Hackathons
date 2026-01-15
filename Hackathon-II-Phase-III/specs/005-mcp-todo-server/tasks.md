---

description: "Task list for MCP Server & Todo Tooling feature"
---

# Tasks: MCP Server & Todo Tooling

**Input**: Design documents from `/specs/005-mcp-todo-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/mcp-tools.json, research.md

**Tests**: Tests are NOT included per specification - implementation first, tests optional

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- MCP server: `backend/src/mcp_server/`
- Tests: `backend/tests/mcp/`
- All paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in `backend/src/mcp_server/`
- [ ] T002 Initialize Python project with `pyproject.toml` or `requirements.txt`
- [ ] T003 [P] Add MCP SDK, SQLModel, asyncpg, PyJWT dependencies
- [ ] T004 [P] Configure linting (ruff) and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create database configuration in `backend/src/mcp_server/config.py`
- [x] T006 [P] Implement async database engine and session factory in `backend/src/mcp_server/database.py`
- [x] T007 [P] Implement JWT validation utility in `backend/src/mcp_server/auth.py`
- [x] T008 Create Task SQLModel entity in `backend/src/mcp_server/models/task.py`
- [x] T009 Create models `__init__.py` exporting Task
- [x] T010 Create MCP server initialization in `backend/src/mcp_server/server.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Tasks via MCP Tools (Priority: P1) MVP

**Goal**: Enable AI agents to add, list, update, and delete tasks through MCP tools

**Independent Test**: Invoke add_task, list_tasks, update_task, delete_task via MCP inspector and verify database state changes for the authenticated user

### Implementation for User Story 1

- [x] T011 [P] [US1] Implement `add_task` tool in `backend/src/mcp_server/tools/add_task.py`
- [x] T012 [P] [US1] Implement `list_tasks` tool in `backend/src/mcp_server/tools/list_tasks.py`
- [x] T013 [P] [US1] Implement `update_task` tool in `backend/src/mcp_server/tools/update_task.py`
- [x] T014 [P] [US1] Implement `delete_task` tool in `backend/src/mcp_server/tools/delete_task.py`
- [x] T015 [US1] Register all US1 tools in `backend/src/mcp_server/server.py` (depends on T011-T014)
- [x] T016 [US1] Add input validation for title length (max 255) and description (max 2000)
- [x] T017 [US1] Implement ownership enforcement: verify task.user_id == current_user_id on all operations

**Checkpoint**: User Story 1 complete - agents can manage tasks with full ownership isolation

---

## Phase 4: User Story 2 - Automated Task Completion (Priority: P2)

**Goal**: Enable AI agents to quickly mark tasks as complete through a dedicated MCP tool

**Independent Test**: Invoke complete_task with a specific ID and verify is_completed flag is true in the DB

### Implementation for User Story 2

- [x] T018 [P] [US2] Implement `complete_task` tool in `backend/src/mcp_server/tools/complete_task.py`
- [x] T019 [US2] Register complete_task tool in `backend/src/mcp_server/server.py` (depends on T018)
- [x] T020 [US2] Add ownership verification for complete_task (depends on T017)

**Checkpoint**: User Story 2 complete - all 5 MCP tools now available

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 [P] Add tool registration logging at server startup
- [ ] T022 Add standardized error response formatting across all tools
- [ ] T023 Create server main entry point in `backend/src/mcp_server/__main__.py`
- [ ] T024 [P] Add environment variable validation for required configs
- [ ] T025 Add .env.example documentation for required environment variables
- [ ] T026 Run quickstart.md validation steps manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 but benefits from the pattern established

### Within Each User Story

- Foundational must be complete first
- Models before tools
- Tools before registration
- Core implementation before ownership enforcement
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user story tools marked [P] can start in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tool implementations for User Story 1 together:
Task: "Implement add_task tool in backend/src/mcp_server/tools/add_task.py"
Task: "Implement list_tasks tool in backend/src/mcp_server/tools/list_tasks.py"
Task: "Implement update_task tool in backend/src/mcp_server/tools/update_task.py"
Task: "Implement delete_task tool in backend/src/mcp_server/tools/delete_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test add_task, list_tasks, update_task, delete_task independently
5. Demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (Core functionality!)
3. Add User Story 2 → Test independently → Demo (Complete toolset)
4. Polish phase

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 tools (add, list, update, delete)
   - Developer B: User Story 2 tool (complete)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
