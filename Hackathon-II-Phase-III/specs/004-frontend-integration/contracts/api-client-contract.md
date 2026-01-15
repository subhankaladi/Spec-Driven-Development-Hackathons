# API Client Contract

## Overview

The API client provides a secure, centralized interface for all backend communication. Every request MUST include valid JWT authentication.

## Base Configuration

```typescript
interface ApiClientConfig {
  baseUrl: string;           // Backend API URL (from env)
  tokenKey: string;          // localStorage key for JWT
  timeout: number;           // Request timeout in ms (default: 10000)
}
```

## Core Methods

### `apiClient.get<T>(endpoint: string, options?: RequestOptions): Promise<T>`
**Purpose**: Fetch data from backend
**Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
**Returns**: Parsed JSON response
**Throws**: ApiError on failure

### `apiClient.post<T>(endpoint: string, data: unknown, options?: RequestOptions): Promise<T>`
**Purpose**: Create resource on backend
**Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
**Body**: JSON stringified data
**Returns**: Parsed JSON response
**Throws**: ApiError on failure

### `apiClient.put<T>(endpoint: string, data: unknown, options?: RequestOptions): Promise<T>`
**Purpose**: Full update of resource
**Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
**Body**: JSON stringified data
**Returns**: Parsed JSON response
**Throws**: ApiError on failure

### `apiClient.patch<T>(endpoint: string, data: unknown, options?: RequestOptions): Promise<T>`
**Purpose**: Partial update of resource
**Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
**Body**: JSON stringified data
**Returns**: Parsed JSON response
**Throws**: ApiError on failure

### `apiClient.delete(endpoint: string, options?: RequestOptions): Promise<void>`
**Purpose**: Delete resource
**Headers**: `Authorization: Bearer <token>`
**Returns**: void (204 No Content expected)
**Throws**: ApiError on failure

---

## Error Handling

### ApiError Class
```typescript
class ApiError extends Error {
  status: number;          // HTTP status code
  errorCode: string | null; // Backend error code
  timestamp: string;       // Error timestamp
  canRetry: boolean;       // Whether retry makes sense
}
```

### Error Code Mapping
| Backend Code | HTTP Status | User Message | Can Retry |
|--------------|-------------|--------------|-----------|
| AUTH_001 | 401 | "Please sign in to continue" | No |
| AUTH_002 | 403 | "You don't have access to this resource" | No |
| NOT_FOUND | 404 | "The requested item was not found" | No |
| VALIDATION_ERROR | 422 | "Please check your input" | No |
| BAD_REQUEST | 400 | "Invalid request" | No |
| SERVER_ERROR | 500 | "Something went wrong. Please try again." | Yes |
| (network) | - | "Network error. Check your connection." | Yes |

### Auto-Logout on 401
When receiving 401 Unauthorized:
1. Clear stored token
2. Update auth context to unauthenticated
3. Redirect to `/auth/signin`
4. Show "Session expired" message

---

## Task API Methods

### `getTasks(params?: TaskQueryParams): Promise<TaskListResponse>`
**Endpoint**: GET `/api/v1/tasks`
**Query Params**:
- `is_completed`: boolean (optional)
- `limit`: number (default 100, max 500)
- `offset`: number (default 0)
**Response**: `{ items: Task[], total: number, limit: number, offset: number }`

### `getTask(id: number): Promise<Task>`
**Endpoint**: GET `/api/v1/tasks/{id}`
**Response**: Single Task object
**Errors**: 404 if not found, 403 if not owner

### `createTask(data: TaskCreateData): Promise<Task>`
**Endpoint**: POST `/api/v1/tasks`
**Body**: `{ title: string, description?: string, is_completed?: boolean }`
**Response**: Created Task object

### `updateTask(id: number, data: TaskUpdateData): Promise<Task>`
**Endpoint**: PUT `/api/v1/tasks/{id}`
**Body**: `{ title?: string, description?: string, is_completed?: boolean }`
**Response**: Updated Task object
**Errors**: 404 if not found, 403 if not owner

### `patchTask(id: number, data: Partial<TaskUpdateData>): Promise<Task>`
**Endpoint**: PATCH `/api/v1/tasks/{id}`
**Body**: Partial task fields
**Response**: Updated Task object
**Errors**: 404 if not found, 403 if not owner

### `deleteTask(id: number): Promise<void>`
**Endpoint**: DELETE `/api/v1/tasks/{id}`
**Response**: 204 No Content
**Errors**: 404 if not found, 403 if not owner

---

## Request/Response Types

```typescript
interface TaskQueryParams {
  is_completed?: boolean;
  limit?: number;
  offset?: number;
}

interface TaskListResponse {
  items: Task[];
  total: number;
  limit: number;
  offset: number;
}

interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

interface TaskCreateData {
  title: string;
  description?: string;
  is_completed?: boolean;
}

interface TaskUpdateData {
  title?: string;
  description?: string;
  is_completed?: boolean;
}
```

---

## Security Requirements

1. **Token Attachment**: Every request MUST include `Authorization: Bearer <token>`
2. **No Token = No Request**: API client MUST throw error if no token available
3. **Token Validation**: Check token expiry before requests, refresh if needed
4. **Secure Storage**: Token stored in localStorage only
5. **HTTPS Only**: All requests must use HTTPS in production
