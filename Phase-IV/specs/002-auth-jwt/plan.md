# Implementation Plan: Authentication & Security (Spec-2)

**Feature ID**: `002-auth-jwt`
**Feature Branch**: `002-auth-jwt`
**Created**: `2026-01-07`
**Status**: `Ready for Implementation`

---

## 1. Architecture Overview

This plan covers the authentication implementation using Better Auth for frontend and JWT for API security. The system follows a stateless authentication model where:

1. **Frontend**: Better Auth handles user signup/signin and stores JWT
2. **Token**: JWT contains user_id claim, signed with shared secret
3. **Backend**: FastAPI middleware verifies JWT on every protected request
4. **Database**: Users table stores email and password hash

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   Frontend (Next.js)           Backend (FastAPI)                  │
│   ┌──────────────┐             ┌──────────────┐                  │
│   │ Better Auth  │────────────>│ JWT Verify   │                  │
│   │ Client       │  Bearer     │ Middleware   │                  │
│   └──────┬───────┘  Token      └──────┬───────┘                  │
│          │                            │                           │
│          │  Sign Up/Sign In           │                           │
│          └───────────────────────────>│                           │
│                                        │                          │
│                                        ▼                          │
│                                 ┌──────────────┐                  │
│                                 │   /auth/*   │  Public          │
│                                 │  Endpoints  │                  │
│                                 └──────────────┘                  │
│                                        │                          │
│                                        ▼                          │
│                                 ┌──────────────┐                  │
│                                 │  Protected   │  JWT Required    │
│                                 │  Endpoints   │                  │
│                                 └──────────────┘                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Key Decisions

### 2.1 JWT Strategy

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Algorithm | HS256 | Symmetric, fast, widely supported |
| Secret | Shared via env | Backend-only verification needed |
| Expiration | 7 days | Balance security and UX |
| Claims | user_id, email | Minimal payload, no sensitive data |

**Trade-off Analysis:**
- HS256 vs RS256: HS256 is simpler for single-service auth, RS256 better for distributed systems
- We chose HS256 because: (1) no need for public key infrastructure, (2) faster verification, (3) simpler deployment

### 2.2 Password Hashing

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Algorithm | bcrypt | Industry standard, adaptive cost |
| Rounds | 12 | Balance security and performance |
| Comparison | timing-safe | Prevent timing attacks |

### 2.3 User Isolation

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| User ID Source | JWT claim | Trusted, authenticated source |
| Path Validation | JWT user_id == URL user_id | Prevents IDOR attacks |
| DB Queries | Always filter by JWT user_id | Defense in depth |

## 3. Interfaces and API Contracts

### 3.1 Auth Endpoints

#### POST /auth/signup

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-07T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (400/409):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format"
  }
}
```

#### POST /auth/signin

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (401):**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid email or password"
  }
}
```

### 3.2 Protected Endpoints (Updated)

All existing task endpoints require `Authorization: Bearer <token>` header.

| Endpoint | New Requirement |
|----------|-----------------|
| GET /users/{user_id}/tasks | JWT with matching user_id |
| POST /users/{user_id}/tasks | JWT with matching user_id |
| GET /users/{user_id}/tasks/{task_id} | JWT with matching user_id |
| PUT /users/{user_id}/tasks/{task_id} | JWT with matching user_id |
| DELETE /users/{user_id}/tasks/{task_id} | JWT with matching user_id |

**Response (401):**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

## 4. Data Model

### 4.1 User Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### 4.2 Configuration

```python
# backend/src/config.py (updates)
class Settings(BaseSettings):
    # ... existing settings ...

    # Auth settings
    JWT_SECRET: str = Field(..., description="Secret key for JWT signing")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=168)  # 7 days
    BCRYPT_ROUNDS: int = Field(default=12)
```

## 5. Implementation Phases

### Phase 1: Database & Configuration
- Add User SQLModel entity
- Update config with auth settings
- Create Alembic migration

### Phase 2: Auth Service
- Password hashing utilities
- JWT token creation/verification
- User CRUD operations

### Phase 3: Auth Endpoints
- POST /auth/signup
- POST /auth/signin
- Token validation helper

### Phase 4: JWT Middleware
- Authorization header extraction
- JWT verification middleware
- Error handling for 401 responses

### Phase 5: Update Task Endpoints
- Add dependency on JWT middleware
- Update task routes to use authenticated user_id
- Remove unauthenticated access

### Phase 6: Frontend Integration
- Configure Better Auth
- Create auth hooks
- Update API client with token

### Phase 7: Testing
- Unit tests for auth utilities
- Integration tests for endpoints
- Security tests for user isolation

## 6. Non-Functional Requirements

### 6.1 Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| JWT verification | <5ms | p95 latency |
| Password hashing | <50ms | bcrypt with 12 rounds |
| Auth endpoint | <100ms | p95 latency |

### 6.2 Security
| Requirement | Implementation |
|-------------|----------------|
| Password storage | bcrypt with 12 rounds |
| Token signing | HS256 with 256-bit secret |
| Token expiration | 7 days (configurable) |
| SQL injection | SQLModel ORM |
| IDOR protection | JWT user_id validation |

### 6.3 Reliability
| SLO | Target |
|-----|--------|
| Auth availability | 99.9% |
| False positive rate | <0.1% |

## 7. Risk Analysis

### Risk 1: JWT Secret Leakage
**Impact**: Critical - attackers can forge tokens
**Mitigation**:
- Store secret in environment variable
- Rotate secret if compromised (with migration period)
- Audit access to secret

### Risk 2: Brute Force Attacks
**Impact**: High - account takeover
**Mitigation**:
- Rate limiting on signin/signup
- Account lockout after failed attempts
- Strong password requirements

### Risk 3: Token Theft
**Impact**: High - unauthorized access
**Mitigation**:
- Short expiration (7 days)
- HTTPS only in production
- Consider refresh token rotation (Phase 3)

## 8. Files to Create/Modify

### New Files
```
backend/src/models/user.py          # User SQLModel entity
backend/src/core/auth.py            # Auth utilities (JWT, password)
backend/src/api/routes/auth.py      # Auth endpoints
backend/src/api/dependencies/auth.py # FastAPI dependencies
frontend/src/lib/auth.ts            # Better Auth configuration
frontend/src/hooks/useAuth.ts       # Auth hooks
```

### Modified Files
```
backend/src/config.py              # Add auth settings
backend/src/main.py               # Add auth middleware
backend/src/api/routes/tasks.py   # Add auth dependency
backend/requirements.txt          # Add bcrypt, PyJWT
alembic/versions/                 # Migration for users table
```

## 9. Testing Strategy

### Unit Tests
- Password hashing/verification
- JWT token creation/verification
- Input validation

### Integration Tests
- Sign up flow (success + validation errors)
- Sign in flow (success + invalid credentials)
- Token refresh flow

### Security Tests
- Access with invalid token
- Access with expired token
- Access without token
- Cross-user task access (should fail)
- User enumeration prevention

### Regression Tests
- All 15 existing tests must pass
- Task CRUD with authentication

## 10. Rollback Plan

### Rollback Triggers
- >1% authentication failures
- Security vulnerability discovered
- Data integrity issues

### Rollback Steps
1. Revert JWT_SECRET to previous value
2. Deploy with auth disabled in config
3. Users can sign in with old tokens during migration
4. Fix and redeploy

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sign up success rate | >95% | 201 / total attempts |
| Sign in success rate | >95% | 200 / total attempts |
| Auth tests pass rate | 100% | All tests passing |
| Cross-user access | 0% | 0 successful breaches |
| Token verification latency | <10ms | p95 |

---

## 12. Open Questions & Decisions Needed

| Question | Impact | Recommendation |
|----------|--------|----------------|
| Rate limiting implementation? | Security | Use SlowAPI for built-in rate limiting |
| Refresh token strategy? | UX | Defer to Phase 3 |
| Better Auth version? | Frontend | Use latest stable (1.x) |

---

**Plan Prepared**: 2026-01-07
**Status**: Ready for Tasks Generation
