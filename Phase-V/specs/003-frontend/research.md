# Frontend & Integration Research

**Feature**: Frontend & Integration (003-frontend)
**Date**: 2026-01-07
**Purpose**: Document architecture decisions and resolve technical unknowns for implementation

## Overview

This document captures research findings and architectural decisions for the frontend implementation. All decisions align with the project constitution and technology constraints.

## Architecture Decisions

### AD-001: JWT Token Storage Strategy

**Decision**: Use **localStorage** with refresh mechanism

**Rationale**:
- Simpler implementation than HttpOnly cookies for this hackathon scope
- Allows easy access for API client interceptors
- Consistent with many modern web applications
- No additional server-side cookie configuration needed
- Token expiration can be handled gracefully in frontend

**Trade-offs**:
- Pros: Easy to implement, no server changes required, explicit control
- Cons: Vulnerable to XSS (mitigated by React's auto-escaping), not shared across tabs

**Alternatives Considered**:
1. **HttpOnly cookies** - More secure but requires backend configuration changes (Set-Cookie headers)
2. **sessionStorage** - Lost when tab closes, not suitable for persistent auth
3. **Memory only** - Lost on page refresh, poor UX

**Mitigation Strategy**:
- Implement XSS protections via React auto-escaping
- Clear tokens on logout
- Implement token expiration handling with refresh capability (future enhancement)

---

### AD-002: API Client Architecture

**Decision**: **Axios instance with request/response interceptors**

**Rationale**:
- Automatic JWT header injection via interceptors
- Centralized error handling
- Request/response transformation
- Request cancellation support
- Better TypeScript integration than fetch

**Implementation Pattern**:
```typescript
// lib/api/client.ts
- Create singleton Axios instance
- Request interceptor: Add Authorization header if token exists
- Response interceptor: Handle 401 errors, redirect to login
- Error interceptor: Extract error details from backend responses
```

**Trade-offs**:
- Pros: Centralized auth logic, automatic token management, clean error handling
- Cons: Additional library dependency (lightweight - 14KB minified)

**Alternatives Considered**:
1. **Fetch API** - Native but requires manual token handling and more boilerplate
2. **Apollo Client** - Overkill for REST API (better for GraphQL)

---

### AD-003: Route Protection Strategy

**Decision**: **Middleware + Client-side hooks**

**Rationale**:
- Next.js 14+ App Router middleware for route-level protection
- React Context + custom hooks for component-level auth state
- Automatic redirect for unauthenticated users
- Prevents loading protected pages without auth

**Implementation Pattern**:
```typescript
// middleware.ts
- Check protected routes (/tasks/*)
- Verify JWT token exists and is valid
- Redirect to /signin if not authenticated

// lib/hooks/useAuth.ts
- React Context for auth state (user, token, loading)
- signIn, signOut functions
- ProtectedRoute component wrapper
```

**Trade-offs**:
- Pros: Server-side protection + client-side state, automatic redirects
- Cons: Slight complexity with two protection layers

**Alternatives Considered**:
1. **Middleware only** - Doesn't provide client-side state for UI
2. **Client-side only** - Vulnerable to SSR issues, less secure

---

### AD-004: State Management Strategy

**Decision**: **React Context + Custom Hooks** (for auth), **Local State** (for forms/tasks)

**Rationale**:
- Auth state is global, needs Context
- Task state can be fetched per page (simpler, easier to cache)
- No additional libraries needed for this scope
- Aligns with "Smallest viable change" principle

**Implementation Pattern**:
```typescript
// src/context/AuthContext.tsx
- Global auth state (user, token, loading)
- signIn, signOut, checkAuth functions

// src/lib/hooks/useTasks.ts
- Fetch tasks for current page
- Optimistic updates for task completion
- Refetch on mutations
```

**Trade-offs**:
- Pros: Simple, minimal dependencies, good for this scope
- Cons: Not optimized for complex state (not needed here)

**Alternatives Considered**:
1. **Zustand** - Lightweight but adds dependency for simple needs
2. **Redux Toolkit** - Overkill for single-user task app

---

### AD-005: Form Validation Strategy

**Decision**: **Controlled components + custom validation logic**

**Rationale**:
- Full control over validation timing
- Easy to test
- Consistent with React patterns
- No external dependencies

**Implementation Pattern**:
```typescript
// lib/utils/validation.ts
- validateEmail(email): boolean
- validatePassword(password): { valid: boolean, errors: string[] }
- validateTaskTitle(title): boolean

// Component state
- errors: Record<string, string>
- handleChange: Validate on blur or change
- handleSubmit: Validate all before submit
```

**Trade-offs**:
- Pros: Explicit control, easy to customize, no library overhead
- Cons: More manual validation code than form libraries

**Alternatives Considered**:
1. **React Hook Form** - Reduces boilerplate but adds 11KB dependency
2. **Zod + React Hook Form** - Powerful but overkill for simple forms
3. **Yup + Formik** - Popular but heavier weight

---

### AD-006: Loading and Error State Patterns

**Decision**: **Suspense + Error Boundaries + Conditional Rendering**

**Rationale**:
- React Suspense for async data loading (future-ready with Next.js)
- Error Boundaries for graceful error handling
- Conditional rendering for loading/error/empty states
- Consistent with React best practices

**Implementation Pattern**:
```typescript
// Components
<LoadingState /> - Spinner or skeleton
<ErrorState error={error} /> - User-friendly message + retry
<EmptyState /> - Helpful message + CTA

// Data fetching
const { data, loading, error } = useTasks()
if (loading) return <LoadingState />
if (error) return <ErrorState error={error} />
if (data.length === 0) return <EmptyState />
return <TaskList tasks={data} />
```

**Trade-offs**:
- Pros: Simple, explicit, easy to understand
- Cons: More boilerplate than some solutions

**Alternatives Considered**:
1. **React Query (TanStack Query)** - Powerful but adds 13KB dependency
2. **SWR** - Lightweight but adds dependency
3. **Custom hooks** - Current choice, no dependency overhead

---

## Integration with Backend

### Backend API Contracts

The frontend must integrate with existing backend endpoints from Spec-1 and Spec-2:

**Authentication Endpoints** (Spec-2):
- `POST /auth/signup` - Create account
- `POST /auth/signin` - Authenticate and get JWT

**Task Endpoints** (Spec-1) - All require JWT header:
- `GET /users/{user_id}/tasks` - List tasks (paginated)
- `POST /users/{user_id}/tasks` - Create task
- `GET /users/{user_id}/tasks/{task_id}` - Get task details
- `PUT /users/{user_id}/tasks/{task_id}` - Update task
- `PATCH /users/{user_id}/tasks/{task_id}` - Partial update
- `DELETE /users/{user_id}/tasks/{task_id}` - Delete task

### API Error Responses

Backend returns errors in format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly message",
    "details": {...}
  }
}
```

Frontend must:
- Extract error details for display
- Handle 401 by redirecting to login
- Handle 403 by showing "forbidden" message
- Handle 404 by showing "not found" message
- Handle 422/400 by showing validation errors

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290,
  "iss": "todo-app"
}
```

Frontend must:
- Decode JWT to extract user_id and email
- Store token in localStorage
- Include in Authorization header: `Bearer {token}`
- Handle expiration (redirect to login)

---

## Responsive Design Strategy

### Breakpoints

- **Mobile**: 320px - 640px
- **Tablet**: 641px - 1024px
- **Desktop**: 1025px+

### Layout Adaptations

**Task List**:
- Mobile: Single column, stacked cards
- Tablet: Single column, wider cards
- Desktop: Grid layout (2-3 columns) or single column with wider width

**Navigation**:
- Mobile: Bottom tab bar or hamburger menu
- Tablet/Desktop: Top navigation bar

**Forms**:
- All sizes: Full-width inputs on mobile, constrained width on larger screens

### Tailwind CSS Configuration

```typescript
// tailwind.config.ts
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
    },
  },
}
```

---

## Performance Considerations

### API Optimization

- Use pagination to limit data transfer (20 items/page)
- Implement optimistic UI updates for task completion
- Cache API responses where appropriate (simple in-memory cache)

### Rendering Optimization

- React.memo for expensive components
- Virtualization for long lists (if needed for 100+ tasks)
- Lazy loading for non-critical components

### Bundle Size

- Code splitting with Next.js dynamic imports
- Tree shaking for unused code
- Target bundle size: <200KB gzipped

---

## Security Considerations

### XSS Protection

- React auto-escapes HTML (built-in XSS protection)
- Avoid dangerouslySetInnerHTML (not needed for this app)
- Sanitize user input before rendering (if using rich text in future)

### CSRF Protection

- Backend uses JWT (stateless) - CSRF not a concern
- No session cookies to protect

### Token Security

- Never log tokens in console
- Clear tokens on logout
- Implement token expiration handling
- Use HTTPS in production (enforced by backend)

---

## Testing Strategy

### Unit Tests

- Test validation functions
- Test API client interceptors
- Test React hooks with @testing-library/react-hooks

### Integration Tests

- Test auth flow (signup, signin, signout)
- Test task CRUD operations
- Test error handling
- Test protected route redirects

### E2E Tests (Playwright)

- Test complete user journeys
- Test responsive behavior
- Test cross-browser compatibility

---

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| JWT Storage | localStorage | Simple, no backend changes |
| API Client | Axios with interceptors | Centralized auth, error handling |
| Route Protection | Middleware + hooks | Server-side + client-side |
| State Management | Context + local state | Minimal dependencies |
| Form Validation | Custom logic | Full control, no library |
| Loading/Errors | Conditional rendering | Simple, explicit |

All decisions align with constitution principles:
- ✅ Security-first (JWT validation, protected routes)
- ✅ Minimal dependencies (no unnecessary libraries)
- ✅ Deterministic behavior (explicit patterns)
- ✅ Full-stack coherence (matches backend contracts)
