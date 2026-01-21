# Frontend Data Model

**Feature**: Frontend & Integration (003-frontend)
**Date**: 2026-01-07
**Purpose**: Define data structures for frontend state and API communication

## Overview

This document describes the data models used in the frontend application. All models are aligned with the backend API contracts from Spec-1 and Spec-2.

## Authentication Data Models

### User Profile

Represents the authenticated user's information.

```typescript
interface User {
  id: string;           // UUID from JWT sub claim
  email: string;        // User's email address
  token: string;        // JWT authentication token
}
```

**Source**: Decoded from JWT token + localStorage
**Validation**:
- Email format validated on sign-up
- Token validated via backend API calls
- ID extracted from JWT payload

### Auth State

Represents the global authentication state in React Context.

```typescript
interface AuthState {
  user: User | null;           // Current authenticated user (null = not logged in)
  loading: boolean;            // Auth check in progress
  error: string | null;        // Last auth error message
  isAuthenticated: boolean;    // Computed: user !== null
}

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  refreshAuth: () => Promise<void>;
}
```

**State Transitions**:
```
[Initial] → loading=true → [Authenticated] (user set)
                         → [Unauthenticated] (user=null)
```

## Task Data Models

### Task

Represents a single task item.

```typescript
interface Task {
  id: string;                // UUID
  title: string;             // Task title (required, 1-255 chars)
  description: string | null;// Task description (optional, plain text)
  is_completed: boolean;     // Completion status
  created_at: string;        // ISO 8601 timestamp
  updated_at: string;        // ISO 8601 timestamp
}
```

**Validation Rules**:
- `title`: Required, 1-255 characters, trimmed, no whitespace-only
- `description`: Optional, plain text only, no HTML
- `is_completed`: Boolean, toggled by user

### TaskListResponse

Represents paginated task list response from API.

```typescript
interface TaskListResponse {
  items: Task[];              // Array of tasks (paginated)
  total: number;              // Total number of tasks (across all pages)
  page: number;               // Current page number (1-based)
  page_size: number;          // Items per page (default 20)
  total_pages: number;        // Total number of pages
}
```

**Pagination Logic**:
- Frontend sends `page` and `page_size` query params
- Backend returns paginated results
- Frontend displays pagination controls

### TaskCreateRequest

Request to create a new task.

```typescript
interface TaskCreateRequest {
  title: string;
  description?: string;       // Optional
}
```

**Validation**:
- `title`: Required, 1-255 chars
- `description`: Optional, plain text

### TaskUpdateRequest

Request to update a task (partial).

```typescript
interface TaskUpdateRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
}
```

**Validation**:
- At least one field must be provided
- If `title` provided, must be 1-255 chars
- Cannot clear `title` (empty strings rejected by backend)

## API Error Models

### ErrorResponse

Standard error response from backend.

```typescript
interface ErrorResponse {
  error: {
    code: string;              // Error code (UNAUTHORIZED, INVALID_CREDENTIALS, etc.)
    message: string;           // User-friendly error message
    details: Record<string, any> | null;  // Additional error details
  };
}
```

**Common Error Codes**:
- `UNAUTHORIZED`: Missing/invalid JWT token
- `TOKEN_EXPIRED`: JWT token has expired
- `INVALID_CREDENTIALS`: Wrong email/password
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `EMAIL_EXISTS`: Email already registered
- `FORBIDDEN`: Access to other user's data denied

## Form State Models

### SignInFormState

State for sign-in form.

```typescript
interface SignInFormState {
  email: string;
  password: string;
  errors: {
    email?: string;
    password?: string;
    general?: string;
  };
  touched: {
    email: boolean;
    password: boolean;
  };
  isSubmitting: boolean;
}
```

### SignUpFormState

State for sign-up form.

```typescript
interface SignUpFormState {
  email: string;
  password: string;
  confirmPassword: string;
  errors: {
    email?: string;
    password?: string;
    confirmPassword?: string;
    general?: string;
  };
  touched: {
    email: boolean;
    password: boolean;
    confirmPassword: boolean;
  };
  isSubmitting: boolean;
}
```

### TaskFormState

State for task create/edit form.

```typescript
interface TaskFormState {
  title: string;
  description: string;
  errors: {
    title?: string;
    description?: string;
    general?: string;
  };
  touched: {
    title: boolean;
    description: boolean;
  };
  isSubmitting: boolean;
}
```

## Loading State Models

### LoadingState

Generic loading state for async operations.

```typescript
type LoadingState = 'idle' | 'loading' | 'success' | 'error';

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}
```

**Usage**:
```typescript
const taskListState: AsyncState<Task[]> = {
  data: [],
  loading: false,
  error: null,
};
```

## UI State Models

### PaginationState

State for task list pagination.

```typescript
interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  canGoBack: boolean;
  canGoForward: boolean;
}
```

### ModalState

State for modal dialogs.

```typescript
interface ModalState {
  isOpen: boolean;
  title?: string;
  content?: React.ReactNode;
  onConfirm?: () => void;
  onCancel?: () => void;
}
```

**Usage**:
```typescript
const deleteModalState: ModalState = {
  isOpen: true,
  title: 'Delete Task?',
  content: 'Are you sure you want to delete this task?',
  onConfirm: handleDelete,
  onCancel: closeModal,
};
```

## Data Flow Diagrams

### Authentication Flow

```
User → SignInForm → signIn() → API POST /auth/signin
                           ↓
                        { token, user }
                           ↓
                   AuthContext.setState()
                           ↓
                   localStorage.setItem('token')
                           ↓
                   Redirect to /tasks
```

### Task List Flow

```
Page Load → useTasks() → API GET /users/{user_id}/tasks
                             ↓
                         { items, pagination }
                             ↓
                     TaskList.render()
                             ↓
                      TaskCard[] mapped
```

### Create Task Flow

```
User → TaskForm → validate → API POST /users/{user_id}/tasks
                        ↓
                     { task }
                        ↓
                Router.push('/tasks')
                        ↓
                  useTasks().refetch()
```

## Type Safety

All models are defined in TypeScript with proper typing:

```typescript
// src/types/auth.ts
export type { User, AuthState, AuthContextType };

// src/types/tasks.ts
export type { Task, TaskListResponse, TaskCreateRequest, TaskUpdateRequest };

// src/types/api.ts
export type { ErrorResponse };

// src/types/ui.ts
export type { LoadingState, AsyncState, PaginationState, ModalState };
```

## Validation Functions

```typescript
// src/lib/utils/validation.ts

export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function validatePassword(password: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }
  return {
    valid: errors.length === 0,
    errors,
  };
}

export function validateTaskTitle(title: string): boolean {
  return title.trim().length > 0 && title.trim().length <= 255;
}
```
