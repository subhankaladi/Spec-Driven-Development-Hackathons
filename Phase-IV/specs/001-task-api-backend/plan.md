# Implementation Plan: Task API Backend

**Branch**: `001-task-api-backend` | **Date**: 2026-01-07 | **Spec**: [spec.md](spec.md)

## Summary

This plan defines the backend architecture for a persistent task management API using FastAPI, SQLModel, and Neon Serverless PostgreSQL. The implementation provides RESTful CRUD operations for tasks with user-scoped data access. All endpoints are designed to integrate with future authentication (Spec-2) by requiring user_id in the API path.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, Uvicorn
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest (for verification)
**Target Platform**: Linux server (WSL compatible)
**Project Type**: Web backend API
**Performance Goals**: <2s response for CRUD operations, <1s for list queries
**Constraints**: User-scoped queries, JWT-ready design, no hard-coded secrets
**Scale/Scope**: Multi-user support, pagination (default 20, max 100)

## Constitution Check

*GATE: Must pass before proceeding with design*

- **Spec-Driven Development**: ✅ Spec created and approved
- **Agentic Workflow**: ✅ Will use Backend and Database agents
- **Security-First Design**: ✅ User isolation via user_id scoping
- **Deterministic Behavior**: ✅ API contracts defined with HTTP semantics
- **Full-Stack Coherence**: ✅ Frontend-ready API design
- **Traceability**: ✅ PHRs will be created for all implementation

**Result**: ✅ All gates pass - proceed to design

## Project Structure

### Documentation (this feature)

```text
specs/001-task-api-backend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (research findings)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (API specifications)
│   ├── task-operations.yaml
│   └── error-responses.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── database.py      # Database connection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── tasks.py     # Task CRUD endpoints
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── task.py      # Pydantic schemas
│   │       └── errors.py    # Error response schemas
│   ├── main.py              # FastAPI app entry
│   └── config.py            # Environment configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_crud.py         # CRUD operation tests
│   └── test_user_isolation.py
├── alembic/
│   └── versions/            # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

**Structure Decision**: Backend as standalone directory with clear separation of models, API routes, and schemas. This enables independent operation and future frontend integration.

---

## Phase 0: Research

### Research Findings

All technical decisions have been validated through research:

1. **SQLModel with Neon PostgreSQL**
   - Decision: Use SQLModel for unified SQL and Pydantic validation
   - Rationale: Native PostgreSQL support, type safety, migration compatibility
   - Alternative: Plain SQLAlchemy - rejected for added Pydantic integration

2. **FastAPI REST Patterns**
   - Decision: Follow standard REST conventions with dedicated error handlers
   - Rationale: Industry standard, automatic OpenAPI generation
   - Alternative: Custom routing - rejected for maintainability

3. **Error Handling Strategy**
   - Decision: Centralized exception handler with consistent error schemas
   - Rationale: Deterministic error responses, proper HTTP status codes
   - Alternative: Per-endpoint errors - rejected for consistency

4. **User Isolation via user_id**
   - Decision: Always filter queries by user_id column
   - Rationale: Prevents cross-user access, prepares for JWT auth
   - Alternative: Row-level security - rejected for portability

---

## Phase 1: Design & Contracts

### Database Schema

**Task Entity**
- `id`: UUID primary key (distributed uniqueness)
- `user_id`: UUID foreign key (user ownership)
- `title`: String(255), required, non-empty
- `description`: Text, nullable
- `is_completed`: Boolean, default False
- `created_at`: DateTime, auto-created
- `updated_at`: DateTime, auto-updated

**Indexes**: Primary key on id, foreign key on user_id, composite index on (user_id, created_at)

### API Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | /users/{user_id}/tasks | Create task | 201, 400, 404 |
| GET | /users/{user_id}/tasks | List tasks | 200, 404 |
| GET | /users/{user_id}/tasks/{task_id} | Get task | 200, 404 |
| PUT/PATCH | /users/{user_id}/tasks/{task_id} | Update task | 200, 400, 404 |
| DELETE | /users/{user_id}/tasks/{task_id} | Delete task | 204, 404 |

### Error Response Schema

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {} // Optional validation details
  }
}
```

---

## Complexity Tracking

No constitution violations require justification.

---

## Artifacts Generated

- `research.md` - Technical research findings
- `data-model.md` - Database schema documentation
- `contracts/task-operations.yaml` - OpenAPI specification
- `contracts/error-responses.yaml` - Error schemas
- `quickstart.md` - Development setup guide

**Status**: Ready for `/sp.tasks` to generate implementation tasks
