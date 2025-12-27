# API Contract: Task Management Endpoints

## Base URL
`/api/v1`

## Authentication
All endpoints require JWT authentication in the Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

## Common Response Format

### Success Responses
```json
{
  "id": <integer>,
  "title": <string>,
  "description": <string>,
  "is_completed": <boolean>,
  "owner_id": <string>,
  "created_at": <ISO datetime>,
  "updated_at": <ISO datetime>
}
```

### Error Responses
```json
{
  "detail": <string>,
  "error_code": <string>
}
```

## Endpoints

### POST /tasks
**Description:** Create a new task for the authenticated user

**Request:**
```json
{
  "title": "Task title (required, 1-255 chars)",
  "description": "Optional description (max 1000 chars)",
  "is_completed": false
}
```

**Response:**
- 201 Created: Task created successfully
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 422 Validation Error: Data validation failed

### GET /tasks
**Description:** Get all tasks for the authenticated user with optional filtering and pagination

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| is_completed | boolean | No | null | Filter by completion status |
| limit | integer | No | 100 | Maximum tasks to return (1-500) |
| offset | integer | No | 0 | Number of tasks to skip |

**Response:**
- 200 OK: Paginated list of tasks belonging to the authenticated user
```json
{
  "items": [
    {
      "id": 1,
      "title": "Sample task",
      "description": "Sample description",
      "is_completed": false,
      "owner_id": "user123",
      "created_at": "2025-12-22T18:00:00Z",
      "updated_at": "2025-12-22T18:00:00Z"
    }
  ],
  "total": 25,
  "limit": 100,
  "offset": 0
}
```
- 401 Unauthorized: Invalid or missing JWT token

### GET /tasks/{id}
**Description:** Get a specific task by ID (must belong to authenticated user)

**Response:**
- 200 OK: Task data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist

### PUT /tasks/{id}
**Description:** Update a specific task by ID (must belong to authenticated user)

**Request:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "is_completed": true
}
```

**Response:**
- 200 OK: Updated task data
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist
- 422 Validation Error: Data validation failed

### PATCH /tasks/{id}
**Description:** Partially update a task (ideal for toggling completion status)

**Request:**
```json
{
  "is_completed": true
}
```
*Note: All fields are optional. Only provided fields will be updated.*

**Response:**
- 200 OK: Updated task data
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist
- 422 Validation Error: Data validation failed

### DELETE /tasks/{id}
**Description:** Delete a specific task by ID (must belong to authenticated user)

**Response:**
- 204 No Content: Task deleted successfully
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist

## Security Requirements

- All endpoints require valid JWT authentication
- Users can only access tasks with matching owner_id
- Unauthorized access attempts return 403 or 404
- Token expiration results in 401 responses
- Invalid tokens result in 401 responses