# Data Model: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Created**: 2026-01-19
**Source**: Derived from [spec.md](./spec.md) and [plan.md](./plan.md)

## Entity Definitions

### Conversation

Represents a chat session between a user and the AI agent.

**Attributes**:
- `id` (UUID, primary key): Unique conversation identifier
- `user_id` (UUID, foreign key → User.id, indexed): Owning user
- `title` (string, nullable, max 255 chars): Optional conversation title (e.g., "Task Management Session")
- `created_at` (datetime): Conversation creation timestamp
- `updated_at` (datetime): Last message timestamp

**Relationships**:
- Belongs to User (1:N - user can have multiple conversations)
- Has many Messages (1:N - conversation contains multiple messages)

**Validation Rules**:
- `user_id` required and must match authenticated JWT user
- `title` max 255 characters if provided
- `created_at` auto-generated on creation
- `updated_at` auto-updated on new message

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user-scoped queries
- Index on `created_at` for chronological sorting

**State Transitions**:
- Created when user sends first message (if no existing conversation)
- Updated timestamp on every new message (user or agent)
- No explicit "closed" state - conversations persist indefinitely

---

### Message

Represents a single message in a conversation (user or agent).

**Attributes**:
- `id` (UUID, primary key): Unique message identifier
- `conversation_id` (UUID, foreign key → Conversation.id, indexed): Parent conversation
- `role` (enum: 'user' | 'agent'): Message sender role
- `content` (text, required, max 5000 chars): Message text content
- `created_at` (datetime): Message creation timestamp

**Relationships**:
- Belongs to Conversation (N:1 - message belongs to one conversation)
- Has many ToolInvocations (1:N - message can trigger multiple tool calls)

**Validation Rules**:
- `conversation_id` required
- `role` must be 'user' or 'agent'
- `content` required, not empty, max 5000 characters
- `created_at` auto-generated on creation

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for conversation retrieval
- Index on `created_at` for chronological ordering

**State Transitions**:
- User messages created when user submits message
- Agent messages created after agent processes user message
- Immutable after creation (no edits or deletions)

---

### ToolInvocation

Audit log for agent tool calls during message processing.

**Attributes**:
- `id` (UUID, primary key): Unique invocation identifier
- `message_id` (UUID, foreign key → Message.id, indexed): Parent message that triggered tool call
- `tool_name` (enum: 'create_task' | 'list_tasks' | 'update_task' | 'delete_task'): MCP tool name
- `input_params` (JSON): Tool input parameters (serialized dict)
- `output_result` (JSON, nullable): Tool output result (serialized dict)
- `success` (boolean): Whether tool invocation succeeded
- `error_message` (text, nullable): Error description if failed
- `created_at` (datetime): Invocation timestamp

**Relationships**:
- Belongs to Message (N:1 - invocation belongs to one message)

**Validation Rules**:
- `message_id` required
- `tool_name` must be one of valid MCP tool names
- `input_params` required, valid JSON
- `output_result` required if `success=true`
- `error_message` required if `success=false`
- `created_at` auto-generated on creation

**Indexes**:
- Primary key on `id`
- Index on `message_id` for message audit trail
- Index on `created_at` for temporal queries

**State Transitions**:
- Created during agent message processing when tool is called
- Multiple invocations can be created per agent message
- Immutable after creation (audit log)

---

## Entity Relationships Diagram

```
User (existing Phase-II)
  │
  └─1:N─► Conversation
            │
            ├── id (PK)
            ├── user_id (FK)
            ├── title
            ├── created_at
            └── updated_at
            │
            └─1:N─► Message
                      │
                      ├── id (PK)
                      ├── conversation_id (FK)
                      ├── role (user/agent)
                      ├── content
                      └── created_at
                      │
                      └─1:N─► ToolInvocation
                                │
                                ├── id (PK)
                                ├── message_id (FK)
                                ├── tool_name
                                ├── input_params
                                ├── output_result
                                ├── success
                                ├── error_message
                                └── created_at
```

## Database Schema (SQLModel)

### Conversation Table

```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message Table

```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: str = Field(nullable=False)  # 'user' or 'agent'
    content: str = Field(nullable=False, max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### ToolInvocation Table

```python
class ToolInvocation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="message.id", index=True, nullable=False)
    tool_name: str = Field(nullable=False)  # create_task, list_tasks, update_task, delete_task
    input_params: str = Field(nullable=False)  # JSON string
    output_result: Optional[str] = Field(default=None)  # JSON string
    success: bool = Field(nullable=False)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Migration Strategy

**Alembic Migration Steps**:

1. Create migration: `alembic revision --autogenerate -m "Add conversation message toolinvocation tables"`
2. Generated migration creates 3 tables:
   - `conversation` with foreign key to `user`
   - `message` with foreign key to `conversation`
   - `toolinvocation` (or `tool_invocation`) with foreign key to `message`
3. Apply migration: `alembic upgrade head`

**Rollback Strategy**:
- Down migration drops tables in reverse order (toolinvocation → message → conversation)
- No impact on existing user/task tables from Phase-II

## Query Patterns

### Load Conversation with Messages

```python
# Get conversation for user
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
    .where(Conversation.user_id == user_id)
).first()

# Get all messages for conversation
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at)
).all()
```

### Create Message with Tool Invocation

```python
# Create agent message
agent_message = Message(
    conversation_id=conversation_id,
    role="agent",
    content=agent_response_text
)
session.add(agent_message)
session.flush()  # Get message.id

# Create tool invocation audit
invocation = ToolInvocation(
    message_id=agent_message.id,
    tool_name="create_task",
    input_params=json.dumps({"title": "Buy milk", "user_id": str(user_id)}),
    output_result=json.dumps({"id": str(task.id), "title": "Buy milk"}),
    success=True
)
session.add(invocation)
session.commit()
```

### Get User's Latest Conversation

```python
latest_conversation = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
    .limit(1)
).first()
```

## Notes

- All timestamps use UTC (datetime.utcnow)
- JSON fields stored as text, serialized with `json.dumps()` / `json.loads()`
- User isolation enforced at query level (always filter by user_id from JWT)
- Conversation history loaded in full per request (optimize later if >100 messages)
- No soft deletes - conversations and messages are immutable audit trail
