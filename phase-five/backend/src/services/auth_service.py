"""
BetterAuth-compatible authentication service for FastAPI backend.
This service integrates with BetterAuth frontend by validating
session cookies and providing user context.
"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from ..models.user import User
from ..models.database import get_session
import json
import base64
from datetime import datetime, timedelta
import hashlib
import os

# Using python-jose for JWT handling since BetterAuth often uses JWT tokens
from jose import JWTError, jwt
import bcrypt


class TokenData(BaseModel):
    user_id: str
    email: str
    exp: int


class BetterAuthIntegration:
    """
    Integration service to handle BetterAuth-compatible authentication
    with the existing FastAPI backend.
    """

    def __init__(self):
        # Get secret from environment or config
        self.secret = os.getenv("JWT_SECRET", "fallback_secret_key_for_dev")
        self.algorithm = "HS256"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        # Bcrypt has a 72 byte limit - truncate password if needed
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def get_password_hash(self, password: str) -> str:
        """Hash a password, truncating if necessary to comply with bcrypt limits."""
        # Bcrypt has a 72 byte limit - truncate password if needed
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            exp: int = payload.get("exp")

            if user_id is None or email is None:
                return None

            token_data = TokenData(user_id=user_id, email=email, exp=exp)
            return token_data
        except JWTError:
            return None


# Global instance
auth_service = BetterAuthIntegration()


class UserSession(BaseModel):
    """Represents a user session from BetterAuth."""
    user_id: str
    email: str
    expires_at: datetime


async def get_current_user_from_betterauth(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current user from BetterAuth session.
    This function looks for BetterAuth-compatible session information
    in the request and validates it against the database.
    """
    # Try to get the session from cookies (support both access_token and better-auth-session)
    auth_cookie = request.cookies.get("access_token") or request.cookies.get("better-auth-session") or request.headers.get("Authorization")

    if not auth_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Remove Bearer prefix if present
    if auth_cookie.startswith("Bearer "):
        auth_cookie = auth_cookie[7:]

    # Decode the token using our auth service
    token_data = auth_service.decode_token(auth_cookie)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Check if token is expired
    if token_data.exp < int(datetime.utcnow().timestamp()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    # Get user from database
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def get_optional_user_from_betterauth(
    request: Request,
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Dependency to optionally get the current user from BetterAuth session.
    Returns None if no valid session is found.
    """
    try:
        return get_current_user_from_betterauth(request, session)
    except HTTPException:
        return None