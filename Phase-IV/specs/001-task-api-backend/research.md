# Research: Task API Backend

## SQLModel with Neon Serverless PostgreSQL

**Decision**: Use SQLModel for unified SQL and Pydantic validation

**Rationale**:
- SQLModel combines SQLAlchemy and Pydantic into a single library
- Native PostgreSQL support with automatic type coercion
- Type safety from Pydantic models carries through to database operations
- Compatible with Alembic for database migrations
- Neon Serverless PostgreSQL supports standard PostgreSQL drivers

**Alternatives Considered**:
- Plain SQLAlchemy: Rejected - requires separate Pydantic models for validation
- Raw SQL with psycopg2: Rejected - no type safety, error-prone
- SQLAlchemy Core only: Rejected - missing Pydantic integration benefits

**Best Practices Applied**:
- Use `Field()` for column constraints
- Set `table=True` for ORM models
- Use `relationship()` for any future foreign key dependencies
- Enable connection pooling via environment variables

---

## FastAPI REST Patterns

**Decision**: Follow standard REST conventions with FastAPI

**Rationale**:
- Industry-standard REST API design patterns
- Automatic OpenAPI/Swagger documentation generation
- Native Pydantic integration for request/response validation
- Dependency injection for database sessions
- Built-in async support for better concurrency

**Endpoint Design**:
- Resource-based URLs: /users/{user_id}/tasks/{task_id}
- HTTP verbs: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- Standard status codes: 200, 201, 204, 400, 404, 500

**Best Practices Applied**:
- Use `APIRouter` for modular route organization
- Centralized exception handling with `@app.exception_handler`
- Request models separate from Response models
- Pagination via query parameters (page, page_size)

---

## Error Handling Strategy

**Decision**: Centralized exception handler with consistent error schemas

**Rationale**:
- Deterministic error responses across all endpoints
- Proper HTTP status codes for client vs server errors
- Structured error data for frontend consumption
- Easy to extend with new error types

**Error Taxonomy**:
| Code | HTTP Status | Condition |
|------|-------------|-----------|
| VALIDATION_ERROR | 400 | Invalid request data |
| NOT_FOUND | 404 | Resource does not exist |
| DATABASE_ERROR | 500 | Connection or query failure |
| INTERNAL_ERROR | 500 | Unexpected server error |

**Best Practices Applied**:
- Custom exception classes inheriting from FastAPI HTTPException
- Error details include field-specific messages for validation
- Logging of all 500-level errors for debugging

---

## User Isolation via user_id

**Decision**: Always filter queries by user_id column

**Rationale**:
- Simple and effective multi-user isolation
- Works seamlessly with future JWT authentication
- No risk of accidentally exposing other users' data
- Database-level enforcement via WHERE clauses

**Implementation Pattern**:
```python
# Always include user_id filter
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

**Security Considerations**:
- Never trust user_id from request body - only from path parameter
- Validate user_id format (UUID) before query execution
- Log any access attempts for audit trail

**Best Practices Applied**:
- Composite queries filter by (user_id, task_id) for single-task operations
- Soft delete pattern for recovery (optional)
- Index on user_id for query performance

---

## Pagination Strategy

**Decision**: Offset-based pagination with configurable limits

**Rationale**:
- Simple implementation and understanding
- Works with all database backends
- Predictable URL structure for caching

**Parameters**:
- `page`: 1-based page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Schema**:
```json
{
  "items": [...],
  "total": 123,
  "page": 1,
  "page_size": 20,
  "total_pages": 7
}
```

---

## Environment Configuration

**Decision**: Use environment variables for all secrets and connections

**Required Variables**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `API_HOST`: Host to bind (default: 0.0.0.0)
- `API_PORT`: Port to listen (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging verbosity (default: info)

**Best Practices Applied**:
- `.env.example` documents all required variables
- No hard-coded values in source code
- Type validation via Pydantic Settings
