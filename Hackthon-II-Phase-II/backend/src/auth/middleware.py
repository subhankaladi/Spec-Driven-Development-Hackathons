from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from src.auth.utils import verify_token, validate_token_signature
from src.config.settings import settings


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme.lower() == "bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            token = credentials.credentials

            # Check token signature first
            if not validate_token_signature(token):
                raise HTTPException(status_code=401, detail="Invalid token signature")

            user_id = self.verify_jwt(token)
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token or expired token")
            request.state.user_id = user_id
            return token
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization code")

    def verify_jwt(self, jwtoken: str) -> str:
        try:
            payload = verify_token(jwtoken)
            if payload:
                user_id = payload.get("sub")
                return user_id
            return None
        except JWTError:
            return None


# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/signup",
    "/api/v1/auth/signin",
]


def is_public_route(path: str) -> bool:
    """Check if the path is a public route that doesn't require authentication."""
    return path in PUBLIC_ROUTES or path.startswith("/docs") or path.startswith("/redoc")


# Alternative middleware approach as a function
async def jwt_middleware(request: Request, call_next):
    """JWT middleware function to verify tokens and extract user identity."""
    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    # Skip authentication for public routes
    if is_public_route(request.url.path):
        response = await call_next(request)
        return response

    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    # Validate token signature
    if not validate_token_signature(token):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    # Verify the token and check expiration
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    # Store user ID in request state for use by endpoints
    request.state.user_id = user_id

    response = await call_next(request)
    return response