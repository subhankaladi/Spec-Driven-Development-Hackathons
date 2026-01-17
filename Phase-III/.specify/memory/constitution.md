<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0 (MINOR: new Phase III principles added)

Modified principles:
- None renamed, all original principles retained

Added sections:
- Phase III: AI-Powered Todo Chatbot (4 new principles: VII-X)
- Technology Stack: Added OpenAI Agents SDK and Official MCP SDK
- Development Workflow: Added Phase 5 for AI Integration

Removed sections:
- None

Templates requiring updates:
✅ plan-template.md (aligned - Constitution Check section will validate new principles)
✅ spec-template.md (aligned - User Scenarios support natural language interaction stories)
✅ tasks-template.md (aligned - Can organize AI/MCP tasks by user story)
⚠️ No command files exist in .specify/templates/commands/ to update
✅ README.md (reviewed - focuses on frontend, no conflicts with Phase III)

Follow-up TODOs:
- None - all placeholders resolved

Rationale for MINOR bump:
- New principles added (VII-X) for Phase III AI integration
- Backward compatible - all Phase I & II principles unchanged
- Existing specs/plans/tasks remain valid
- Additive change: extends project capabilities without breaking existing work
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development
All implementation MUST strictly follow approved specifications. No code may be written without first creating and obtaining approval for a feature spec. The workflow is mandatory: Spec → Plan → Tasks → Implementation. This ensures every feature has explicit documentation of behavior before any code is written.

### II. Agentic Workflow Compliance
All code generation MUST occur through Claude Code using specialized agents (Auth, Frontend, Database, Backend). No manual coding is permitted. This ensures consistency, traceability, and enables the hackathon evaluation process to review prompts and iterations.

### III. Security-First Design
Authentication, authorization, and user isolation MUST be enforced by default. JWT tokens must be validated on every backend request. Task ownership must be enforced on every CRUD operation. Multi-user isolation is mandatory - users can only access their own data.

### IV. Deterministic Behavior
APIs and UI MUST behave consistently across users and sessions. All API behavior must be explicitly defined in specs. REST APIs must follow HTTP semantics and status codes. Errors must be explicit, predictable, and documented.

### V. Full-Stack Coherence
Frontend, backend, and database must integrate without mismatches. The frontend must consume APIs exactly as specified. All database queries must be user-scoped. No hard-coded secrets; environment variables only.

### VI. Traceability
All prompts, iterations, and implementation decisions MUST be recorded in Prompt History Records (PHRs). Specs, plans, and iterations must be reviewable and traceable. This enables the hackathon evaluation process.

### VII. Natural Language as First-Class Interface (Phase III)
Users MUST be able to manage todos through natural language conversation. The AI chatbot is not an add-on but a primary interface. All task operations (create, read, update, delete, list) must be accessible via conversational commands. Natural language takes precedence over rigid command syntax.

**Rationale**: Modern users expect conversational interfaces. Voice assistants and chat interfaces are becoming the primary way users interact with productivity tools. Natural language reduces friction and learning curves.

### VIII. Tool-Driven AI Architecture (Phase III)
AI agents MUST act exclusively via MCP (Model Context Protocol) tools. Agents may not directly access databases, APIs, or file systems. Every task operation must be implemented as a stateless, deterministic MCP tool. This enforces clean separation between AI reasoning and system actions.

**Rationale**: Tool-driven architecture ensures AI behavior is auditable, testable, and safe. MCP provides a standardized interface that prevents AI from taking uncontrolled actions. Tools can be tested independently of AI logic.

### IX. Fully Stateless Server Architecture (Phase III)
The backend MUST NOT maintain in-memory conversation state. All conversation history must be persisted in PostgreSQL. Server restarts must not lose user conversations. The AI chatbot must resume conversations from database state after any interruption.

**Rationale**: Stateless architecture enables horizontal scaling, simplifies deployment, and ensures reliability. Users expect conversations to persist across sessions. Database-backed state is the only acceptable approach for production systems.

### X. User Identity Enforcement at Tool Level (Phase III)
Every MCP tool invocation MUST verify the user's identity via JWT token. Tools must reject operations that would access data outside the authenticated user's scope. User isolation enforcement happens at the tool layer, not just the API layer.

**Rationale**: Defense in depth - even if AI reasoning has errors, tools provide a security boundary. User isolation must be enforced at every layer to prevent data leakage. Tools are the last line of defense before data access.

## Technology Stack

The following technology stack is fixed and non-negotiable for this project:

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 16+ (App Router) | Use Frontend Agent |
| Backend | Python FastAPI | Use Backend Agent |
| ORM | SQLModel | Use Database Agent |
| Database | Neon Serverless PostgreSQL | Use Database Agent |
| Authentication | Better Auth (JWT-based) | Use Auth Agent |
| AI Framework | OpenAI Agents SDK | Phase III: Conversational AI |
| Tool Protocol | Official MCP SDK | Phase III: Tool exposure |

## Development Workflow

### Phase 0: Specification
1. Create feature spec in `specs/<feature>/spec.md`
2. Define user stories with priorities (P1, P2, P3)
3. Define functional requirements
4. Define success criteria
5. Obtain approval before proceeding

### Phase 1: Planning
1. Create implementation plan in `specs/<feature>/plan.md`
2. Define technical context and project structure
3. Document architecture decisions
4. Verify compliance with constitution
5. Obtain approval before proceeding

### Phase 2: Task Breakdown
1. Create task list in `specs/<feature>/tasks.md`
2. Organize tasks by user story
3. Define clear dependencies
4. Enable independent implementation of each story

### Phase 3: Implementation
1. Use specialized agents based on task type
2. Follow Red-Green-Refactor where tests are included
3. Create PHR for every agent invocation
4. Maintain full traceability

### Phase 4: Integration
1. Integrate frontend with backend APIs
2. Verify user isolation works correctly
3. Test end-to-end functionality
4. Ensure all unauthorized requests return 401

### Phase 5: AI Integration (Phase III)
1. Define MCP tools for all task operations
2. Implement tools as stateless, user-scoped functions
3. Configure OpenAI Agents SDK with tool schemas
4. Implement conversation persistence in PostgreSQL
5. Create single chat endpoint: POST /api/{user_id}/chat
6. Test AI tool selection and natural language understanding
7. Verify conversation state survives server restarts
8. Validate user isolation at tool invocation level

## Quality Standards

### API Requirements
- All endpoints require valid JWT after authentication
- Stateless backend authentication (JWT only)
- REST APIs must follow HTTP semantics
- Proper status codes for all outcomes
- Explicit error responses with documented schemas

### Security Requirements
- JWT token validation on every request
- Task ownership enforced on every operation
- User-scoped database queries
- No hard-coded secrets
- Environment variables for all credentials
- **Phase III**: User identity verified at MCP tool invocation
- **Phase III**: Tools must validate user_id from JWT matches operation scope

### Testing Requirements
- Contract tests for API endpoints
- Integration tests for user journeys
- Independent testability of each user story
- All tests must fail before implementation (where applicable)
- **Phase III**: MCP tool unit tests (stateless, deterministic behavior)
- **Phase III**: AI conversation integration tests
- **Phase III**: Conversation persistence tests (verify resume after restart)

### AI Requirements (Phase III)
- Agents must invoke MCP tools for all task actions
- MCP tools must be stateless and deterministic
- Conversation state must be persisted in PostgreSQL
- No in-memory conversation state allowed
- AI must reliably select correct MCP tools for user intent
- Natural language commands must map to tool invocations

## Governance

This constitution supersedes all other development practices. Amendments require documentation and approval. All team members must verify compliance with these principles before merging any implementation.

The constitution takes precedence over:
- Individual developer preferences
- Convenience-driven shortcuts
- Undocumented assumptions

### Amendment Procedure
1. Propose changes with clear rationale
2. Identify affected templates and artifacts
3. Increment version according to semantic versioning:
   - MAJOR: Backward incompatible changes (principle removal/redefinition)
   - MINOR: New principles or sections added
   - PATCH: Clarifications, wording improvements, non-semantic fixes
4. Update all dependent templates and documentation
5. Document changes in Sync Impact Report
6. Obtain approval before committing

### Compliance Review
- Every feature spec must reference constitution principles
- Every plan must include Constitution Check section
- Every task must trace to a principle-driven requirement
- PHRs must document adherence to agentic workflow

**Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-16
