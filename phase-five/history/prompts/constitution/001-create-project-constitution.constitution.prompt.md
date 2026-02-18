---
id: "001"
title: Create project constitution for Phase-2 Todo web app
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: a
command: /sp.constitution
labels: ["constitution","governance","principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/c/Users/a/Documents/GitHub/YT-Hackathon-II/phase-II/.specify/memory/constitution.md
tests:
  - None
---

## Prompt

/sp.constitution

Project: Todo Full-Stack Web Application (Hackathon Phase-2)

Core principles:
- Spec-driven development: all implementation must strictly follow approved specs
- Agentic workflow compliance: spec → plan → tasks → implementation (no manual coding)
- Security-first design: authentication, authorization, and user isolation enforced by default
- Deterministic behavior: APIs and UI must behave consistently across users and sessions
- Full-stack coherence: frontend, backend, and database must integrate without mismatches

Key standards:
- No implementation without an approved spec and plan
- All API behavior must be explicitly defined in specs
- Authentication must use Better Auth with JWT tokens
- All backend routes must validate JWT and enforce task ownership
- All database queries must be user-scoped
- REST APIs must follow HTTP semantics and status codes
- Errors must be explicit, predictable, and documented
- Frontend must consume APIs exactly as specified
- No hard-coded secrets; environment variables only

Constraints:
- No manual coding; all code generated via Claude Code
- Technology stack is fixed and non-negotiable:
  - Frontend: Next.js 16+ (App Router)
  - Backend: Python FastAPI
  - ORM: SQLModel
  - Database: Neon Serverless PostgreSQL
  - Auth: Better Auth (JWT-based)
- All endpoints require valid JWT after authentication
- Stateless backend authentication (JWT only)
- Multi-user support is mandatory
- Data persistence required across sessions

Success criteria:
- All three specs (Backend, Auth, Frontend) are fully implemented and integrated
- Users can sign up, sign in, and manage only their own tasks
- Unauthorized requests return 401 consistently
- Task ownership is enforced on every CRUD operation
- Application works end-to-end as a full-stack system
- Specs, plans, and iterations are reviewable and traceable
- Project passes hackathon evaluation based on process and correctness

## Response snapshot

Created project constitution at `.specify/memory/constitution.md` with:
- 6 core principles (Spec-Driven Development, Agentic Workflow, Security-First, Deterministic Behavior, Full-Stack Coherence, Traceability)
- Technology Stack section documenting fixed stack (Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
- Development Workflow section with 4 phases (Specification, Planning, Task Breakdown, Implementation, Integration)
- Quality Standards covering API, Security, and Testing requirements
- Governance section establishing constitution precedence

## Outcome

- ✅ Impact: Established project constitution v1.0.0 for Phase-2 Todo web application
- 🧪 Tests: None
- 📁 Files: `.specify/memory/constitution.md`
- 🔁 Next prompts: Create feature specs for Backend, Auth, and Frontend
- 🧠 Reflection: Constitution establishes the governance framework for agentic SDD workflow

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (if applicable): N/A
