# Data Model: AI Agent & Stateless Chat API

**Feature**: 006-ai-agent-chat-api
**Created**: 2026-01-16
**Status**: Design Complete

## Entity Relationship Diagram

```
User (existing)
├── 1:N Conversation
│   ├── 1:N Message
│   │   └── Properties: role, content, tool_calls
│   └── Metadata: title, created_at, updated_at
├── 1:N Task (existing)
└── 1:N Message (as sender)
```

---

## Entity Specifications

### 1. Conversation

Represents a chat session between user and agent.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """Chat conversation between user and agent."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="Owner of conversation (FK to User)"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User-provided conversation name"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation started"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last message timestamp"
    )

    # Relationships
    messages: list["Message"] = Field(default_factory=list, back_populates="conversation")
```

**Validation Rules**:
- `user_id`: Must reference existing User (FK constraint)
- `title`: Max 255 characters, optional
- `created_at` / `updated_at`: ISO 8601 format, UTC timezone
- No duplicate conversations for same user (handled by application logic)

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` (for user-scoped queries)
- Composite: `(user_id, updated_at DESC)` (for conversation list sorting)

**State Transitions**:
- Created: On first message from user
- Active: Receiving messages
- Archived: After 90 days without updates (optional, for cleanup)

---

### 2. Message

Individual message in a conversation.

**SQLModel Definition**:
```python
from enum import Enum
from typing import Optional, Any

class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    """Individual message in conversation."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="conversation.id",
        description="Parent conversation (FK)"
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="user.id",
        description="Message sender"
    )
    role: MessageRole = Field(
        nullable=False,
        description="Message source: 'user' or 'assistant'"
    )
    content: str = Field(
        nullable=False,
        min_length=1,
        max_length=50000,
        description="Message text content"
    )
    tool_calls: Optional[dict[str, Any]] = Field(
        default=None,
        description="MCP tools invoked (agent messages only)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When message was sent"
    )

    # Relationships
    conversation: Conversation = Field(back_populates="messages")
```

**Validation Rules**:
- `conversation_id`: Must reference existing Conversation
- `user_id`: Must reference existing User AND match conversation.user_id
- `role`: Must be "user" or "assistant" (enum validated)
- `content`: 1-50000 characters, non-empty
- `tool_calls`: JSON structure for tools invoked (optional, only for assistant messages)

**Tool Calls Structure**:
```json
{
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "buy groceries", "description": null},
      "result": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "buy groceries",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "is_completed": false,
        "created_at": "2026-01-16T12:00:00Z"
      }
    }
  ]
}
```

**Indexes**:
- Primary: `id`
- Foreign Key: `conversation_id` (for conversation history)
- Foreign Key: `user_id` (for user isolation)
- Composite: `(conversation_id, created_at ASC)` (for message ordering)

---

### 3. Task (Existing, Reference)

Used by agent via MCP tools only. No direct access from chat API.

**Read-Only Reference**:
```python
class Task(SQLModel, table=True):
    """Task entity (existing schema)."""

    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = None
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
```

**Chat API Access**: Via MCP tools only (add_task, list_tasks, complete_task, update_task, delete_task)

---

### 4. User (Existing, Reference)

Existing user entity from authentication system.

**Reference**:
```python
class User(SQLModel, table=True):
    """User entity (existing schema)."""

    id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, max_length=255)
    password_hash: str
    created_at: datetime
    updated_at: datetime
```

**Chat API Access**: Via JWT token validation (extract user_id from `sub` claim)

---

## Data Flow & Relationships

### Conversation Creation Flow
```
1. User sends POST /api/chat with message
2. API validates JWT → extract user_id
3. If conversation_id not provided:
   - Create new Conversation(user_id=extracted_user_id)
   - Set conversation_id in response
4. Persist user message to Message table
5. Call agent service
6. Persist agent response to Message table
7. Update Conversation.updated_at
8. Return both messages in response
```

### Conversation History Retrieval
```
1. User sends GET /api/chat/{conversation_id}
2. API validates JWT → extract user_id
3. Query: SELECT * FROM Conversation WHERE id={conversation_id} AND user_id={user_id}
4. If not found: return 404 (or 403 if unauthorized)
5. Query: SELECT * FROM Message WHERE conversation_id={conversation_id} ORDER BY created_at ASC
6. Return Conversation + paginated Messages
```

### User Isolation
```
- Conversation: WHERE user_id = authenticated_user_id
- Message: WHERE user_id = authenticated_user_id AND conversation_id IN (user's conversations)
- Task: Via MCP tools with JWT validation
```

---

## Query Patterns

### P1: List User's Conversations (Recent First)
```sql
SELECT * FROM conversation
WHERE user_id = {user_id}
ORDER BY updated_at DESC
LIMIT 50;
```
**Index**: (user_id, updated_at DESC)

### P2: Get Conversation History
```sql
SELECT * FROM message
WHERE conversation_id = {conversation_id} AND user_id = {user_id}
ORDER BY created_at ASC;
```
**Index**: (conversation_id, created_at ASC)

### P3: Search Conversations by Title
```sql
SELECT * FROM conversation
WHERE user_id = {user_id} AND title ILIKE %{search_term}%
ORDER BY updated_at DESC;
```
**Index**: (user_id, updated_at DESC) + Full-text search (optional)

### P4: Cleanup Old Conversations (90+ days)
```sql
DELETE FROM conversation
WHERE user_id = {user_id} AND updated_at < NOW() - INTERVAL '90 days';
```
**Index**: (updated_at)

---

## Database Constraints

### Foreign Keys
- `Conversation.user_id` → `User.id` (CASCADE DELETE)
- `Message.conversation_id` → `Conversation.id` (CASCADE DELETE)
- `Message.user_id` → `User.id` (CASCADE DELETE)

### Unique Constraints
- None (allow multiple conversations per user)

### Check Constraints
- `Message.role` IN ('user', 'assistant')
- `Message.content` LENGTH > 0
- `Conversation.title` LENGTH <= 255

---

## Migration Strategy

### New Tables
```sql
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_user_updated (user_id, updated_at DESC)
);

CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_user_id (user_id),
    INDEX idx_conv_created (conversation_id, created_at ASC)
);
```

### Backward Compatibility
- No changes to existing tables (User, Task)
- Purely additive: new tables only
- Existing APIs unaffected
- Can deploy with feature flag to control chat endpoint availability

---

## Performance Considerations

### Query Performance
- Conversation list: O(log n) via index on (user_id, updated_at)
- Message retrieval: O(log n) via index on (conversation_id, created_at)
- User isolation: enforced via WHERE clause on user_id

### Storage Considerations
- Message content: average 100-500 bytes
- Tool calls JSON: 500-2000 bytes (optional)
- 1000 conversations × 100 messages × 1KB average = 100MB per user (acceptable)

### Cleanup Strategy
- Conversations older than 90 days: soft archive (optional)
- Hard delete: after 1 year (data retention policy)
- Cron job: daily cleanup for archived conversations

---

## Testing Approach

### Unit Tests
- Conversation creation with user isolation
- Message persistence and retrieval
- Validation rules enforcement

### Integration Tests
- Full chat flow: message → agent → persistence → retrieval
- User isolation: verify users can't access others' conversations
- Authorization: verify JWT validation

### Performance Tests
- Retrieve conversation history (50+ messages): <500ms
- List user conversations: <200ms
- Conversation creation: <1s (includes agent processing)
