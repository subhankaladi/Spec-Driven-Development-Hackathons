"""Authentication dependencies for FastAPI with BetterAuth compatibility."""
from typing import Optional
from uuid import UUID
from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from src.models.user import User
from src.models.database import get_session
from src.services.auth_service import get_current_user_from_betterauth, get_optional_user_from_betterauth


class AuthenticationError(HTTPException):
    """Raised when authentication fails."""

    def __init__(self, message: str, code: str = "UNAUTHORIZED"):
        # Convert technical error messages to user-friendly ones
        user_friendly_message = message
        if "expired" in message.lower() or "invalid" in message.lower():
            user_friendly_message = "Your session has expired. Please log in again."
        elif "missing" in message.lower() or "not found" in message.lower():
            user_friendly_message = "Your session has expired. Please log in again."

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user_friendly_message
        )


class TokenUser(BaseModel):
    """User information extracted from JWT token."""

    user_id: UUID
    email: str

    @classmethod
    def from_user_model(cls, user: User) -> "TokenUser":
        """Create TokenUser from User model."""
        return cls(
            user_id=user.id,
            email=user.email,
        )


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> TokenUser:
    """Dependency to extract and verify the current user from BetterAuth session.

    Args:
        request: FastAPI request object containing session information

    Returns:
        TokenUser with user_id and email from session

    Raises:
        AuthenticationError: If session is missing, invalid, or expired
    """
    try:
        # Get user from BetterAuth-compatible session
        user = await get_current_user_from_betterauth(request, session)

        # Convert to TokenUser
        return TokenUser.from_user_model(user)
    except HTTPException as e:
        raise AuthenticationError(
            message=e.detail if isinstance(e.detail, str) else "Authentication failed",
            code="UNAUTHORIZED"
        )


async def get_optional_user(
    request: Request,
    session: Session = Depends(get_session),
) -> Optional[TokenUser]:
    """Dependency to optionally extract user from BetterAuth session.

    Unlike get_current_user, this returns None instead of raising
    an exception when no valid session is provided.

    Args:
        request: FastAPI request object containing session information

    Returns:
        TokenUser if valid session provided, None otherwise
    """
    try:
        user = get_optional_user_from_betterauth(request, session)
        if user:
            return TokenUser.from_user_model(user)
        return None
    except HTTPException:
        return None


def require_auth(
    current_user: TokenUser = Depends(get_current_user),
) -> TokenUser:
    """Explicit auth dependency for routes that require authentication.

    This is an alias for get_current_user that makes the intent clearer
    in route definitions.
    """
    return current_user
