"""
JWT authentication and user context validation.

Validates JWT tokens and extracts user_id for ownership enforcement.
"""

import logging
from typing import Optional
from uuid import UUID

import jwt

from .config import Config

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Authentication error."""
    pass


def extract_user_id(token: str) -> UUID:
    """
    Extract user_id from JWT token.

    Args:
        token: JWT token string

    Returns:
        UUID: Extracted user_id

    Raises:
        AuthError: If token is invalid or user_id not found
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        user_id_str = payload.get("sub") or payload.get("user_id")
        if not user_id_str:
            raise AuthError("No user_id in token")
        return UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {e}")
    except (ValueError, TypeError) as e:
        raise AuthError(f"Invalid user_id format: {e}")


def validate_token(token: Optional[str]) -> UUID:
    """
    Validate token and return user_id.

    Args:
        token: JWT token string or None

    Returns:
        UUID: Extracted user_id

    Raises:
        AuthError: If token is missing or invalid
    """
    if not token:
        raise AuthError("No authentication token provided")
    return extract_user_id(token)
