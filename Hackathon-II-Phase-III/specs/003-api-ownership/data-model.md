# Data Model: REST API Completion & Ownership Enforcement

## Task Entity

**Fields:**
- `id`: Integer (Primary Key, Auto-generated)
- `title`: String (Required, 1-255 characters)
- `description`: String (Optional, max 1000 characters)
- `is_completed`: Boolean (Default: false)
- `owner_id`: String (Required, links to authenticated user)
- `created_at`: DateTime (Auto-generated)
- `updated_at`: DateTime (Auto-generated, updates on modification)

**Validation Rules:**
- Title must be 1-255 characters
- Description max 1000 characters
- owner_id must match authenticated user ID for operations
- created_at and updated_at are automatically managed

**Relationships:**
- One User (authenticated user) to Many Tasks (via owner_id)

## User Identity

**Source:** JWT token 'sub' claim
**Format:** String identifier
**Validation:** Must exist in token and match owner_id for access

## State Transitions

**Task Completion:**
- Initial state: is_completed = false
- Transition: PUT/PATCH request changes is_completed to true/false
- Validation: Only task owner can change completion status

## Access Control Rules

- Read operations: Only tasks with owner_id matching authenticated user ID
- Write operations: Only tasks with owner_id matching authenticated user ID
- Delete operations: Only tasks with owner_id matching authenticated user ID
- Unauthorized access attempts return 403 or 404

## Query Parameters (GET /tasks)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| is_completed | boolean | null | Filter by completion status |
| limit | integer | 100 | Maximum number of tasks to return |
| offset | integer | 0 | Number of tasks to skip |

## Response Schemas

### TaskResponse (Single Task)
```json
{
  "id": <integer>,
  "title": <string>,
  "description": <string|null>,
  "is_completed": <boolean>,
  "owner_id": <string>,
  "created_at": <ISO datetime>,
  "updated_at": <ISO datetime>
}
```

### TaskListResponse (Multiple Tasks)
```json
{
  "items": [TaskResponse, ...],
  "total": <integer>,
  "limit": <integer>,
  "offset": <integer>
}
```

### ErrorResponse
```json
{
  "detail": <string>,
  "error_code": <string|null>,
  "timestamp": <ISO datetime>
}
```

## HTTP Status Codes

| Code | Description | Use Case |
|------|-------------|----------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid JWT |
| 403 | Forbidden | Cross-user access attempt |
| 404 | Not Found | Task does not exist |
| 422 | Validation Error | Schema validation failed |
| 500 | Server Error | Unexpected server error |