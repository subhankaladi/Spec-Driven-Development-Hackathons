# API Security Contract: Authentication & Authorization

**Feature**: 002-auth-security
**Date**: 2025-12-22
**Version**: 1.0.0

## API Security Overview

This document describes the security requirements for the Todo API. All endpoints require valid JWT authentication, and proper user ID matching is enforced to prevent cross-user access.

## Authentication Requirements

### JWT Token Format
- **Algorithm**: HS256 (or as configured)
- **Claims**:
  - `sub`: User ID (required)
  - `iat`: Issued at timestamp (required)
  - `exp`: Expiration timestamp (required)
  - `jti`: JWT ID (optional)

### Authorization Header
All authenticated requests must include:
```
Authorization: Bearer <jwt-token>
```

## Security Endpoints

### Authentication Required
All existing endpoints now require authentication:

- `GET /api/v1/tasks` - Requires valid JWT, returns only user's tasks
- `POST /api/v1/tasks` - Requires valid JWT, creates task for authenticated user
- `GET /api/v1/tasks/{id}` - Requires valid JWT, user_id must match task owner
- `PUT /api/v1/tasks/{id}` - Requires valid JWT, user_id must match task owner
- `DELETE /api/v1/tasks/{id}` - Requires valid JWT, user_id must match task owner

## Security Response Codes

### 401 Unauthorized
- No Authorization header provided
- Invalid token format
- Expired token
- Invalid signature

### 403 Forbidden
- Valid token but user ID doesn't match requested resource
- Insufficient permissions for the requested action

## Security Validation Rules

### Token Validation
1. Check for Authorization header with Bearer token
2. Decode JWT using shared secret
3. Verify token signature
4. Check token expiration
5. Extract user ID from subject claim

### User ID Matching
1. Extract user ID from JWT token
2. Extract user ID from URL path parameters (where applicable)
3. Compare user IDs - return 403 if they don't match
4. Allow access only if user IDs match or endpoint doesn't require user-specific access

## Example Requests

### Valid Authenticated Request
```
GET /api/v1/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Invalid Token Request
```
GET /api/v1/tasks
Authorization: Bearer invalid.token.here
```
Response: `401 Unauthorized`

### Cross-User Access Attempt
```
GET /api/v1/tasks/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm90aGVyLXVzZXIiLCJpYXQiOjE1MTYyMzkwMjJ9.invalid_signature
```
Response: `403 Forbidden`

## Error Response Format

### 401 Unauthorized
```json
{
  "detail": "Not authenticated",
  "error_code": "AUTH_001"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied",
  "error_code": "AUTH_002"
}
```