from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # NOTE: In this backend, JWT 'sub' is a stringified int user id (src/auth/utils.py)
    # but Spec-6 contract uses UUID format. We'll store as str to match auth.
    user_id: str = Field(index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
