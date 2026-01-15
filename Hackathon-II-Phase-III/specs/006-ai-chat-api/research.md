# Research: AI Agent & Stateless Chat API

**Feature**: 006-ai-chat-api
**Date**: 2026-01-10

## Agents SDK: Tools + Context Passing

**Decision**: Use OpenAI Agents SDK `Agent` with function tools; pass a per-request context object containing `user_id`, JWT token, and a slice of conversation history.

**Rationale**:
- Agents SDK supports dependency injection via `Runner.run(..., context=...)` and `RunContextWrapper[T]` for tools.
- This matches statelessness: all context is constructed on-demand from the DB.

**Pattern (from Agents SDK docs)**:
- Define a dataclass context and pass it to `Runner.run()`.
- Tools can access `wrapper.context.<field>`.

## Tool Calling Determinism

**Decision**: Increase determinism by:
- Using strict tool schemas (typed inputs)
- Using a strong system prompt: "MUST use tools for task ops", "do not invent task IDs", "ask clarifying questions"
- Constraining responses to a fixed JSON envelope internally, then formatting a friendly user message

**Tradeoffs**:
- Cannot guarantee perfect determinism across all LLM randomness, but can improve practical consistency.

## MCP Server Invocation Option

**Decision**: Treat MCP server as a callable dependency from the API layer.

**Options Considered**:
1) Spawn MCP server subprocess per request (stdio)
   - Pros: simplest wiring
   - Cons: expensive; may violate latency goals
2) Run MCP server as a long-lived sidecar process and connect over stdio/pipe
   - Pros: better performance
   - Cons: additional operational complexity
3) Run MCP server as a separate service and connect over network
   - Pros: clear separation, scalable
   - Cons: requires additional deployment and service discovery

**Recommended for this phase**: Option 3 (separate service) OR Option 2 (sidecar), depending on your deployment setup.

## Existing Backend Auth Pattern

**Observed (codebase)**:
- JWT middleware sets `request.state.user_id` and rejects unauthenticated requests.
- Dependency `get_user_id_from_path` enforces route user_id matches authenticated user.

This should be reused for chat endpoint security.
