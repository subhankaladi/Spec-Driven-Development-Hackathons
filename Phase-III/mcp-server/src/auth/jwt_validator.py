"""JWT token validation for MCP server tool authentication.

This module reuses the backend's BetterAuthIntegration to validate JWT tokens
and extract user identity for tool invocations.
"""

import sys
import os
from typing import Optional
from datetime import datetime

# Add backend to Python path for imports
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.services.auth_service import BetterAuthIntegration
from ..utils.errors import AuthenticationError


# Global auth service instance
auth_service = BetterAuthIntegration()


async def validate_jwt_token(token: Optional[str]) -> str:
    """Validate JWT token and extract user ID.

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        User ID (UUID string) extracted from token 'sub' claim

    Raises:
        AuthenticationError: If token is missing, invalid, expired, or malformed

    Examples:
        >>> user_id = await validate_jwt_token("eyJhbGciOiJIUzI1NiIs...")
        >>> print(user_id)
        '123e4567-e89b-12d3-a456-426614174000'
    """
    # Check if token is provided
    if not token or not isinstance(token, str):
        raise AuthenticationError("Missing authentication token")

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    # Decode and validate token
    token_data = auth_service.decode_token(token)

    if token_data is None:
        raise AuthenticationError("Invalid authentication token")

    # Check if token is expired
    current_timestamp = int(datetime.utcnow().timestamp())
    if token_data.exp < current_timestamp:
        raise AuthenticationError("Authentication token has expired")

    # Extract user_id from 'sub' claim
    user_id = token_data.user_id

    if not user_id:
        raise AuthenticationError("Invalid token: missing user identity")

    return user_id
