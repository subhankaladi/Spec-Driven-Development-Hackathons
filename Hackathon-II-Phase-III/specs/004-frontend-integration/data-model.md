# Data Model: Frontend Web Application & Integration

## Client-Side Entities

### User Session
**Purpose**: Represents the authenticated user's state on the frontend

**Fields:**
- `userId`: string - Unique identifier from JWT token 'sub' claim
- `email`: string - User's email address (from token or API)
- `isAuthenticated`: boolean - Whether user has valid session
- `token`: string - JWT token for API requests (stored in localStorage)

**State Transitions:**
- Initial: `isAuthenticated = false`, no token
- After sign-in: `isAuthenticated = true`, token stored
- After sign-out: `isAuthenticated = false`, token cleared
- Token expired: Auto-transition to `isAuthenticated = false`

### Task (Frontend Representation)
**Purpose**: Client-side representation of a task for display and manipulation

**Fields:**
- `id`: number - Unique task identifier from backend
- `title`: string - Task title (required, 1-255 chars)
- `description`: string | null - Optional task description (max 1000 chars)
- `isCompleted`: boolean - Completion status
- `ownerId`: string - User ID who owns this task
- `createdAt`: string (ISO date) - Creation timestamp
- `updatedAt`: string (ISO date) - Last update timestamp

**UI States:**
- `isLoading`: boolean - Task operation in progress
- `error`: string | null - Error message if operation failed

### Task Form Data
**Purpose**: Data structure for task creation and editing

**Fields:**
- `title`: string - Required, validated for non-empty
- `description`: string - Optional
- `isCompleted`: boolean - Default false for new tasks

**Validation Rules:**
- Title: Required, 1-255 characters, no whitespace-only
- Description: Optional, max 1000 characters

## Frontend State Structure

### Auth Context State
```typescript
interface AuthState {
  user: {
    userId: string;
    email: string;
  } | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

### Tasks Context State
```typescript
interface TasksState {
  items: Task[];
  total: number;
  isLoading: boolean;
  error: string | null;
  filter: {
    isCompleted: boolean | null;
  };
  pagination: {
    limit: number;
    offset: number;
  };
}
```

### UI Component States

**Loading State:**
- Displayed during async operations
- Button disabled, spinner visible
- Form inputs disabled

**Error State:**
- Displayed when operation fails
- User-friendly message shown
- Retry option available

**Empty State:**
- Displayed when task list is empty
- Call-to-action to create first task
- Encouraging message

**Success State:**
- Brief confirmation after successful operations
- Auto-dismiss after 2-3 seconds

## Data Flow

### Sign-Up Flow
1. User enters email + password
2. Submit to Better Auth sign-up endpoint
3. Receive JWT token on success
4. Store token in localStorage
5. Update auth context state
6. Redirect to dashboard

### Sign-In Flow
1. User enters credentials
2. Submit to Better Auth sign-in endpoint
3. Receive JWT token on success
4. Store token in localStorage
5. Update auth context state
6. Redirect to dashboard

### Task List Flow
1. Dashboard mounts
2. Check auth state
3. Fetch tasks from /api/v1/tasks
4. Update tasks context
5. Render task list

### Task Create Flow
1. User clicks "Create Task"
2. Form modal opens
3. User enters title + description
4. Submit to POST /api/v1/tasks
5. On success: Add task to list, close modal
6. On error: Show error message

### Task Update Flow
1. User clicks edit on task
2. Form pre-filled with current values
3. User modifies fields
4. Submit to PUT /api/v1/tasks/{id}
5. On success: Update task in list
6. On error: Show error, revert UI

### Task Complete Toggle Flow
1. User clicks checkbox
2. Optimistic UI update
3. Submit to PATCH /api/v1/tasks/{id}
4. On success: Confirm state
5. On error: Revert UI, show error

### Task Delete Flow
1. User clicks delete
2. Confirmation modal appears
3. User confirms
4. Submit to DELETE /api/v1/tasks/{id}
5. On success: Remove from list
6. On error: Show error, task remains

## API Response Mapping

### Backend Response → Frontend State

```typescript
// Backend TaskListResponse
{
  items: TaskRead[],
  total: number,
  limit: number,
  offset: number
}

// Maps to TasksState
{
  items: items.map(mapTaskFromBackend),
  total: total,
  pagination: { limit, offset }
}
```

### Error Response Handling

```typescript
// Backend ErrorResponse
{
  detail: string,
  error_code: string | null,
  timestamp: string
}

// Maps to UI error message
{
  message: translateErrorCode(error_code) || detail,
  canRetry: isRetryableError(error_code)
}
```
