---
id: 002
title: Create MCP server implementation plan
stage: plan
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: mcp-server-todo-tooling
branch: 005-mcp-server-todo-tooling
user: a
command: /sp.plan
labels: ["plan", "mcp", "tools", "phase-3", "mcp-sdk"]
links:
  spec: /mnt/c/Users/a/Desktop/phase-3/specs/005-mcp-server-todo-tooling/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-mcp-server-todo-tooling/plan.md
  - specs/005-mcp-server-todo-tooling/data-model.md
  - specs/005-mcp-server-todo-tooling/quickstart.md
  - specs/005-mcp-server-todo-tooling/contracts/add_task.json
  - specs/005-mcp-server-todo-tooling/contracts/list_tasks.json
  - specs/005-mcp-server-todo-tooling/contracts/update_task.json
  - specs/005-mcp-server-todo-tooling/contracts/complete_task.json
  - specs/005-mcp-server-todo-tooling/contracts/delete_task.json
tests:
  - None (planning document)
---

## Prompt

```text
/sp.plan before planning make sure that you have context7 mcp server for getting official docs to make better plan Now plan: - Initialize MCP server using Official MCP SDK
- Define MCP tool interfaces and schemas
- Implement tool handlers backed by SQLModel
- Enforce JWT-based user validation per tool
- Ensure all tools are stateless and database-driven
- Validate tool behavior with example inputs/outputs
```

## Response snapshot

Created comprehensive implementation plan for MCP Server & Todo Tooling feature, including research findings from Official MCP Python SDK documentation via Context7.

**Phase 0: Research Completed** (5 research tasks embedded in plan):
1. **MCP SDK Low-Level Server API**: Use `mcp.server.lowlevel.Server` with decorator-based handlers for precise control
2. **Lifespan Context for DB Pooling**: Use lifespan context manager to initialize connection pool at startup, session-per-invocation
3. **JWT Token Validation**: Pass JWT as tool argument, validate using existing `BetterAuthIntegration` class, extract user_id from `sub` claim
4. **Structured Error Responses**: Return TextContent with JSON error objects matching existing FastAPI error format
5. **Async SQLModel Integration**: Import existing Task/User models, use AsyncSession with async queries

**Phase 1: Design & Contracts Completed**:
1. **data-model.md**: Comprehensive tool schemas, data flow diagrams, authentication patterns, error handling matrix
2. **contracts/**: 5 JSON schema files (add_task, list_tasks, update_task, complete_task, delete_task) with input/output schemas
3. **quickstart.md**: Developer onboarding guide with installation, testing, development workflow, troubleshooting

**Technical Context Defined**:
- Language: Python 3.11+
- Dependencies: mcp (Official SDK), sqlmodel, pyjwt, bcrypt, asyncio
- Storage: Neon Serverless PostgreSQL (shared with backend)
- Testing: pytest with async support
- Performance: <500ms queries, <50ms auth rejection, <3s startup
- Structure: Standalone `mcp-server/` directory at repo root

**Constitution Check**: ✅ ALL 10 PRINCIPLES PASSED
- Spec-driven development ✅
- Agentic workflow compliance ✅
- Security-first design ✅
- Deterministic behavior ✅
- Full-stack coherence ✅
- Traceability ✅
- Natural language interface ✅ (enables Phase III AI chat)
- Tool-driven AI architecture ✅ (this IS the tool layer)
- Stateless server architecture ✅
- User identity at tool level ✅

**Project Structure Decision**: Create standalone `mcp-server/` directory separate from `backend/`, import shared models/auth utilities to avoid duplication. No changes to existing backend code required.

**Key Design Patterns**:
- Low-level MCP API with async handlers
- Lifespan context for connection pooling
- JWT validation before every database operation
- User-scoped queries (WHERE user_id = ?)
- Structured I/O with JSON Schema validation
- Consistent error responses
- Session-per-invocation (stateless)

**MCP SDK Documentation Fetched**:
- Official Python SDK: `/modelcontextprotocol/python-sdk`
- Low-level server examples with decorators
- Lifespan management patterns
- Structured tool schemas with input/output validation
- Error handling best practices
- Async database integration examples

## Outcome

- ✅ Impact: Comprehensive implementation plan with embedded research, complete design artifacts, and developer documentation ready for `/sp.tasks` task breakdown
- 🧪 Tests: No tests (planning phase - tests defined in spec and plan for implementation phase)
- 📁 Files: Created plan.md (research + technical context), data-model.md (15+ pages), 5 contract JSON schemas, quickstart.md (developer guide)
- 🔁 Next prompts: Ready for `/sp.tasks` to generate implementation task breakdown organized by user story
- 🧠 Reflection: Successfully fetched and incorporated official MCP SDK documentation via Context7. All research unknowns resolved with proven patterns from SDK examples. Plan provides clear implementation path with low-level MCP API, lifespan-based DB pooling, and JWT validation at tool layer.

## Evaluation notes (flywheel)

- Failure modes observed: None. Context7 MCP SDK documentation provided comprehensive examples for all technical patterns needed.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 10 principles aligned)
- Prompt variant (if applicable): User requested Context7 documentation fetch before planning - successfully completed
- Next experiment (smallest change to try): Proceed to `/sp.tasks` for task breakdown, then implementation using Backend Agent for MCP server code generation
