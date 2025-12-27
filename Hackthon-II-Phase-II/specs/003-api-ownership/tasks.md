---
description: "Task list for REST API Completion & Ownership Enforcement implementation"
---

# Tasks: REST API Completion & Ownership Enforcement

**Input**: Design documents from `/specs/003-api-ownership/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - included only where explicitly beneficial for validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow the established project structure

## Current Implementation Status

The following endpoints already exist and are functional:
- POST /tasks - Creates task with owner_id ✅
- GET /tasks - Returns user's tasks (needs pagination/filtering)
- GET /tasks/{id} - Returns single task with ownership check ✅
- PUT /tasks/{id} - Updates task with ownership check ✅
- DELETE /tasks/{id} - Deletes task with ownership check ✅

**Missing/Enhancement items:**
- PATCH /tasks/{id} - Needs to be added
- GET /tasks pagination - Needs query parameters (is_completed, limit, offset)
- TaskListResponse model - Needs to be added for paginated responses
- Standardized error responses - Needs exception handlers

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure and add missing dependencies

- [x] T001 Verify existing project structure matches plan.md in backend/
- [x] T002 [P] Verify requirements.txt includes all needed dependencies for API enhancements
- [x] T003 [P] Verify JWT authentication middleware is properly configured in backend/src/auth/middleware.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story enhancements

**Status**: Most foundational work already complete from previous features

- [x] T004 Add TaskListResponse model for paginated responses in backend/src/models/task.py
- [x] T005 [P] Add ErrorResponse model for standardized errors in backend/src/models/task.py
- [x] T006 Add global exception handlers for consistent error format in backend/src/api/main.py

**Checkpoint**: Foundation ready - user story enhancement implementation can now begin

---

## Phase 3: User Story 1 - Create and Manage Personal Tasks (Priority: P1)

**Goal**: Enhance CRUD operations with pagination, filtering, and PATCH endpoint

**Independent Test**: Can be fully tested by making authenticated API requests to all CRUD endpoints with valid JWT tokens and verifying that only the user's own tasks are accessible, modifiable, and deletable.

### Implementation for User Story 1

- [x] T007 [US1] Add PATCH /tasks/{id} endpoint for partial updates in backend/src/api/routes/tasks.py
- [x] T008 [US1] Update GET /tasks to accept is_completed query parameter in backend/src/api/routes/tasks.py
- [x] T009 [US1] Update GET /tasks to accept limit and offset query parameters in backend/src/api/routes/tasks.py
- [x] T010 [US1] Update GET /tasks to return TaskListResponse with items, total, limit, offset in backend/src/api/routes/tasks.py
- [x] T011 [US1] Add input validation for query parameters (limit 1-500, offset >= 0) in backend/src/api/routes/tasks.py

**Checkpoint**: At this point, User Story 1 enhancements should be fully functional

---

## Phase 4: User Story 2 - Toggle Task Completion Status (Priority: P1)

**Goal**: Ensure task completion toggle works via both PUT and PATCH endpoints

**Independent Test**: Can be fully tested by creating tasks, toggling their completion status via PUT/PATCH /api/v1/tasks/{id}, and verifying the status updates correctly.

### Implementation for User Story 2

- [x] T012 [US2] Verify PUT /tasks/{id} properly handles is_completed field updates in backend/src/api/routes/tasks.py
- [x] T013 [US2] Verify PATCH /tasks/{id} properly handles is_completed field updates in backend/src/api/routes/tasks.py
- [x] T014 [US2] Verify filter by ?is_completed=true/false works correctly in backend/src/api/routes/tasks.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Secure Cross-User Access Prevention (Priority: P1)

**Goal**: Verify all endpoints enforce ownership and return appropriate error codes

**Independent Test**: Can be fully tested by attempting to access another user's data with a valid JWT token from a different user account and verifying that access is denied with 403/404.

### Implementation for User Story 3

- [x] T015 [US3] Verify GET /tasks/{id} returns 403/404 for other users' tasks in backend/src/api/routes/tasks.py
- [x] T016 [US3] Verify PUT /tasks/{id} returns 403/404 for other users' tasks in backend/src/api/routes/tasks.py
- [x] T017 [US3] Verify PATCH /tasks/{id} returns 403/404 for other users' tasks in backend/src/api/routes/tasks.py
- [x] T018 [US3] Verify DELETE /tasks/{id} returns 403/404 for other users' tasks in backend/src/api/routes/tasks.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T019 [P] Update API documentation to reflect all endpoints in backend/README.md
- [x] T020 Add comprehensive error handling for edge cases in backend/src/api/routes/tasks.py
- [x] T021 [P] Add logging for security-related events in backend/src/api/routes/tasks.py
- [x] T022 Security hardening review of all endpoints
- [x] T023 Run quickstart.md validation for API ownership features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user story enhancements
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - Can proceed in parallel (if staffed)
  - Or sequentially in priority order (all P1)
- **Polish (Phase 6)**: Depends on all user story phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on PATCH endpoint from US1
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Verifies all endpoints including US1/US2

### Within Each User Story

- Models before endpoints
- Core implementation before validation
- Story complete before moving to verification

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T004 and T005 can run in parallel (same file but different models)
- T019 and T021 can run in parallel (different files)
- User stories can be worked on in parallel after Foundational phase

---

## Parallel Example: Foundational Phase

```bash
# Launch these tasks together:
Task: "Add TaskListResponse model for paginated responses in backend/src/models/task.py"
Task: "Add ErrorResponse model for standardized errors in backend/src/models/task.py"

# Then launch:
Task: "Add global exception handlers for consistent error format in backend/src/api/main.py"
```

---

## Implementation Strategy

### MVP Enhancement (User Story 1 Focus)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundational models and handlers
3. Complete Phase 3: User Story 1 (PATCH + pagination)
4. **STOP and VALIDATE**: Test PATCH and pagination independently
5. Continue to US2 and US3

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add PATCH endpoint -> Test independently
3. Add pagination/filtering -> Test independently
4. Verify completion toggle -> Test independently
5. Verify security (US3) -> Test independently
6. Polish phase -> Final validation

---

## Task Summary

| Phase | Task Count | Key Deliverables |
|-------|------------|------------------|
| Setup | 3 | Verification tasks |
| Foundational | 3 | TaskListResponse, ErrorResponse, Exception handlers |
| User Story 1 | 5 | PATCH endpoint, pagination, filtering |
| User Story 2 | 3 | Completion toggle verification |
| User Story 3 | 4 | Security enforcement verification |
| Polish | 5 | Documentation, logging, hardening |

**Total Tasks**: 23
**Parallel Opportunities**: 8 tasks marked [P]
**MVP Scope**: Phases 1-3 (11 tasks)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing implementation provides solid foundation - enhancements build on it
