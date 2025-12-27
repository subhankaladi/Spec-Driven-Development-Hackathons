# Data Model: Authentication & API Security

**Feature**: 002-auth-security
**Date**: 2025-12-22

## JWT Token Entity

### Claims Structure
- **sub** (Subject): User ID, uniquely identifies the user
- **iat** (Issued At): Unix timestamp when the token was issued
- **exp** (Expiration Time): Unix timestamp when the token expires
- **jti** (JWT ID): Unique identifier for the token
- **name** (User Name): User's display name (optional)
- **email** (Email): User's email address (optional)

### Validation Rules
- Token must be properly signed with the shared secret
- Current time must be before the expiration time (exp)
- Token must have all required claims (sub, iat, exp)
- User ID (sub) must be a valid identifier format

### State Transitions
- **Issued**: When a new JWT token is created by Better Auth
- **Valid**: When a token is being used for authentication and is within its validity period
- **Expired**: When a token has passed its expiration time
- **Invalid**: When a token is malformed, improperly signed, or has invalid claims

## User Identity Entity

### Properties
- **user_id** (String): Unique identifier for the authenticated user
- **name** (String, Optional): User's display name
- **email** (String, Optional): User's email address
- **is_authenticated** (Boolean): Whether the user is properly authenticated
- **token_scopes** (List, Optional): Scopes granted to the token

### Validation Rules
- user_id must match the subject (sub) claim in the JWT token
- User must exist in the system if authenticated
- User identity can only access resources associated with the same user_id

## Authentication Middleware Entity

### Purpose
- Intercepts incoming requests to validate JWT tokens
- Extracts user identity from valid tokens
- Stores user identity in request context for use by endpoints
- Handles invalid token responses

### Characteristics
- Stateless operation (no session storage required)
- Thread-safe for concurrent requests
- Efficient validation (under 50ms per request)
- Proper error handling for different token validation failures

## API Security Contract Models

### AuthenticatedUser
- **user_id** (String): The authenticated user's unique identifier
- **name** (String, Optional): User's display name
- **email** (String, Optional): User's email address
- **is_authenticated** (Boolean): Always true for authenticated users

### AuthenticatedRequest
- **user** (AuthenticatedUser): The authenticated user making the request
- **token_valid** (Boolean): Whether the token is valid
- **timestamp** (DateTime): When the request was authenticated

### AuthError
- **error_code** (String): Error code identifying the auth issue
- **message** (String): Human-readable error message
- **timestamp** (DateTime): When the error occurred