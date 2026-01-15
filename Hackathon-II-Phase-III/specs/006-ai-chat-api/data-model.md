# Data Model: Conversation Memory

**Feature**: 006-ai-chat-api
**Date**: 2026-01-10

## Conversation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Conversation identifier |
| `user_id` | UUID | Indexed, NOT NULL | Owner of conversation |
| `created_at` | DateTime | NOT NULL | Creation timestamp |
| `updated_at` | DateTime | NOT NULL | Updated timestamp |

## Message

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Message identifier |
| `conversation_id` | UUID | FK, Indexed, NOT NULL | Parent conversation |
| `role` | String | NOT NULL | "user" or "assistant" |
| `content` | Text | NOT NULL | Message content |
| `tool_calls_json` | JSON/Text | NULLABLE | Serialized tool calls and results (for audit/debug) |
| `created_at` | DateTime | NOT NULL | Timestamp |

## Relationships

- Conversation (1:N) → Message

## Indexes

- `idx_conversation_user_id` on `Conversation.user_id`
- `idx_message_conversation_id_created_at` on `(Message.conversation_id, Message.created_at)`

## Notes

- Conversation history reconstruction should fetch recent messages ordered by created_at.
- Use a capped history window (e.g., last N messages) to bound token usage.
