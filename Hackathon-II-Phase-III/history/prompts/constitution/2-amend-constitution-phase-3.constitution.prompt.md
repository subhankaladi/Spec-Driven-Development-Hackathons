---
id: 2
title: Amend constitution for Phase III AI Chatbot
stage: constitution
date: 2026-01-10
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 004-frontend-integration
user: a
command: /sp.constitution
labels: [constitution, phase-3, ai, mcp, stateless]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution

Project Update: Phase III — AI-Powered Todo Chatbot

Added principles:
- Natural language as a first-class interface
- Tool-driven AI (agents act only via MCP tools)
- Fully stateless server architecture
- Database-backed conversation memory

Added standards:
- AI logic implemented using OpenAI Agents SDK
- Task operations exposed via Official MCP SDK
- Agents must invoke MCP tools for all task actions
- MCP tools are stateless and deterministic
- Conversation state persisted in PostgreSQL

Added constraints:
- Single chat endpoint: POST /api/{user_id}/chat
- JWT authentication required for chat requests
- User identity enforced on every tool invocation
- No in-memory conversation state allowed

Success criteria:
- Users manage todos via natural language
- AI reliably selects correct MCP tools
- Conversations resume after server restart
- System remains secure, stateless, and scalable

## Response snapshot

Amended the constitution to version 1.1.0, incorporating the Phase III requirements for an AI-powered Todo Chatbot. The update mandates the use of the OpenAI Agents SDK, the Official MCP SDK for tool-driven AI, and strict statelessness with database-backed conversation memory. The Sync Impact Report and PHR have been recorded.

## Outcome

- ✅ Impact: High - Redefines the core implementation path for Phase III using AI Agents and MCP.
- 🧪 Tests: none
- 📁 Files: Updated constitution.md
- 🔁 Next prompts: /sp.specify for the Chatbot features.
- 🧠 Reflection: The transition to AI-centric development requires clear guardrails on tool execution and identity enforcement.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
