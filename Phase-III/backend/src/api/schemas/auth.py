"""Authentication Pydantic schemas for API request/response."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class SignUpRequest(BaseModel):
    """Schema for user registration request."""

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="User's email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class SignInRequest(BaseModel):
    """Schema for user sign-in request."""

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="User's email address"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="User's password"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User's email address")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com"
            }
        }
    )


class SignUpResponse(BaseModel):
    """Schema for sign-up response."""

    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="Access token for authentication")
    refresh_token: str = Field(..., description="Refresh token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(..., description="Type of token (e.g., bearer)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "refresh_token_here",
                "expires_in": 900,
                "token_type": "bearer"
            }
        }
    )


class SignInResponse(BaseModel):
    """Schema for sign-in response."""

    access_token: str = Field(..., description="Access token for authentication")
    refresh_token: str = Field(..., description="Refresh token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(..., description="Type of token (e.g., bearer)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "refresh_token_here",
                "expires_in": 900,
                "token_type": "bearer"
            }
        }
    )