from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.config.settings import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token with the provided data."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration_delta)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload if valid, None otherwise."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        # Check if token is expired
        if "exp" in payload:
            expiration = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > expiration:
                return None

        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            return user_id
    return None


def validate_token_signature(token: str) -> bool:
    """Validate the token signature without decoding the payload."""
    try:
        # Try to decode the token with our secret to validate the signature
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], options={"verify_exp": False})
        return True
    except JWTError:
        return False