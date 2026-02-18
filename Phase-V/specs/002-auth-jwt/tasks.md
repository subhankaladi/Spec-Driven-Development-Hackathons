# Tasks: Authentication & Security

**Input**: Design documents from `/specs/002-auth-jwt/`
**Prerequisites**: plan.md (required), spec.md (required)
**Status**: READY - 40 tasks across 7 phases
**Feature Branch**: `002-auth-jwt`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend source: `backend/src/`
- Backend tests: `backend/tests/`
- Frontend source: `frontend/src/`
- Configuration: `backend/`

---

## Phase 1: Setup & Configuration

**Purpose**: Environment configuration and project updates

- [ ] T001 Create `backend/src/core/__init__.py` directory package
- [ ] T002 [P] Update `backend/src/config.py` with JWT settings (SECRET, ALGORITHM, EXPIRATION_HOURS)
- [ ] T003 [P] Update `backend/requirements.txt` with `bcrypt==4.1.2`, `pyjwt==2.9.0`, `python-jose==3.3.0`
- [ ] T004 Create `.env.example` with JWT_SECRET example and documentation

**Checkpoint**: Dependencies installed and configured

---

## Phase 2: Database Foundation

**Purpose**: User entity and database setup - BLOCKS all auth user stories

**CRITICAL**: No auth user story work can begin until this phase is complete

- [ ] T005 [P] Create `backend/src/models/user.py` with User SQLModel entity (id, email, password_hash, created_at, updated_at)
- [ ] T006 Update `backend/src/models/__init__.py` to export User model
- [ ] T007 Create Alembic migration for users table in `backend/alembic/versions/`
- [ ] T008 Run Alembic migration to create users table in Neon PostgreSQL
- [ ] T009 Add email unique constraint index in migration

**Checkpoint**: Users table exists in database

---

## Phase 3: Auth Utilities (Foundation)

**Purpose**: Core authentication functions - BLOCKS auth endpoints

**CRITICAL**: No auth endpoint work can begin until this phase is complete

- [ ] T010 [P] Create `backend/src/core/auth.py` with password hashing functions (bcrypt)
- [ ] T011 [P] Create `backend/src/core/auth.py` with JWT token creation function
- [ ] T012 [P] Create `backend/src/core/auth.py` with JWT token verification function
- [ ] T013 Create `backend/src/core/auth.py` with token decode helper (without verification for debugging)
- [ ] T014 Write unit tests for password hashing/verification in `backend/tests/test_auth_password.py`
- [ ] T015 Write unit tests for JWT creation/verification in `backend/tests/test_auth_jwt.py`

**Checkpoint**: Auth utilities verified and tested

---

## Phase 4: Auth Endpoints

**Purpose**: Sign up and sign in API endpoints

- [ ] T016 [P] Create `backend/src/api/routes/auth.py` router
- [ ] T017 [US1] Create POST `/auth/signup` endpoint with email/password validation
- [ ] T018 [US1] Implement email uniqueness check before user creation
- [ ] T019 [US1] Hash password before storing in database
- [ ] T020 [US1] Return 201 with user profile (no password) and JWT token on success
- [ ] T021 [US1] Return 400 for invalid email format
- [ ] T022 [US1] Return 400 for weak password (less than 8 characters)
- [ ] T023 [US1] Return 409 for duplicate email

- [ ] T024 [US2] Create POST `/auth/signin` endpoint with email/password validation
- [ ] T025 [US2] Verify credentials and return 200 with JWT token
- [ ] T026 [US2] Return 401 for invalid credentials (generic message)
- [ ] T027 [US2] Add timing-safe password comparison to prevent timing attacks

- [ ] T028 Create auth response schemas in `backend/src/api/schemas/auth.py` (TokenResponse, UserResponse)
- [ ] T029 Add auth router to `backend/src/main.py`

**Checkpoint**: Sign up and sign in endpoints working

---

## Phase 5: JWT Authentication Middleware

**Purpose**: FastAPI dependency for protecting endpoints

- [ ] T030 Create `backend/src/api/dependencies/auth.py` with `get_current_user` dependency
- [ ] T031 Implement Authorization header extraction (Bearer token)
- [ ] T032 Implement JWT verification in dependency
- [ ] T033 Return 401 with UNAUTHORIZED code for missing header
- [ ] T034 Return 401 for invalid token signature
- [ ] T035 Return 401 for expired token
- [ ] T036 Create `User` Pydantic schema from JWT claims for endpoint use

**Checkpoint**: All endpoints can be protected with auth dependency

---

## Phase 6: Protect Task Endpoints

**Purpose**: Update existing task endpoints to require authentication

- [ ] T037 Update `backend/src/api/routes/tasks.py` to use `get_current_user` dependency
- [ ] T038 [US3] Add auth dependency to GET `/users/{user_id}/tasks`
- [ ] T039 [US3] Add auth dependency to POST `/users/{user_id}/tasks`
- [ ] T040 [US3] Add auth dependency to GET `/users/{user_id}/tasks/{task_id}`
- [ ] T041 [US3] Add auth dependency to PUT `/users/{user_id}/tasks/{task_id}`
- [ ] T042 [US3] Add auth dependency to DELETE `/users/{user_id}/tasks/{task_id}`

- [ ] T043 [US4] Implement user_id validation (JWT user_id == URL user_id)
- [ ] T044 [US4] Return 403 or 404 when user attempts to access other user's tasks
- [ ] T045 [US4] Update all task service methods to use authenticated user_id from JWT

**Checkpoint**: All task endpoints require authentication

---

## Phase 7: Testing & Polish

**Purpose**: Comprehensive testing of auth flow

- [ ] T046 Update `backend/tests/conftest.py` with auth fixtures (test user, valid token, expired token)
- [ ] T047 [US1] Write integration tests for signup in `backend/tests/test_auth_signup.py`
- [ ] T048 [US2] Write integration tests for signin in `backend/tests/test_auth_signin.py`
- [ ] T049 [US3] Write integration tests for token validation in `backend/tests/test_auth_middleware.py`
- [ ] T050 [US4] Write integration tests for protected endpoints in `backend/tests/test_auth_protected.py`
- [ ] T051 Update `backend/tests/test_user_isolation.py` to use authentication
- [ ] T052 Update `backend/tests/test_crud.py` to use authentication
- [ ] T053 Run all tests and verify 100% pass rate

- [ ] T054 Update `backend/README.md` with authentication documentation
- [ ] T055 Add rate limiting documentation (from plan.md)

**Checkpoint**: All tests passing, auth ready for frontend integration

---

## Test Results Summary

**Test Coverage Targets:**
- Auth utilities: 10 tests
- Sign up flow: 5 tests
- Sign in flow: 5 tests
- Token validation: 5 tests
- Protected endpoints: 5 tests
- User isolation with auth: 5 tests
- **Total: ~35 tests**

**Existing Tests to Update:**
- `test_crud.py`: 11 tests → add auth headers
- `test_user_isolation.py`: 4 tests → add auth headers

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Blocks | Blocked By |
|-------|--------|------------|
| Phase 1 (Setup) | 2, 3 | - |
| Phase 2 (Database) | 3, 4, 5, 6 | Phase 1 |
| Phase 3 (Utilities) | 4, 5 | Phase 2 |
| Phase 4 (Endpoints) | 5 | Phase 3 |
| Phase 5 (Middleware) | 6 | Phase 4 |
| Phase 6 (Protect) | 7 | Phase 5 |
| Phase 7 (Testing) | - | Phase 6 |

### Parallel Execution

Tasks marked `[P]` can run in parallel:
- T001, T002, T003, T004 (Phase 1)
- T005, T006 (Phase 2)
- T010, T011, T012 (Phase 3)
- T016, T028 (Phase 4)
- T030, T036 (Phase 5)
- T038, T039, T040, T041, T042 (Phase 6)
- T047, T048, T049, T050, T051, T052 (Phase 7)

---

## Implementation Complete

All 55 tasks complete when:
- Sign up returns 201 with user + token
- Sign in returns 200 with token
- All endpoints require JWT authentication
- Cross-user access returns 401/403
- All existing tests pass with auth headers
- New auth tests have 100% pass rate
