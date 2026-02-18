"""ToolInvocation database model for AI chat agent."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class ToolInvocation(SQLModel, table=True):
    """ToolInvocation entity for tracking MCP tool calls.

    Attributes:
        id: Unique tool invocation identifier (UUID)
        message_id: Parent message identifier (UUID, foreign key, indexed)
        tool_name: Name of the invoked MCP tool
        input_params: JSON-encoded input parameters
        output_result: JSON-encoded output result (optional)
        success: Boolean flag indicating success/failure
        error_message: Error message if invocation failed (optional)
        created_at: Timestamp of tool invocation
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique tool invocation identifier"
    )
    message_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="message.id",
        description="Parent message identifier (UUID)"
    )
    tool_name: str = Field(
        nullable=False,
        max_length=100,
        description="Name of the invoked MCP tool"
    )
    input_params: str = Field(
        nullable=False,
        description="JSON-encoded input parameters"
    )
    output_result: Optional[str] = Field(
        default=None,
        nullable=True,
        description="JSON-encoded output result"
    )
    success: bool = Field(
        nullable=False,
        description="Boolean flag indicating success/failure"
    )
    error_message: Optional[str] = Field(
        default=None,
        nullable=True,
        max_length=1000,
        description="Error message if invocation failed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<ToolInvocation id={self.id} tool_name='{self.tool_name}' success={self.success}>"
