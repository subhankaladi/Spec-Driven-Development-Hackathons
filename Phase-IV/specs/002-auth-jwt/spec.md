# Feature Specification: Authentication & Security (Spec-2)

**Feature ID**: `002-auth-jwt`
**Version**: `1.0.0`
**Status**: `Draft`
**Created**: `2026-01-07`
**Feature Branch**: `002-auth-jwt`

---

## 1. Overview

This specification defines the authentication and security implementation for the Todo Full-Stack Web Application. The system uses **Better Auth** for frontend authentication and **JWT (JSON Web Tokens)** for stateless API authorization.

## 2. Problem Statement

Currently, the Task API Backend (`spec-001`) lacks authentication. All endpoints are accessible without any credentials, which means:
- Any user can access any other user's tasks
- There's no way to identify who is making requests
- The system cannot enforce user-level security boundaries

## 3. User Stories

### US1: User Registration (Sign Up)
**As a** new user, **I want to** create an account with email and password, **so that** I can access the task management system.

**Acceptance Criteria:**
- [ ] User can sign up with email and password
- [ ] Password is hashed before storage (bcrypt/argon2)
- [ ] Email uniqueness is enforced
- [ ] Invalid email format returns 400
- [ ] Weak password returns 400 (min 8 chars)
- [ ] Successful signup returns 201 with user profile (no password)
- [ ] JWT token is issued upon successful signup

### US2: User Authentication (Sign In)
**As a** registered user, **I want to** sign in with my credentials, **so that** I can access my tasks securely.

**Acceptance Criteria:**
- [ ] User can sign in with email and password
- [ ] Correct credentials return 200 with JWT token
- [ ] Invalid credentials return 401 Unauthorized
- [ ] JWT token contains user_id claim
- [ ] Token includes expiration time (e.g., 7 days)
- [ ] Password is verified securely (timing-safe comparison)

### US3: JWT Token Authentication (API Security)
**As a** authenticated user, **I want to** access the Task API using a JWT token, **so that** my requests are authenticated.

**Acceptance Criteria:**
- [ ] API accepts Bearer token in `Authorization` header
- [ ] Valid token allows access to task endpoints
- [ ] Invalid token returns 401 Unauthorized
- [ ] Expired token returns 401 Unauthorized
- [ ] Missing token returns 401 Unauthorized
- [ ] Malformed token returns 401 Unauthorized

### US4: Protected Task Access
**As a** authenticated user, **I want to** only access my own tasks, **so that** I cannot view or modify other users' data.

**Acceptance Criteria:**
- [ ] User can only list their own tasks
- [ ] User can only get their own tasks
- [ ] User can only update their own tasks
- [ ] User can only delete their own tasks
- [ ] Accessing other user's tasks returns 404 (not 403)
- [ ] Token user_id must match requested user_id in URL

### US5: Token Refresh (Optional - Phase 2)
**As a** authenticated user, **I want to** refresh my token before it expires, **so that** I can continue using the app without re-authenticating.

**Acceptance Criteria:**
- [ ] Valid expired-ish token can be refreshed
- [ ] Refresh token endpoint returns new JWT
- [ ] Old token remains valid until expiration
- [ ] Refresh token rotation is implemented

## 4. Functional Requirements

### 4.1 Authentication Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │ Better Auth │ ──────> │   Backend   │
│   (Next.js) │         │   (Client)  │         │  (FastAPI)  │
└─────────────┘         └─────────────┘         └─────────────┘
        │                     │                        │
        │  1. Sign Up/Sign In │                        │
        │ <───────────────────│                        │
        │                     │                        │
        │  2. Store JWT       │                        │
        │ <───────────────────│                        │
        │                     │                        │
        │  3. Bearer Token    │                        │
        │ ──────────────────> │  4. Verify JWT        │
        │                     │ ────────────────────> │
        │                     │                        │
        │                     │  5. Allow/Deny        │
        │                     │ <─────────────────────│
        │  6. Response        │                        │
        │ <───────────────────│                        │
```

### 4.2 JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid-here",
    "email": "user@example.com",
    "iat": 1735689600,
    "exp": 1736294400,
    "iss": "todo-app"
  }
}
```

**Claims:**
- `sub`: User ID (UUID)
- `email`: User's email address
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp
- `iss`: Issuer (for validation)

### 4.3 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Create new account | No |
| POST | `/auth/signin` | Sign in & get token | No |
| POST | `/auth/refresh` | Refresh JWT token | No |
| GET | `/users/{user_id}/tasks` | List user's tasks | Yes |
| POST | `/users/{user_id}/tasks` | Create a task | Yes |
| GET | `/users/{user_id}/tasks/{task_id}` | Get a task | Yes |
| PUT | `/users/{user_id}/tasks/{task_id}` | Update a task | Yes |
| DELETE | `/users/{user_id}/tasks/{task_id}` | Delete a task | Yes |

### 4.4 Error Responses

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

| Status | Code | Message |
|--------|------|---------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 401 | UNAUTHORIZED | Invalid token |
| 401 | UNAUTHORIZED | Token expired |
| 401 | UNAUTHORIZED | Missing authorization header |
| 404 | NOT_FOUND | User or task not found |

## 5. Key Entities

### 5.1 User Model

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5.2 Auth Configuration

```python
class AuthConfig:
    JWT_SECRET: str  # Shared secret for signing/verifying
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days
    BCRYPT_ROUNDS: int = 12
```

## 6. Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Sign up success rate | >95% | 201 responses / total signup attempts |
| Sign in success rate | >95% | 200 responses / total signin attempts |
| Unauthorized access blocked | 100% | 401 responses for invalid/missing tokens |
| Cross-user task access | 0% | 0 successful cross-user accesses in tests |
| Token verification latency | <10ms | p95 latency for JWT verification |
| Password hashing time | <100ms | p95 latency for bcrypt verify |

## 7. Security Requirements

1. **Password Storage**: bcrypt with minimum 10 rounds
2. **Token Security**: HS256 algorithm, 256-bit secret
3. **Token Expiration**: Maximum 7 days (configurable)
4. **No Sensitive Data in Token**: Never include password hash
5. **HTTPS Only**: Production requires TLS 1.2+
6. **Rate Limiting**: Apply to auth endpoints (prevent brute force)
7. **Timing-Safe Comparison**: Use for password verification

## 8. Out of Scope

- OAuth social login (Google, GitHub, etc.)
- Email verification flow
- Password reset functionality
- Multi-factor authentication (MFA)
- Session management (we use stateless JWT)
- Role-based access control (RBAC)

## 9. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.109+ | Backend framework |
| SQLModel | 0.0.14+ | ORM |
| bcrypt | 4.1+ | Password hashing |
| PyJWT | 2.9+ | JWT handling |
| Better Auth | 1.x | Frontend auth |
| Neon PostgreSQL | Serverless | Database |

## 10. Validation Checklist

- [ ] Sign up with valid email/password returns 201
- [ ] Sign up with duplicate email returns 409
- [ ] Sign up with invalid email returns 400
- [ ] Sign up with weak password returns 400
- [ ] Sign in with valid credentials returns 200 with token
- [ ] Sign in with invalid credentials returns 401
- [ ] Protected endpoint without token returns 401
- [ ] Protected endpoint with invalid token returns 401
- [ ] Protected endpoint with expired token returns 401
- [ ] User can access own tasks
- [ ] User cannot access other user's tasks (returns 404)
- [ ] All 15 existing tests still pass
- [ ] New auth tests have 100% pass rate
- [ ] JWT secret is loaded from environment
- [ ] Password hash is never exposed in API responses

## 11. Implementation Notes

### 11.1 User Isolation Enforcement

The current implementation uses `user_id` from the URL path. With JWT auth, we must:
1. Extract `user_id` from JWT token
2. Verify it matches the `user_id` in the URL path
3. Use the JWT `user_id` for all database queries

```python
# Current (no auth):
def get_tasks(user_id: UUID):
    return session.query(Task).filter(Task.user_id == user_id).all()

# Required (with auth):
def get_tasks(token_user_id: UUID, url_user_id: UUID):
    if token_user_id != url_user_id:
        raise UnauthorizedError("Cannot access other user's tasks")
    return session.query(Task).filter(Task.user_id == token_user_id).all()
```

### 11.2 Better Auth Integration

Better Auth provides:
- React hooks for sign up/sign in
- Token management (automatic refresh)
- Session state management

The backend needs:
- Endpoints that accept Better Auth tokens
- JWT verification middleware

## 12. Open Questions

1. Should we use Better Auth's built-in JWT or issue our own?
   - **Decision needed**: Shared secret approach allows backend-only JWT verification
2. Should refresh tokens be implemented in Phase 2?
   - **Recommendation**: Defer to Phase 3 for MVP
3. Should we implement rate limiting for auth endpoints?
   - **Recommendation**: Yes, prevent brute force attacks
