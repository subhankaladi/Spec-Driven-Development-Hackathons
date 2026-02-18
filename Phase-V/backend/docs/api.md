# API Documentation: Advanced Task Management Features

## Overview
This document provides comprehensive API documentation for the advanced task management features including recurring tasks, due dates & reminders, task prioritization & tagging, advanced search/filter/sort, and event-driven architecture with Kafka and Dapr.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Common Headers
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

## Common Response Format
```json
{
  "data": { ... },
  "message": "Success message",
  "timestamp": "2026-02-15T10:30:00Z"
}
```

## Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": { ... }
  },
  "timestamp": "2026-02-15T10:30:00Z"
}
```

## Task Management Endpoints

### Create Task with Advanced Features
- **Endpoint**: `POST /users/{user_id}/tasks`
- **Description**: Create a new task with optional advanced features
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Request Body**:
```json
{
  "title": "Task title",
  "description": "Task description",
  "due_date": "2026-02-20T10:00:00Z",
  "priority": "high",
  "tags": ["work", "important"],
  "parent_template_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
- **Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Task title",
  "description": "Task description",
  "is_completed": false,
  "due_date": "2026-02-20T10:00:00Z",
  "priority": "high",
  "parent_template_id": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["work", "important"],
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Update Task with Advanced Features
- **Endpoint**: `PUT /users/{user_id}/tasks/{task_id}`
- **Description**: Update an existing task with advanced features
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `task_id` (UUID): Task ID to update
- **Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "is_completed": true,
  "due_date": "2026-02-25T15:00:00Z",
  "priority": "medium",
  "tags": ["work", "completed"]
}
```
- **Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated task title",
  "description": "Updated task description",
  "is_completed": true,
  "due_date": "2026-02-25T15:00:00Z",
  "priority": "medium",
  "parent_template_id": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["work", "completed"],
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T11:00:00Z"
}
```

### Get Task with Advanced Features
- **Endpoint**: `GET /users/{user_id}/tasks/{task_id}`
- **Description**: Get a specific task with all advanced features
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `task_id` (UUID): Task ID to retrieve
- **Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Task title",
  "description": "Task description",
  "is_completed": false,
  "due_date": "2026-02-20T10:00:00Z",
  "priority": "high",
  "parent_template_id": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["work", "important"],
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### List Tasks with Advanced Filters
- **Endpoint**: `GET /users/{user_id}/tasks`
- **Description**: Get all tasks for a user with optional filters, sorting, and pagination
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Query Parameters**:
  - `skip` (integer, default=0): Number of items to skip
  - `limit` (integer, default=20, max=100): Number of items to return
  - `priority` (string): Filter by priority (low, medium, high)
  - `due_after` (string): Filter tasks with due date after this date (ISO 8601)
  - `due_before` (string): Filter tasks with due date before this date (ISO 8601)
  - `completed` (boolean): Filter by completion status
  - `sort_by` (string, default="created_at"): Field to sort by (created_at, due_date, priority, title)
  - `sort_order` (string, default="desc"): Sort order (asc, desc)
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Task title",
      "description": "Task description",
      "is_completed": false,
      "due_date": "2026-02-20T10:00:00Z",
      "priority": "high",
      "parent_template_id": "550e8400-e29b-41d4-a716-446655440000",
      "tags": ["work", "important"],
      "created_at": "2026-02-15T10:30:00Z",
      "updated_at": "2026-02-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

## Recurring Task Template Endpoints

### Create Recurring Task Template
- **Endpoint**: `POST /users/{user_id}/recurring-tasks`
- **Description**: Create a new recurring task template
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Request Body**:
```json
{
  "title": "Weekly team meeting",
  "description": "Team sync meeting every Monday",
  "priority": "high",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO"],
    "until": "2026-12-31T23:59:59Z"
  },
  "start_date": "2026-02-16T09:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 50
}
```
- **Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Weekly team meeting",
  "description": "Team sync meeting every Monday",
  "priority": "high",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO"],
    "until": "2026-12-31T23:59:59Z"
  },
  "start_date": "2026-02-16T09:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 50,
  "is_active": true,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Get Recurring Task Template
- **Endpoint**: `GET /users/{user_id}/recurring-tasks/{template_id}`
- **Description**: Get a specific recurring task template
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `template_id` (UUID): Template ID to retrieve
- **Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Weekly team meeting",
  "description": "Team sync meeting every Monday",
  "priority": "high",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO"],
    "until": "2026-12-31T23:59:59Z"
  },
  "start_date": "2026-02-16T09:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 50,
  "is_active": true,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Update Recurring Task Template
- **Endpoint**: `PUT /users/{user_id}/recurring-tasks/{template_id}`
- **Description**: Update a recurring task template
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `template_id` (UUID): Template ID to update
- **Request Body**:
```json
{
  "title": "Updated weekly team meeting",
  "description": "Updated team sync meeting every Monday",
  "priority": "medium",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO", "FR"],
    "until": "2026-12-31T23:59:59Z"
  },
  "start_date": "2026-02-16T09:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 60,
  "is_active": true
}
```
- **Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated weekly team meeting",
  "description": "Updated team sync meeting every Monday",
  "priority": "medium",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO", "FR"],
    "until": "2026-12-31T23:59:59Z"
  },
  "start_date": "2026-02-16T09:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 60,
  "is_active": true,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T11:00:00Z"
}
```

### Delete Recurring Task Template
- **Endpoint**: `DELETE /users/{user_id}/recurring-tasks/{template_id}`
- **Description**: Delete a recurring task template
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `template_id` (UUID): Template ID to delete
- **Response**: `204 No Content`

## Reminder Endpoints

### Create Reminder
- **Endpoint**: `POST /users/{user_id}/reminders`
- **Description**: Create a new reminder for a task
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Request Body**:
```json
{
  "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
  "reminder_time": "2026-02-16T08:00:00Z",
  "method": "email"
}
```
- **Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "reminder_time": "2026-02-16T08:00:00Z",
  "method": "email",
  "is_sent": false,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Get User Reminders
- **Endpoint**: `GET /users/{user_id}/reminders`
- **Description**: Get all reminders for a user
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Query Parameters**:
  - `skip` (integer, default=0): Number of items to skip
  - `limit` (integer, default=20, max=100): Number of items to return
  - `task_instance_id` (UUID): Filter by specific task
  - `is_sent` (boolean): Filter by sent status
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "reminder_time": "2026-02-16T08:00:00Z",
      "method": "email",
      "is_sent": false,
      "created_at": "2026-02-15T10:30:00Z",
      "updated_at": "2026-02-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

## Tag Management Endpoints

### Create Tag
- **Endpoint**: `POST /users/{user_id}/tags`
- **Description**: Create a new tag for a user
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Request Body**:
```json
{
  "name": "work",
  "color": "#FF5733"
}
```
- **Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "work",
  "color": "#FF5733",
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Add Tag to Task
- **Endpoint**: `POST /users/{user_id}/tasks/{task_id}/tags/{tag_id}`
- **Description**: Associate a tag with a task
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `task_id` (UUID): Task ID to tag
  - `tag_id` (UUID): Tag ID to add
- **Response**: `204 No Content`

### Remove Tag from Task
- **Endpoint**: `DELETE /users/{user_id}/tasks/{task_id}/tags/{tag_id}`
- **Description**: Remove a tag association from a task
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
  - `task_id` (UUID): Task ID
  - `tag_id` (UUID): Tag ID to remove
- **Response**: `204 No Content`

## Advanced Search Endpoints

### Search Tasks
- **Endpoint**: `POST /users/{user_id}/tasks/search`
- **Description**: Search tasks with advanced filters, sorting, and pagination
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Request Body**:
```json
{
  "filters": {
    "priority": ["high", "medium"],
    "due_before": "2026-02-28T23:59:59Z",
    "tags": ["work", "urgent"],
    "completed": false,
    "title_contains": "meeting"
  },
  "sort_by": "due_date",
  "sort_order": "asc",
  "page": 1,
  "page_size": 20
}
```
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Team meeting",
      "description": "Weekly team sync",
      "is_completed": false,
      "due_date": "2026-02-16T09:00:00Z",
      "priority": "high",
      "parent_template_id": "550e8400-e29b-41d4-a716-446655440002",
      "tags": ["work", "meeting", "urgent"],
      "created_at": "2026-02-15T10:30:00Z",
      "updated_at": "2026-02-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

## Event Log Endpoints

### Get User Event Logs
- **Endpoint**: `GET /users/{user_id}/event-logs`
- **Description**: Get event logs for a user with optional filters
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Path Parameters**:
  - `user_id` (UUID): User ID (must match authenticated user)
- **Query Parameters**:
  - `skip` (integer, default=0): Number of items to skip
  - `limit` (integer, default=20, max=100): Number of items to return
  - `event_type` (string): Filter by event type
  - `task_instance_id` (UUID): Filter by specific task
  - `after` (string): Filter events after this date (ISO 8601)
  - `before` (string): Filter events before this date (ISO 8601)
  - `processed_by_kafka` (boolean): Filter by Kafka processing status
- **Response**: `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_instance_id": "550e8400-e29b-41d4-a716-446655440001",
      "event_type": "task.created",
      "payload": {
        "task_title": "Team meeting",
        "due_date": "2026-02-16T09:00:00Z"
      },
      "processed_by_kafka": true,
      "created_at": "2026-02-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `TASK_NOT_FOUND` | Task does not exist or does not belong to user |
| `RECURRING_TEMPLATE_NOT_FOUND` | Recurring task template does not exist or does not belong to user |
| `REMINDER_NOT_FOUND` | Reminder does not exist or does not belong to user |
| `TAG_NOT_FOUND` | Tag does not exist or does not belong to user |
| `INVALID_RECURRENCE_PATTERN` | Recurrence pattern is invalid |
| `REMINDER_TIME_AFTER_DUE_DATE` | Reminder time is after task's due date |
| `UNAUTHORIZED` | User is not authorized to access this resource |
| `VALIDATION_ERROR` | Request data validation failed |
| `INTERNAL_ERROR` | An unexpected error occurred |

## Rate Limits

- API requests are limited to 100 requests per minute per IP
- Exceeding the limit results in a 429 Too Many Requests response

## Versioning

This API uses URI versioning. All endpoints are under `/api/v1/`.