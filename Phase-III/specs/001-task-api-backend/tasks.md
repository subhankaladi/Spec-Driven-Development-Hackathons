# Tasks: Task API Backend

**Input**: Design documents from `/specs/001-task-api-backend/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/task-operations.yaml, quickstart.md
**Status**: COMPLETED - All 54 tasks implemented and tested

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend source: `backend/src/`
- Backend tests: `backend/tests/`
- Configuration: `backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per implementation plan in backend/
- [X] T002 Create requirements.txt with FastAPI, SQLModel, Uvicorn, pytest, alembic
- [X] T003 Create .env.example with DATABASE_URL, API_HOST, API_PORT, DEBUG, LOG_LEVEL
- [X] T004 [P] Create backend/README.md with setup instructions from quickstart.md
- [X] T005 [P] Initialize Python virtual environment and install dependencies

**Checkpoint**: Project structure ready - foundational work can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create backend/src/config.py with Pydantic BaseSettings for environment variables
- [X] T007 [P] Create backend/src/models/__init__.py
- [X] T008 [P] Create backend/src/api/__init__.py
- [X] T009 [P] Create backend/src/api/routes/__init__.py
- [X] T010 [P] Create backend/src/api/schemas/__init__.py
- [X] T011 Create backend/src/models/database.py with SQLModel engine and session creation
- [X] T012 Create backend/src/models/task.py with Task SQLModel entity from data-model.md
- [X] T013 Create backend/src/api/schemas/errors.py with ErrorResponse and custom exceptions
- [X] T014 Create backend/src/api/schemas/task.py with TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
- [X] T015 Create backend/src/main.py with FastAPI app initialization and exception handlers
- [X] T016 Create alembic.ini and migrations environment for database versioning
- [X] T017 Create initial Alembic migration for task table in backend/alembic/versions/
- [X] T018 Run Alembic migration to create task table in Neon PostgreSQL

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Tasks (Priority: P1)

**Goal**: Users can create new tasks via POST /users/{user_id}/tasks

**Independent Test**: POST /users/{user_id}/tasks with valid data returns 201 and task is in database

### Implementation for User Story 1

- [X] T019 [P] [US1] Create backend/src/api/routes/tasks.py with TaskService class
- [X] T020 [US1] Implement create_task method in TaskService (user-scoped, validates title)
- [X] T021 [US1] Add POST /users/{user_id}/tasks endpoint in tasks.py router
- [X] T022 [US1] Add request validation using TaskCreate schema
- [X] T023 [US1] Add error handling for validation (400) and not found (404)
- [X] T024 [US1] Add response model TaskResponse with 201 status code

**Checkpoint**: User Story 1 complete - tasks can be created

---

## Phase 4: User Story 2 - Read Tasks (List) (Priority: P1)

**Goal**: Users can list all their tasks via GET /users/{user_id}/tasks with pagination

**Independent Test**: GET /users/{user_id}/tasks returns 200 with paginated task list

### Implementation for User Story 2

- [X] T025 [P] [US2] Implement get_tasks method in TaskService with pagination support
- [X] T026 [US2] Add GET /users/{user_id}/tasks endpoint in tasks.py router
- [X] T027 [US2] Add pagination query parameters (page, page_size) with defaults
- [X] T028 [US2] Add response model TaskListResponse with pagination metadata
- [X] T029 [US2] Add user-scoped query filtering by user_id
- [X] T030 [US2] Add error handling for invalid pagination params (400)

**Checkpoint**: User Story 2 complete - task lists can be retrieved

---

## Phase 5: User Story 3 - Read Single Task (Priority: P1)

**Goal**: Users can get a specific task via GET /users/{user_id}/tasks/{task_id}

**Independent Test**: GET /users/{user_id}/tasks/{task_id} returns 200 with task or 404 if not found/not owned

### Implementation for User Story 3

- [X] T031 [P] [US3] Implement get_task method in TaskService with user_id filter
- [X] T032 [US3] Add GET /users/{user_id}/tasks/{task_id} endpoint in tasks.py router
- [X] T033 [US3] Add path parameter validation for task_id (UUID format)
- [X] T034 [US3] Add 404 response when task_id not found or not owned by user
- [X] T035 [US3] Add response model TaskResponse

**Checkpoint**: User Story 3 complete - single tasks can be retrieved

---

## Phase 6: User Story 4 - Update Tasks (Priority: P1)

**Goal**: Users can update tasks via PUT/PATCH /users/{user_id}/tasks/{task_id}

**Independent Test**: PUT/PATCH /users/{user_id}/tasks/{task_id} returns 200 with updated task

### Implementation for User Story 4

- [X] T036 [P] [US4] Implement update_task method in TaskService with user_id filter
- [X] T037 [US4] Add PUT /users/{user_id}/tasks/{task_id} endpoint (full update)
- [X] T038 [US4] Add PATCH /users/{user_id}/tasks/{task_id} endpoint (partial update)
- [X] T039 [US4] Add request validation using TaskUpdate schema
- [X] T040 [US4] Add validation for empty title (400)
- [X] T041 [US4] Add 404 response when task not found or not owned
- [X] T042 [US4] Update updated_at timestamp on successful update

**Checkpoint**: User Story 4 complete - tasks can be updated

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P1)

**Goal**: Users can delete tasks via DELETE /users/{user_id}/tasks/{task_id}

**Independent Test**: DELETE /users/{user_id}/tasks/{task_id} returns 204 and task is removed

### Implementation for User Story 5

- [X] T043 [P] [US5] Implement delete_task method in TaskService with user_id filter
- [X] T044 [US5] Add DELETE /users/{user_id}/tasks/{task_id} endpoint
- [X] T045 [US5] Add 404 response when task not found or not owned
- [X] T046 [US5] Return 204 status code on successful deletion

**Checkpoint**: User Story 5 complete - tasks can be deleted

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T047 Create backend/tests/conftest.py with test fixtures and test database
- [X] T048 [P] Create backend/tests/__init__.py
- [X] T049 [P] Create backend/tests/test_crud.py with integration tests for all CRUD operations
- [X] T050 [P] Create backend/tests/test_user_isolation.py to verify cross-user access is blocked
- [X] T051 Run all tests and verify 100% pass rate
- [X] T052 Update backend/README.md with API documentation links
- [X] T053 Verify backend runs independently per quickstart.md
- [X] T054 Validate API contracts match contracts/task-operations.yaml specification

**Checkpoint**: All user stories complete and tested

---

## Test Results Summary

```
======================= 15 passed, 25 warnings in 15.50s =======================
```

**Test Coverage**:
- CRUD operations: 9 tests
- User isolation: 4 tests
- Pagination: 2 tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Completed
- **Foundational (Phase 2)**: Completed - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All completed
- **Polish (Phase 8)**: Completed

### User Story Dependencies

All user stories are now complete and independently testable.

---

## Implementation Complete

All 54 tasks have been implemented and verified:
- Backend API with FastAPI and SQLModel
- Database schema with Neon PostgreSQL
- User isolation via user_id scoping
- Comprehensive test suite (15 tests, 100% pass rate)
- API documentation ready at /docs
