# Backend JWT Authentication Skill

## Overview
Specialized skill for implementing secure JWT (JSON Web Token) authentication in backend applications with best practices for token management, security, and user session handling.

## Core Capabilities

### 1. JWT Token Generation & Validation
- Generate secure access and refresh tokens
- Implement proper token signing with RS256/HS256
- Validate token signatures and claims
- Handle token expiration and renewal
- Implement token blacklisting/revocation

### 2. Authentication Middleware
- Create reusable auth middleware for route protection
- Extract and verify tokens from headers/cookies
- Implement role-based access control (RBAC)
- Handle authentication errors gracefully
- Support multiple authentication strategies

### 3. Secure Password Management
- Hash passwords using bcrypt/argon2
- Implement password strength validation
- Generate secure password reset tokens
- Handle password reset flows
- Prevent timing attacks

### 4. Refresh Token Strategy
- Implement refresh token rotation
- Store refresh tokens securely (database/Redis)
- Handle token family detection for security
- Implement sliding sessions
- Clean up expired tokens

## Implementation Patterns

### Node.js/Express Example Structure
```javascript
// Token service
- generateAccessToken(payload, expiresIn)
- generateRefreshToken(userId)
- verifyAccessToken(token)
- verifyRefreshToken(token)
- revokeRefreshToken(token)

// Auth middleware
- authenticate(req, res, next)
- authorize(...roles)
- optionalAuth(req, res, next)

// Auth routes
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- POST /auth/forgot-password
- POST /auth/reset-password
```

### Security Best Practices
1. **Token Storage**
   - Access tokens: Short-lived (15-30 min)
   - Refresh tokens: Longer-lived (7-30 days)
   - Store refresh tokens in httpOnly cookies or secure database
   - Never store tokens in localStorage for sensitive apps

2. **Token Claims**
   - Include: userId, email, roles, iat, exp
   - Avoid sensitive data in payload
   - Use appropriate token expiration times
   - Include token versioning for invalidation

3. **Security Headers**
   - Set httpOnly and secure flags for cookies
   - Implement CORS properly
   - Add rate limiting on auth endpoints
   - Use HTTPS in production

4. **Error Handling**
   - Don't leak information in error messages
   - Use consistent error responses
   - Log authentication failures
   - Implement account lockout after failed attempts

## Technology Stack Support

### Node.js
- Libraries: jsonwebtoken, bcryptjs, passport-jwt
- Frameworks: Express, Fastify, NestJS, Koa

### Python
- Libraries: PyJWT, passlib, python-jose
- Frameworks: FastAPI, Django, Flask

### Go
- Libraries: golang-jwt, bcrypt
- Frameworks: Gin, Echo, Fiber

### Java/Kotlin
- Libraries: jjwt, spring-security
- Frameworks: Spring Boot, Ktor

## Database Schema Considerations

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  revoked BOOLEAN DEFAULT FALSE,
  replaced_by UUID REFERENCES refresh_tokens(id)
);

-- Create indexes
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

## Common Flows

### Registration Flow
1. Validate user input
2. Check if email exists
3. Hash password
4. Create user record
5. Generate email verification token
6. Send verification email
7. Return success response (don't auto-login)

### Login Flow
1. Validate credentials
2. Find user by email
3. Compare password hash
4. Check if email verified
5. Generate access + refresh tokens
6. Store refresh token
7. Return tokens to client

### Token Refresh Flow
1. Validate refresh token
2. Check if token is revoked
3. Verify token signature and expiration
4. Generate new access token
5. Optionally rotate refresh token
6. Return new tokens

### Logout Flow
1. Verify access token
2. Revoke refresh token(s)
3. Clear client-side tokens
4. Return success response

## Testing Considerations
- Test token expiration handling
- Test invalid token scenarios
- Test refresh token rotation
- Test concurrent login sessions
- Test password reset flows
- Load test authentication endpoints

## Monitoring & Logging
- Log failed login attempts
- Monitor token generation rates
- Track refresh token usage
- Alert on suspicious patterns
- Log security events (password changes, etc.)

## Migration & Versioning
- Plan for secret key rotation
- Support multiple JWT versions
- Handle graceful token invalidation
- Implement feature flags for auth changes

---

**When to use this skill:**
- Building authentication systems from scratch
- Implementing JWT-based APIs
- Securing microservices
- Adding auth to existing applications
- Implementing SSO or OAuth2 flows
- Creating admin/user role systems