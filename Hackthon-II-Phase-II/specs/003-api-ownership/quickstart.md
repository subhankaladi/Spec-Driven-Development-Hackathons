# Quickstart: REST API Completion & Ownership Enforcement

## Prerequisites
- Python 3.11+
- FastAPI and SQLModel dependencies
- JWT authentication system (already implemented)
- Database connection (SQLite/PostgreSQL)

## Setup

1. Ensure authentication system is active (JWT middleware in place)
2. Verify database connection and models are available
3. Confirm JWT secret and algorithm settings in environment

## API Usage

### Authentication
All API calls require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Creating a Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My new task",
    "description": "Task description",
    "is_completed": false
  }'
```

### Getting User's Tasks
```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Updating a Task (Full Update)
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "description": "Updated description",
    "is_completed": true
  }'
```

### Toggle Task Completion (Partial Update)
```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_completed": true
  }'
```

### Filter Tasks by Completion Status
```bash
curl -X GET "http://localhost:8000/api/v1/tasks?is_completed=false&limit=10" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Deleting a Task
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Testing
Run tests to verify API functionality:
```bash
cd backend
python -m pytest tests/test_auth.py
```

## Key Features
- Automatic task ownership assignment based on JWT user ID
- User-specific task filtering on all read operations
- Cross-user access prevention with 403/404 responses
- Consistent error handling across all endpoints
- Task completion toggle functionality via PUT or PATCH
- Pagination support with limit/offset parameters
- Filter tasks by completion status

## Acceptance Criteria Validation

### User Story 1: Create and Manage Personal Tasks
- [x] POST /tasks creates task with authenticated user as owner
- [x] GET /tasks returns only user's own tasks
- [x] PUT /tasks/{id} updates only owned tasks
- [x] DELETE /tasks/{id} deletes only owned tasks

### User Story 2: Toggle Task Completion Status
- [x] PUT/PATCH updates is_completed field
- [x] Filter by ?is_completed=true/false works

### User Story 3: Secure Cross-User Access Prevention
- [x] GET /tasks/{id} returns 403/404 for other users' tasks
- [x] PUT /tasks/{id} returns 403/404 for other users' tasks
- [x] DELETE /tasks/{id} returns 403/404 for other users' tasks