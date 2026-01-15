<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles:
  - Security-First Design → Security & Statelessness
  - Full-Stack Architecture Standards → Stack & Logic (AI-Centric)
- Added sections:
  - Technology Stack Requirements (updated with OpenAI Agents SDK, Chat Endpoint)
  - Principles: Natural Language Interface, Tool-driven AI (MCP), Stateless Server, DB-backed Memory
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/memory/constitution.md (updated)
  - ⚠ .specify/templates/plan-template.md (requires manual alignment of "Constitution Check" examples)
- Follow-up TODOs: Ensure all new AI logic uses the OpenAI Agents SDK as per the new mandate.
-->
# AI-Powered Todo Chatbot Constitution

## Core Principles

### Spec-Driven Development (NON-NEGOTIABLE)
All development follows the spec → plan → tasks → implementation workflow; Specifications must be complete and approved before any coding begins; Every feature must have corresponding test cases defined in the tasks document before implementation.

### Natural Language as a First-Class Interface
The system primary user interaction is through natural language; Human-computer interaction must be intuitive, conversational, and accessible; The chatbot must handle complex intent parsing and multi-turn dialogues effectively.

### Tool-driven AI (MCP)
Agents must act exclusively via Model Context Protocol (MCP) tools; No direct side effects allowed from the AI model itself; Every external action (DB, API, System) must be encapsulated in a tool call for auditability and safety.

### Fully Stateless Server Architecture
The server must not hold any session or conversation state in memory; All state required for a request must be passed in the request or retrieved from the database; Ensures horizontal scalability and resilience.

### Database-backed Conversation Memory
Conversation history and context must be persisted in PostgreSQL; The system remains fully stateless while providing deep contextual continuity; Conversations must be resumable across server restarts or different worker nodes.

### Zero Manual Coding
Implementation must be achieved exclusively through Claude Code and automated tools; No hand-written code modifications allowed during the development phase; All changes must be traceable through the agentic development workflow.

### Security & Statelessness
JWT authentication must be enforced on every API route; User identity must be strictly enforced on every tool invocation; No in-memory conversation state allowed to prevent cross-user data leakage.

### Deterministic and Reproducible Outputs
Every development step must produce consistent, repeatable results; All environment configurations must be version-controlled and reproducible; Build and deployment processes must be idempotent and deterministic.

### Stack & Logic (AI-Centric)
AI logic must be implemented using the OpenAI Agents SDK; Task operations must be exposed via the Official MCP SDK; MCP tools must be stateless and deterministic; Backend uses FastAPI + SQLModel + Neon.

## Technology Stack Requirements

- **AI Logic**: OpenAI Agents SDK for orchestration and reasoning
- **Task Interface**: Official MCP SDK for exposing system/data capabilities
- **Backend**: Python FastAPI with SQLModel ORM (fully stateless)
- **Database**: Neon Serverless PostgreSQL (Conversation & Task Storage)
- **Authentication**: JWT-based authentication required for all requests
- **API Design**: Single chat endpoint: `POST /api/{user_id}/chat`
- **Environment**: All auth secrets and IDs must be shared via environment variables

## Development Workflow

- All code must be generated through Claude Code commands (e.g., /sp.specify, /sp.plan, /sp.tasks, /sp.implement)
- Specifications must be reviewed and approved before planning
- AI agents must be restricted to tool-based interactions verified against user identity
- Every tool invocation must validate the `user_id` from the JWT context
- All production logic changes must follow the red-green-refactor cycle with proper testing

## Governance

This constitution governs all development activities for the AI-Powered Todo Chatbot; All team members must comply with these principles; Amendments require explicit documentation and approval through the `/sp.constitution` command; Version control and audit trails must be maintained for all changes.

**Version**: 1.1.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2026-01-10
