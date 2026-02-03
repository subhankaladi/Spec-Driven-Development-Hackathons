"""Error response schemas and custom exceptions."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from fastapi import HTTPException, status


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: dict = Field(..., description="Error details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Title is required",
                    "details": {"field": "title"}
                }
            }
        }
    )


class ValidationError(HTTPException):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": details
            }
        )


class NotFoundError(HTTPException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": message,
                "details": {"resource_id": resource_id} if resource_id else None
            }
        )


class DatabaseError(HTTPException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": message,
                "details": None
            }
        )
