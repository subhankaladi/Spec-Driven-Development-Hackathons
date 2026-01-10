# Todo API Backend

A FastAPI-based REST API for managing todo tasks with JWT authentication and user-based task isolation.

## Features

- JWT-based authentication on all endpoints
- User-specific task ownership and isolation
- Complete CRUD operations for tasks
- Task completion toggle functionality
- Pagination and filtering support
- Standardized error responses

## API Endpoints

All endpoints require JWT authentication via Bearer token:
```
Authorization: Bearer <JWT_TOKEN>
```

### Tasks API (`/api/v1`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /tasks | Create a new task |
| GET | /tasks | Get all tasks (with pagination/filtering) |
| GET | /tasks/{id} | Get a specific task |
| PUT | /tasks/{id} | Update a task (full update) |
| PATCH | /tasks/{id} | Partially update a task |
| DELETE | /tasks/{id} | Delete a task |

### Query Parameters (GET /tasks)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| is_completed | boolean | null | Filter by completion status |
| limit | integer | 100 | Max tasks to return (1-500) |
| offset | integer | 0 | Number of tasks to skip |

### Response Formats

**Task Object:**
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "is_completed": false,
  "owner_id": "user123",
  "created_at": "2025-12-27T18:00:00Z",
  "updated_at": "2025-12-27T18:00:00Z"
}
```

**Task List Response:**
```json
{
  "items": [...],
  "total": 25,
  "limit": 100,
  "offset": 0
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-12-27T18:00:00Z"
}
```

## Security

- All endpoints require valid JWT authentication
- Users can only access their own tasks
- Cross-user access attempts return 403 Forbidden
- Invalid/expired tokens return 401 Unauthorized

## Running the API

```bash
cd backend
uvicorn src.api.main:app --reload
```

## Running Tests

```bash
cd backend
python -m pytest tests/
```
