from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import hashlib
import secrets


class UserBase(SQLModel):
    """Base user model with common fields."""
    email: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    """Database model for users."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        # Extract salt from stored hash (format: salt$hash)
        parts = self.hashed_password.split("$")
        if len(parts) != 2:
            return False
        salt, stored_hash = parts
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return password_hash == stored_hash

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage using PBKDF2."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return f"{salt}${password_hash}"


class UserCreate(SQLModel):
    """Schema for creating a new user."""
    email: str
    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Schema for reading user data (excludes password)."""
    id: int
    created_at: datetime


class TokenResponse(SQLModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
