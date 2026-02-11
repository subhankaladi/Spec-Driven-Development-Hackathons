"""Rate limiting middleware for chat endpoints.

This middleware enforces request rate limits per authenticated user to prevent abuse
and ensure fair resource allocation.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using in-memory storage.

    Tracks requests per user_id (from JWT) and enforces configurable rate limits.
    """

    def __init__(self, app, rate_limit: int = 10, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            app: FastAPI application instance
            rate_limit: Maximum requests per window (default: 10)
            window_seconds: Time window in seconds (default: 60)
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        # Storage: user_id -> list of request timestamps
        self.requests: Dict[str, List[datetime]] = {}

        logger.info(
            f"RateLimitMiddleware initialized: "
            f"{rate_limit} requests per {window_seconds} seconds"
        )

    async def dispatch(self, request: Request, call_next):
        """Process request and enforce rate limit.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response from next handler

        Raises:
            HTTPException: 429 Too Many Requests if rate limit exceeded
        """
        # Only apply rate limiting to chat endpoint
        if not request.url.path.startswith("/api/chat"):
            return await call_next(request)

        # Skip rate limiting for non-POST requests (GET is read-only)
        if request.method != "POST":
            return await call_next(request)

        # Check if rate limiting is disabled (rate_limit = 0)
        if self.rate_limit == 0:
            logger.debug("Rate limiting disabled (CHAT_RATE_LIMIT=0)")
            return await call_next(request)

        # Extract user identifier from Authorization header or cookies
        # Since rate limiting happens before auth dependency, we extract from raw request
        user_key = self._extract_user_key(request)
        if not user_key:
            # No auth token means request will fail at auth layer - let it through
            return await call_next(request)

        # Clean up old requests outside the time window
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=self.window_seconds)

        if user_key in self.requests:
            # Remove timestamps older than the window
            self.requests[user_key] = [
                ts for ts in self.requests[user_key]
                if ts > cutoff_time
            ]
        else:
            self.requests[user_key] = []

        # Check if rate limit is exceeded
        if len(self.requests[user_key]) >= self.rate_limit:
            logger.warning(
                f"Rate limit exceeded for user {user_key[:10]}...: "
                f"{len(self.requests[user_key])} requests in {self.window_seconds}s"
            )
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in a moment."
            )

        # Add current request timestamp
        self.requests[user_key].append(now)

        logger.debug(
            f"Rate limit check passed for user {user_key[:10]}...: "
            f"{len(self.requests[user_key])}/{self.rate_limit} requests"
        )

        # Process request
        return await call_next(request)

    def _extract_user_key(self, request: Request) -> str:
        """Extract user identifier for rate limiting.

        Args:
            request: Incoming HTTP request

        Returns:
            User identifier string (token hash) or empty string if not found
        """
        # Try Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Use first 32 chars of token as key (enough to be unique)
            return token[:32] if len(token) > 32 else token

        # Try better-auth-session cookie
        token = request.cookies.get("better-auth-session")
        if token:
            return token[:32] if len(token) > 32 else token

        return ""


def get_rate_limit_from_env() -> int:
    """Get rate limit configuration from environment variable.

    Returns:
        Rate limit value (0 to disable, default: 10)
    """
    try:
        limit = int(os.getenv("CHAT_RATE_LIMIT", "10"))
        return max(0, limit)  # Ensure non-negative
    except ValueError:
        logger.warning("Invalid CHAT_RATE_LIMIT value, using default of 10")
        return 10
