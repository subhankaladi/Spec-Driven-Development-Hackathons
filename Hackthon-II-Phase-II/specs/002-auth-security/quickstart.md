# Quickstart Guide: Authentication & API Security

**Feature**: 002-auth-security
**Date**: 2025-12-22

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ for frontend
- Better Auth account or self-hosted instance
- Environment variables configured for JWT secrets

### Installation

1. **Set up environment variables**
   ```bash
   # Backend .env file
   JWT_SECRET="your-very-secure-jwt-secret-key-here"
   JWT_ALGORITHM="HS256"

   # Frontend environment variables
   NEXTAUTH_URL="http://localhost:3000"
   NEXTAUTH_SECRET="your-nextauth-secret"
   ```

2. **Install backend dependencies**
   ```bash
   pip install python-jose[cryptography] python-multipart
   ```

3. **Install frontend dependencies**
   ```bash
   npm install @better-auth/react @better-auth/node
   ```

## Configuration

### Better Auth Setup (Frontend)
```javascript
// frontend/src/lib/auth.js
import { createAuthClient } from "@better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  // JWT configuration
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
    expiresIn: "7d",
  }
});
```

### FastAPI Middleware Setup (Backend)
```python
# backend/src/auth/middleware.py
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.src.config.settings import settings

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            token = credentials.credentials
            user_id = self.verify_jwt(token)
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token or expired token")
            request.state.user_id = user_id
            return token
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization code")

    def verify_jwt(self, jwtoken: str) -> str:
        try:
            payload = jwt.decode(jwtoken, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("sub")
            return user_id
        except JWTError:
            return None
```

## API Usage with Authentication

### Making Authenticated Requests
```bash
# Get JWT token from Better Auth
# Then use it in API requests:

curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <your-jwt-token>"
```

### User ID Matching
All endpoints that operate on user-specific data will validate that the user ID in the JWT token matches the user ID in the URL:
```bash
# Valid: Token user_id matches URL user_id
curl -X GET http://localhost:8000/api/v1/users/123/tasks \
  -H "Authorization: Bearer <jwt-token-with-user-id-123>"

# Invalid: Token user_id does not match URL user_id (returns 403)
curl -X GET http://localhost:8000/api/v1/users/456/tasks \
  -H "Authorization: Bearer <jwt-token-with-user-id-123>"
```

## Development

### Running Tests
```bash
# Backend authentication tests
pytest tests/auth/
```

### Environment Variables
- `JWT_SECRET`: Secret key for JWT signing/verification
- `JWT_ALGORITHM`: Algorithm to use for JWT (default: HS256)
- `JWT_EXPIRATION_DELTA`: Token expiration time (default: 7 days)