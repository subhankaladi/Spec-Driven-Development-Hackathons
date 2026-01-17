---
id: 002
title: Update constitution Phase III AI chatbot
stage: constitution
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-mcp-server-todo-tooling
user: a
command: /sp.constitution
labels: ["constitution", "phase-3", "ai-chatbot", "mcp", "openai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitutional document update)
---

## Prompt

```text
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
```

## Response snapshot

Constitution updated to version 1.1.0 with Phase III AI-Powered Todo Chatbot principles.

**Added Principles**:
- **VII. Natural Language as First-Class Interface**: Users must be able to manage todos through natural language conversation. AI chatbot is a primary interface, not an add-on.
- **VIII. Tool-Driven AI Architecture**: AI agents must act exclusively via MCP tools. No direct database/API access. Clean separation between AI reasoning and system actions.
- **IX. Fully Stateless Server Architecture**: Backend must not maintain in-memory conversation state. All history persisted in PostgreSQL. Conversations resume after server restart.
- **X. User Identity Enforcement at Tool Level**: Every MCP tool invocation must verify user identity via JWT. Defense in depth security at tool layer.

**Technology Stack Updates**:
- Added: OpenAI Agents SDK (AI Framework)
- Added: Official MCP SDK (Tool Protocol)

**Development Workflow Updates**:
- Added Phase 5: AI Integration workflow with 8 steps covering MCP tool definition, OpenAI integration, conversation persistence, and testing

**Quality Standards Updates**:
- Added AI Requirements section with 6 requirements for tool invocation, statelessness, persistence, and natural language mapping
- Enhanced Security Requirements with Phase III tool-level user validation
- Enhanced Testing Requirements with MCP tool tests, AI conversation tests, and persistence tests

**Version Bump Rationale**: MINOR (1.0.0 → 1.1.0) - New principles added, backward compatible with Phases I & II.

**Templates Validated**:
- ✅ plan-template.md - Constitution Check section will validate new principles
- ✅ spec-template.md - User Scenarios support natural language stories
- ✅ tasks-template.md - Can organize AI/MCP tasks by user story
- ✅ README.md - No conflicts with Phase III

## Outcome

- ✅ Impact: Constitution successfully amended with 4 new Phase III principles (VII-X). All Phase I & II principles retained for backward compatibility.
- 🧪 Tests: No tests required (constitutional document, not code)
- 📁 Files: Modified `.specify/memory/constitution.md` (version 1.0.0 → 1.1.0)
- 🔁 Next prompts: Ready for Phase III feature specification (/sp.specify) to define AI chatbot user stories and requirements
- 🧠 Reflection: Principles clearly articulated with rationales. Stateless architecture, tool-driven AI, and defense-in-depth security align with modern best practices. Natural language interface positions project as modern productivity tool.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update followed proper amendment procedure with version increment, sync impact report, and template validation.
- Graders run and results (PASS/FAIL): N/A (constitutional document)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to Phase III feature specification to translate principles into user stories and functional requirements
