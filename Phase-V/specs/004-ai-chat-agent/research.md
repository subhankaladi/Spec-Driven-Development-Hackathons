# Research: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Created**: 2026-01-19
**Phase**: 0 (Outline & Research)

## Research Objectives

1. Determine how to integrate OpenAI Agents SDK with FastAPI in stateless mode
2. Define MCP tool implementation approach compatible with OpenAI SDK
3. Design conversation persistence strategy for stateless architecture
4. Evaluate frontend chat UI options and integration patterns

## R001: OpenAI Agents SDK Integration Patterns

### Research Question
How can we integrate OpenAI Agents SDK with FastAPI while maintaining stateless operation and rebuilding conversation context from database on each request?

### Findings

**OpenAI Agents SDK Capabilities**:
- Supports loading conversation history from external storage (list of messages)
- Agent can be instantiated per-request without maintaining in-memory state
- SDK provides built-in tool/function calling mechanism
- Compatible with stateless architectures through message history replay

**Integration Pattern**:
```python
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

# Load conversation history from database
messages = load_messages_from_db(conversation_id)

# Convert to OpenAI message format
openai_messages = [
    {"role": msg.role, "content": msg.content}
    for msg in messages
]

# Add new user message
openai_messages.append({"role": "user", "content": user_message})

# Call agent with tools
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=openai_messages,
    tools=mcp_tools,  # Registered MCP tools
    tool_choice="auto"
)
```

### Decision

**Use OpenAI Agents SDK in stateless mode with conversation history passed as context**

### Rationale

- SDK supports loading external conversation history (no in-memory state required)
- Agent can be instantiated per-request, aligning with stateless architecture
- Built-in tool calling mechanism simplifies MCP tool integration
- Official SDK is reliable and well-documented

### Alternatives Considered

1. **LangChain**: More complex abstraction layer, overkill for single-agent use case, adds unnecessary dependencies
2. **Custom agent implementation**: Reinventing wheel, less reliable than official SDK, requires manual tool calling logic
3. **Persistent agent instances**: Violates Principle VII (statelessness), doesn't support horizontal scaling or crash recovery

### Best Practices

- Pass full conversation history on each request (optimize later with message windowing if needed)
- Use system prompt to define agent behavior and available tools
- Validate tool responses before persisting to database
- Handle SDK errors gracefully with fallback responses
- Set reasonable timeout values (3-5 seconds)
- Log all agent interactions for debugging and auditing

### Implementation Notes

- Conversation history format: `[{"role": "user|agent", "content": "text"}, ...]`
- System prompt defines agent personality and task management domain expertise
- Tool responses are JSON that agent includes in conversational response
- Agent instance created per request, no shared state between requests

---

## R002: MCP Tool Definition and Integration

### Research Question
What is the best approach to implement MCP tools that integrate with OpenAI Agents SDK while maintaining statelessness and user isolation?

### Findings

**MCP SDK Requirements**:
- Tools defined with JSON schemas (input/output validation)
- Tools must be stateless functions (deterministic given inputs)
- Official MCP SDK provides schema validation and serialization
- Compatible with OpenAI function calling API

**OpenAI Function Calling Format**:
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Optional description"}
                },
                "required": ["title"]
            }
        }
    }
]
```

**Tool Execution Pattern**:
```python
# Agent returns tool calls in response
tool_calls = response.choices[0].message.tool_calls

for tool_call in tool_calls:
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    # Execute MCP tool
    result = execute_mcp_tool(tool_name, tool_args, user_id)

    # Log invocation
    log_tool_invocation(message_id, tool_name, tool_args, result)
```

### Decision

**Implement MCP tools as Python functions with JSON schema validation, registered with OpenAI agent via function calling API**

### Rationale

- Python functions integrate naturally with existing FastAPI codebase (no separate server needed)
- Official MCP SDK provides schema definition and validation utilities
- OpenAI function calling API is well-documented and stable
- In-process function calls avoid network overhead and simplify deployment
- Type safety through Pydantic models and JSON schemas

### Alternatives Considered

1. **Separate MCP server**: Over-engineered for 4 simple tools, adds deployment complexity and network latency
2. **Direct database access by agent**: Violates Principle VIII, bypasses validation and logging, creates tight coupling
3. **REST API calls**: Unnecessary network overhead for in-process calls, complicates error handling

### Best Practices

- Define explicit JSON schemas for all tool inputs and outputs
- Tools are pure functions (no side effects except database writes via service layer)
- Each tool validates `user_id` matches authenticated user from JWT
- Log all tool invocations to `ToolInvocation` table for traceability and debugging
- Return structured errors instead of throwing exceptions
- Use service layer for database operations (tools call `task_service.create_task()`, not direct DB access)

### Implementation Notes

**Tool Structure**:
```python
# src/services/mcp_tools.py

def create_task(title: str, description: Optional[str], user_id: UUID) -> dict:
    """MCP tool: Create new task"""
    # Validate user_id matches authenticated user (passed from endpoint)
    # Call task_service.create_task(...)
    # Return structured result
    return {"id": str(task.id), "title": task.title, ...}
```

**Tool Registration**:
- Tools registered as OpenAI function definitions in `agent_service.py`
- Agent receives tool list on each request (stateless)
- Tool execution happens after agent response, results logged to database

---

## R003: Conversation Persistence Strategy

### Research Question
How should we persist conversations and messages to enable stateless architecture with seamless conversation resumption?

### Findings

**Persistence Requirements** (from Principle VII):
- Agent rebuilds conversation context from database on every request
- No in-memory conversation state cached between requests
- All messages persisted immediately after processing
- Conversation resumption must work after application restart

**Database Design Options**:

1. **Write-through on every message**: Insert to DB immediately, load full history per request
2. **Event sourcing**: Store events and rebuild state (overkill for MVP)
3. **Redis cache with DB backup**: Adds complexity, risk of cache/DB inconsistency
4. **Lazy persistence**: Batch writes (violates Principle VII)

**Performance Considerations**:
- Neon PostgreSQL handles <100 messages per conversation efficiently
- Query time for conversation + messages: <100ms
- Index on `conversation_id` and `created_at` for fast chronological retrieval
- Transaction ensures atomicity (user message + agent message + tool invocations)

### Decision

**Store conversations and messages in PostgreSQL with immediate write-through on every message**

### Rationale

- Guarantees data durability and enables stateless architecture (no in-memory cache)
- Existing Neon PostgreSQL connection from Phase-II (no new infrastructure)
- Simple schema extension (2 new tables: `conversation`, `message`)
- Query performance acceptable for <100 messages per conversation (<100ms)
- Atomic transactions ensure consistency (all-or-nothing writes)

### Alternatives Considered

1. **Redis cache**: Adds complexity, risk of data loss on crash, violates durability guarantee
2. **Event sourcing**: Over-engineered for MVP, adds development time and complexity
3. **Lazy persistence with batch writes**: Violates Principle VII (immediate persistence required), risks data loss

### Best Practices

- Load conversation and all messages in single query with JOIN (minimize round trips)
- Insert messages immediately after agent response (no batching or delayed writes)
- Use database transactions to ensure atomicity of multi-message operations
- Index on `user_id`, `conversation_id`, `created_at` for efficient queries
- Limit conversation history to last 50-100 messages if performance degrades (optimize later)
- Store tool invocations separately for audit trail (don't bloat message content)

### Implementation Notes

**Write Flow**:
1. User sends message → insert to `message` table with `role='user'`
2. Agent processes → insert to `message` table with `role='agent'`
3. Tool invocations → insert to `tool_invocation` table (linked to agent message)
4. Update `conversation.updated_at` timestamp
5. Commit transaction (all writes succeed or all fail)

**Read Flow**:
1. Load conversation by ID (verify `user_id` matches JWT)
2. Load all messages for conversation ordered by `created_at`
3. Convert to OpenAI message format for agent
4. Return full history to frontend for display

---

## R004: Frontend Chat UI Integration

### Research Question
What is the best approach to build the frontend chat interface that integrates with the chat API and existing Phase-II authentication?

### Findings

**Frontend Requirements**:
- Display conversation history in chronological order
- Distinguish user vs agent messages visually
- Send messages to chat API with JWT authentication
- Show loading state while agent processes
- Handle API errors gracefully
- Auto-scroll to latest message

**UI Library Options**:

1. **Custom React components**: Full control, consistent with Phase-II, simple MVP requirements
2. **Pre-built chat library** (ChatKit, Stream Chat): Overkill, vendor lock-in, configuration overhead
3. **WebSocket/SSE for real-time updates**: Not needed for MVP (no streaming responses)

**Integration Pattern**:
```typescript
// Custom hook for chat API
const useChat = (conversationId: string | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (content: string) => {
    setLoading(true);
    const response = await chatApi.sendMessage(conversationId, content);
    setMessages([...messages, userMessage, agentMessage]);
    setLoading(false);
  };

  return { messages, loading, sendMessage };
};
```

### Decision

**Build custom chat component using existing Next.js/React patterns from Phase-II frontend**

### Rationale

- Consistent with existing Phase-II UI architecture (Next.js, React, Tailwind)
- Full control over UI/UX without vendor lock-in
- Reuse existing authentication and API client patterns (Axios with JWT)
- Simple MVP requirements don't justify third-party library complexity
- Easy to extend with additional features later

### Alternatives Considered

1. **Pre-built chat UI library** (ChatKit, Stream Chat): Overkill for simple text chat, vendor lock-in, additional dependencies, configuration overhead
2. **WebSocket real-time updates**: Not required for MVP (no streaming responses), adds complexity to backend and frontend
3. **Server-sent events (SSE)**: Not needed without streaming agent responses, complicates error handling

### Best Practices

- Display messages in chronological order with clear user/agent distinction (e.g., different background colors)
- Show loading spinner/indicator while agent processes message (disable input during processing)
- Handle API errors with user-friendly error messages (toast notifications or inline alerts)
- Auto-scroll to latest message when new message arrives
- Load conversation history on page load and display immediately
- Persist conversation ID in URL or component state for page refreshes
- Use optimistic UI updates (show user message immediately, wait for agent response)
- Validate message content before sending (not empty, max length)

### Implementation Notes

**Component Structure**:
```
ChatInterface (page)
├── MessageList (scrollable container)
│   └── MessageBubble (individual message)
│       ├── UserMessage (right-aligned, blue bg)
│       └── AgentMessage (left-aligned, gray bg)
└── MessageInput (textarea + send button)
```

**API Integration**:
- Use existing Axios client with JWT interceptor from Phase-II
- POST `/chat` endpoint with `{conversation_id, message}`
- Parse response and append agent message to conversation
- Display tool invocation results if available (optional for MVP)

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| **OpenAI SDK Integration** | Stateless mode with history replay | Supports stateless architecture, official SDK reliability |
| **MCP Tools** | In-process Python functions | Simplicity, performance, type safety, no separate server |
| **Conversation Persistence** | PostgreSQL write-through | Durability guarantee, existing infrastructure, acceptable performance |
| **Frontend UI** | Custom React components | Consistency with Phase-II, full control, simple requirements |

## Resolved Clarifications

All technical unknowns from plan.md Technical Context have been researched and resolved:

- ✅ OpenAI SDK integration approach defined
- ✅ MCP tool implementation pattern established
- ✅ Conversation persistence strategy decided
- ✅ Frontend UI approach selected

## Next Steps

1. ✅ Phase 0 complete - all research findings documented
2. ⏭️ Phase 1 complete - data model, contracts, quickstart generated
3. ⏭️ Run `/sp.tasks` to break down implementation into executable tasks
4. ⏭️ Implement using specialized agents (Backend, Database, Frontend)
