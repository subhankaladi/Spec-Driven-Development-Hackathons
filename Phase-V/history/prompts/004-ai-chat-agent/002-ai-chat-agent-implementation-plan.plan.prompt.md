---
id: 002
title: AI Chat Agent Implementation Plan
stage: plan
date: 2026-01-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-ai-chat-agent
branch: 004-ai-chat-agent
user: a
command: /sp.plan
labels: ["planning", "ai-agent", "architecture", "stateless-design", "mcp-tools"]
links:
  spec: specs/004-ai-chat-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-ai-chat-agent/plan.md
 - specs/004-ai-chat-agent/research.md
 - specs/004-ai-chat-agent/data-model.md
 - specs/004-ai-chat-agent/contracts/chat-api.yaml
 - specs/004-ai-chat-agent/contracts/mcp-tools.json
 - specs/004-ai-chat-agent/quickstart.md
tests:
 - Contract tests defined in chat-api.yaml
 - Integration test patterns documented in plan.md
---

## Prompt

before planing first you can review the frontend and backend folder after that generate plan here is plan: /sp.plan

- Define agent prompt and behavior
- Build stateless chat API endpoint
- Persist conversations and messages
- Connect ChatKit frontend to chat API
- Validate tool calls and responses

## Response snapshot

Completed comprehensive implementation planning for AI Chat Agent & Integration feature after reviewing existing Phase-II backend (FastAPI, SQLModel, Neon PostgreSQL, JWT auth) and frontend (Next.js 16, React 19, Axios) architecture.

**Phase 0 Research Completed** (4 research areas):
1. **OpenAI Agents SDK Integration** - Decided on stateless mode with conversation history replay from database
2. **MCP Tool Implementation** - In-process Python functions with JSON schema validation (no separate MCP server)
3. **Conversation Persistence** - PostgreSQL write-through strategy for immediate durability
4. **Frontend Chat UI** - Custom React components consistent with Phase-II architecture

**Phase 1 Design Completed**:
- **Data Model** (3 new entities):
  - Conversation: Chat session (id, user_id, title, timestamps)
  - Message: Individual messages (id, conversation_id, role, content, created_at)
  - ToolInvocation: Audit log (id, message_id, tool_name, input, output, success, created_at)

- **API Contracts**:
  - Chat endpoint: `POST /chat` with JWT auth, stateless operation
  - 4 MCP tools: create_task, list_tasks, update_task, delete_task
  - Complete OpenAPI spec and MCP tool JSON schemas

- **Architecture Decisions**:
  - Stateless agent: Rebuild context from DB on every request (no in-memory cache)
  - MCP tools as service layer functions (not direct DB access)
  - Single conversation per user initially (multi-conversation future enhancement)
  - Frontend chat component with message bubbles and input field

**Constitution Check**: ✅ ALL 8 PRINCIPLES PASS
- Principle VII (Statelessness): Context rebuilt from DB per request
- Principle VIII (MCP Tool-First): All task ops via MCP tools, no direct DB access

**Key Architectural Decisions Requiring ADRs**:
1. Stateless Agent with Database-Backed Context
2. MCP Tools as In-Process Python Functions
3. Single Conversation Per User

**Project Structure**:
- Backend adds: conversation.py, message.py, mcp_tools.py, agent_service.py, conversation_service.py, chat.py route
- Frontend adds: chat/ page, ChatInterface, MessageList, MessageBubble, MessageInput components, useChat hook

**Performance Goals Met**:
- Agent response: <3s simple, <5s complex
- Conversation load: <1s
- Database ops: <500ms per query

Planning complete and ready for `/sp.tasks` to generate task breakdown.

## Outcome

- ✅ Impact: Complete implementation plan with all phases (0: Research, 1: Design) documented, architecture validated against constitution
- 🧪 Tests: Defined contract tests in OpenAPI spec, integration test patterns in plan.md
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, 2 contracts, quickstart.md)
- 🔁 Next prompts: Ready for `/sp.tasks` to break down into executable tasks organized by user story
- 🧠 Reflection: Stateless architecture thoroughly designed - conversation persistence strategy ensures durability, MCP tool-first approach maintains separation of concerns, frontend integration reuses Phase-II patterns

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with constitution compliance verified
- Graders run and results (PASS/FAIL): Constitution Check PASS - all 8 principles satisfied by design
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate task breakdown with `/sp.tasks`, prioritizing P1 (Create Task) user story for MVP delivery
