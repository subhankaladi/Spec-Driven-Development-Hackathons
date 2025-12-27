# Implementation Plan: REST API Completion & Ownership Enforcement

**Branch**: `003-api-ownership` | **Date**: 2025-12-22 | **Spec**: [specs/003-api-ownership/spec.md](specs/003-api-ownership/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement complete REST API behavior for the Todo application with ownership enforcement. This includes implementing all CRUD endpoints for tasks, task completion toggle functionality, and ensuring all operations are filtered by authenticated user identity. The implementation will follow security-first design principles with JWT authentication enforced on every endpoint and multi-user task isolation.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI, SQLModel, python-jose[cryptography], pydantic, uvicorn
**Storage**: SQLite for development (with Neon PostgreSQL capability)
**Testing**: pytest with TestClient for API testing
**Target Platform**: Linux server (cross-platform compatible)
**Project Type**: Web backend API
**Performance Goals**: <500ms p95 response time for 95% of requests
**Constraints**: <100MB memory usage, stateless authentication with JWT tokens, offline-capable during development
**Scale/Scope**: 10k users, 1M tasks, authenticated user isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Development: Complete specification exists at specs/003-api-ownership/spec.md
- ✅ Zero Manual Coding: Implementation will be achieved exclusively through Claude Code
- ✅ Security-First Design: JWT authentication enforced on every API route, multi-user task isolation
- ✅ Deterministic and Reproducible Outputs: Using established backend structure
- ✅ Full-Stack Architecture Standards: Using FastAPI + SQLModel as required
- ✅ End-to-End Agentic Workflow: Following spec → plan → tasks → implementation workflow

## Project Structure

### Documentation (this feature)

```text
specs/003-api-ownership/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── task.py              # Task entity model with owner_id
│   ├── auth/
│   │   ├── utils.py             # JWT utilities
│   │   ├── middleware.py        # Authentication middleware
│   │   └── dependencies.py      # Authentication dependencies
│   ├── api/
│   │   ├── main.py              # Main FastAPI application with JWT middleware
│   │   └── routes/
│   │       └── tasks.py         # Task CRUD endpoints with ownership enforcement
│   ├── database/
│   │   └── session.py           # Database session management
│   └── config/
│       └── settings.py          # Configuration with JWT settings
└── tests/
    ├── test_auth_utils.py       # JWT utilities tests
    ├── test_auth_middleware.py  # Middleware tests
    └── test_auth.py             # API authentication tests
```

**Structure Decision**: Single backend project following the established pattern from previous features. The structure leverages existing auth infrastructure while implementing complete REST endpoints with ownership enforcement.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Plan (Updated 2025-12-27)

### Phase 1: Enhance Existing Endpoints

Based on user request for remaining REST endpoints and standardized responses:

#### 1.1 Add PATCH Endpoint for Partial Updates
- **File**: `backend/src/api/routes/tasks.py`
- **Action**: Add `@router.patch("/tasks/{task_id}")` endpoint
- **Purpose**: Provide semantic partial updates, ideal for completion toggling
- **Contract**: See `contracts/tasks-api-contract.md`

#### 1.2 Add Query Parameter Filtering to GET /tasks
- **File**: `backend/src/api/routes/tasks.py`
- **Action**: Update `read_tasks()` to accept `is_completed`, `limit`, `offset` parameters
- **Purpose**: Enable filtering by completion status and pagination
- **Response**: Return paginated response with `items`, `total`, `limit`, `offset`

#### 1.3 Standardize Error Responses
- **File**: `backend/src/api/main.py`
- **Action**: Add exception handlers for consistent error format
- **Format**: `{"detail": <string>, "error_code": <string|null>, "timestamp": <ISO datetime>}`

### Phase 2: Response Schema Updates

#### 2.1 Add Response Models
- **File**: `backend/src/models/task.py`
- **Action**: Add `TaskListResponse` model for paginated responses
- **Fields**: `items: List[TaskRead]`, `total: int`, `limit: int`, `offset: int`

### Phase 3: Validation Against Acceptance Criteria

#### 3.1 User Story 1 Validation
- [ ] POST /tasks creates task with authenticated user as owner
- [ ] GET /tasks returns only user's own tasks
- [ ] GET /tasks/{id} retrieves single task with ownership check
- [ ] PUT /tasks/{id} updates only owned tasks
- [ ] DELETE /tasks/{id} deletes only owned tasks

#### 3.2 User Story 2 Validation
- [ ] PUT/PATCH updates is_completed field correctly
- [ ] Filter by ?is_completed=true/false works

#### 3.3 User Story 3 Validation
- [ ] GET /tasks/{id} returns 403/404 for other users' tasks
- [ ] PUT /tasks/{id} returns 403/404 for other users' tasks
- [ ] PATCH /tasks/{id} returns 403/404 for other users' tasks
- [ ] DELETE /tasks/{id} returns 403/404 for other users' tasks

## Dependencies

| Artifact | Status | Path |
|----------|--------|------|
| Feature Spec | ✅ Complete | `specs/003-api-ownership/spec.md` |
| Research | ✅ Complete | `specs/003-api-ownership/research.md` |
| Data Model | ✅ Complete | `specs/003-api-ownership/data-model.md` |
| API Contract | ✅ Complete | `specs/003-api-ownership/contracts/tasks-api-contract.md` |
| Quickstart | ✅ Complete | `specs/003-api-ownership/quickstart.md` |
| Tasks | ✅ Complete | `specs/003-api-ownership/tasks.md` |

## Next Steps

1. Run `/sp.tasks` to regenerate task breakdown with new PATCH endpoint requirements
2. Run `/sp.implement` to execute implementation
3. Validate against acceptance criteria in quickstart.md