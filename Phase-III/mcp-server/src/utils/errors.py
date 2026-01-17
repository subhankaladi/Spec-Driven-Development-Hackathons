"""Custom error classes for MCP server tool operations.

All errors are raised by tool handlers and converted to structured MCP responses.
"""


class AuthenticationError(Exception):
    """Raised when JWT token is missing, invalid, or expired.

    Maps to HTTP 401 Unauthorized.

    Examples:
        - Missing jwt_token parameter
        - Invalid token signature
        - Expired token
        - Malformed token structure
    """
    pass


class ValidationError(Exception):
    """Raised when input parameters fail validation.

    Maps to HTTP 400 Bad Request.

    Examples:
        - Empty required field
        - Field exceeds max length
        - Invalid UUID format
        - Invalid enum value
        - Out of range pagination parameters
    """
    pass


class NotFoundError(Exception):
    """Raised when requested resource doesn't exist.

    Maps to HTTP 404 Not Found.

    Examples:
        - Task ID not found in database
        - User ID not found
        - Resource already deleted
    """
    pass


class AuthorizationError(Exception):
    """Raised when user not authorized to access resource.

    Maps to HTTP 403 Forbidden.

    Examples:
        - Task belongs to different user
        - User attempting to access another user's resource
        - JWT user_id mismatch with resource owner
    """
    pass


class DatabaseError(Exception):
    """Raised when database operation fails unexpectedly.

    Maps to HTTP 500 Internal Server Error.

    Examples:
        - Database connection timeout
        - Query execution failure
        - Transaction rollback
        - Connection pool exhausted
    """
    pass
