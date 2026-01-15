# Frontend Routes Contract

## Public Routes (No Authentication Required)

### `/` - Landing/Home
**Purpose**: Welcome page for unauthenticated users
**Behavior**:
- If authenticated: Redirect to `/dashboard`
- If unauthenticated: Show welcome content with sign-in/sign-up links

### `/auth/signin` - Sign In Page
**Purpose**: User authentication
**Behavior**:
- If authenticated: Redirect to `/dashboard`
- If unauthenticated: Show sign-in form
**Form Fields**:
- email: string (required, email format)
- password: string (required, min 8 chars)
**Success**: Redirect to `/dashboard`
**Error**: Display error message, remain on page

### `/auth/signup` - Sign Up Page
**Purpose**: New user registration
**Behavior**:
- If authenticated: Redirect to `/dashboard`
- If unauthenticated: Show sign-up form
**Form Fields**:
- email: string (required, email format)
- password: string (required, min 8 chars)
- confirmPassword: string (required, must match password)
**Success**: Redirect to `/dashboard`
**Error**: Display error message, remain on page

---

## Protected Routes (Authentication Required)

### `/dashboard` - Task Dashboard
**Purpose**: Main task management interface
**Behavior**:
- If unauthenticated: Redirect to `/auth/signin`
- If authenticated: Show task list
**Features**:
- Task list with completion status
- Create task button
- Edit/delete task actions
- Completion toggle
- Filter by completion status
- Responsive layout

---

## Route Protection Middleware

### Middleware Behavior
**Path**: `/middleware.ts`
**Protected Paths**: `/dashboard`, `/dashboard/*`
**Public Paths**: `/`, `/auth/*`

**Logic**:
1. Check for valid session token
2. If protected route + no token → Redirect to `/auth/signin`
3. If auth route + valid token → Redirect to `/dashboard`
4. Otherwise → Continue to requested route

---

## Navigation Components

### Header Navigation (Authenticated)
- Logo/Brand → `/dashboard`
- Dashboard link → `/dashboard`
- Sign Out button → Clear session, redirect to `/`

### Header Navigation (Unauthenticated)
- Logo/Brand → `/`
- Sign In link → `/auth/signin`
- Sign Up link → `/auth/signup`

---

## URL Query Parameters

### `/dashboard`
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| filter | 'all' \| 'completed' \| 'incomplete' | 'all' | Filter tasks by status |

---

## Error Pages

### 404 - Not Found
**Path**: `/not-found`
**Content**: Friendly message with link back to dashboard/home

### Error Boundary
**Behavior**: Catch React errors, show recovery UI with retry option
