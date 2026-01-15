---
id: 1
title: Specify AI agent chat API
stage: spec
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-ai-chat-api
branch: 006-ai-chat-api
user: a
command: /sp.specify
labels: [spec, agent, chat, stateless, jwt, mcp]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-ai-chat-api/spec.md
  - specs/006-ai-chat-api/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.specify

Spec-6: AI Agent & Stateless Chat API

Specify the AI agent and chat interaction layer.
Define:
- OpenAI Agents SDK configuration
- Agent system prompt and behavior rules
- MCP tool registration and invocation
- Stateless chat endpoint: POST /api/{user_id}/chat
- Conversation persistence and reconstruction from database

Agent behavior rules:
- Agent must use MCP tools for all task operations
- Natural language mapped to tool calls deterministically
- Multiple tools may be chained in one turn if needed
- All actions must be confirmed in a friendly response
- Errors handled gracefully with clear explanations

Chat architecture rules:
- Server holds no in-memory conversation state
- Conversation history fetched from DB per request
- User messages and assistant responses persisted
- JWT authentication required for all chat requests
- Authenticated user ID must match route user_id

Out of scope:
- MCP tool implementation
- Chat frontend UI

Acceptance criteria:
- Agent correctly selects and invokes MCP tools
- Chat endpoint remains fully stateless
- Conversation resumes correctly after restart
- Unauthorized access is rejected
 @switch

## Response snapshot

Created feature branch `006-ai-chat-api` and drafted `specs/006-ai-chat-api/spec.md` covering user stories (P1 chat-to-manage-tasks, P2 resume after restart), edge cases, functional requirements, entities (Conversation, Message), and measurable success criteria. Added and completed a spec-quality checklist at `specs/006-ai-chat-api/checklists/requirements.md` and revised requirements language to treat OpenAI Agents SDK + MCP and the chat route path as governance constraints.

## Outcome

- ✅ Impact: Spec established for stateless chat endpoint and agent tooling constraints.
- 🧪 Tests: none
- 📁 Files: spec.md, requirements checklist
- 🔁 Next prompts: /sp.plan to design persistence, contracts, and agent/tool wiring.
- 🧠 Reflection: Determinism must be approached as a practical constraint (strict schemas + prompting), not an absolute guarantee.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
