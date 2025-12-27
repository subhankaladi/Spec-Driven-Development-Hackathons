# OpenAPI Contract: Task Management API

**Feature**: 001-backend-foundation
**Date**: 2025-12-22
**Version**: 1.0.0

## API Overview

This document describes the REST API for managing todo tasks. The API follows RESTful principles and returns JSON responses.

## Base URL
`http://localhost:8000` (development)
`https://api.example.com` (production)

## Common Headers
- `Content-Type: application/json`
- `Accept: application/json`

## Data Types

### Task Object
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "is_completed": false,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Endpoints

### Create Task
- **Method**: `POST`
- **Path**: `/tasks`
- **Description**: Creates a new task
- **Request Body**:
  ```json
  {
    "title": "Task title",
    "description": "Task description"
  }
  ```
- **Success Response**: `201 Created`
  - Body: Task object with assigned ID
- **Error Responses**:
  - `400 Bad Request`: Invalid input data
  - `500 Internal Server Error`: Server error

### Get All Tasks
- **Method**: `GET`
- **Path**: `/tasks`
- **Description**: Retrieves all tasks
- **Success Response**: `200 OK`
  - Body: Array of Task objects
- **Error Responses**:
  - `500 Internal Server Error`: Server error

### Get Task by ID
- **Method**: `GET`
- **Path**: `/tasks/{id}`
- **Description**: Retrieves a specific task by ID
- **Path Parameters**:
  - `id`: Task ID (integer)
- **Success Response**: `200 OK`
  - Body: Task object
- **Error Responses**:
  - `404 Not Found`: Task not found
  - `500 Internal Server Error`: Server error

### Update Task
- **Method**: `PUT`
- **Path**: `/tasks/{id}`
- **Description**: Updates an existing task
- **Path Parameters**:
  - `id`: Task ID (integer)
- **Request Body**:
  ```json
  {
    "title": "Updated title",
    "description": "Updated description",
    "is_completed": true
  }
  ```
- **Success Response**: `200 OK`
  - Body: Updated Task object
- **Error Responses**:
  - `404 Not Found`: Task not found
  - `400 Bad Request`: Invalid input data
  - `500 Internal Server Error`: Server error

### Delete Task
- **Method**: `DELETE`
- **Path**: `/tasks/{id}`
- **Description**: Deletes a specific task
- **Path Parameters**:
  - `id`: Task ID (integer)
- **Success Response**: `204 No Content`
- **Error Responses**:
  - `404 Not Found`: Task not found
  - `500 Internal Server Error`: Server error