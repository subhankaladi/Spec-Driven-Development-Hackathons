<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.0 (initial constitution)
- Modified principles: All principles added as initial content
- Added sections: All sections added as initial content
- Removed sections: None
- Templates requiring updates: ✅ No templates to update (initial constitution)
- Follow-up TODOs: None
-->
# Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-Driven Development (NON-NEGOTIABLE)
All development follows the spec → plan → tasks → implementation workflow; Specifications must be complete and approved before any coding begins; Every feature must have corresponding test cases defined in the tasks document before implementation.

### Zero Manual Coding
Implementation must be achieved exclusively through Claude Code and automated tools; No hand-written code modifications allowed during the development phase; All changes must be traceable through the agentic development workflow.

### Security-First Design
JWT authentication must be enforced on every API route; Multi-user task isolation is mandatory - users can only access their own data; All sensitive data must be properly validated and sanitized before persistence.

### Deterministic and Reproducible Outputs
Every development step must produce consistent, repeatable results; All environment configurations must be version-controlled and reproducible; Build and deployment processes must be idempotent and deterministic.

### Full-Stack Architecture Standards
Backend must use FastAPI + SQLModel with Neon Serverless PostgreSQL; Frontend must use Next.js 16+ App Router with stateless authentication; Better Auth (JWT-based) must be implemented for user management.

### End-to-End Agentic Workflow
All development phases must follow the Agentic Dev Stack workflow from specification to deployment; Each phase must be validated before proceeding to the next; Comprehensive testing must be integrated throughout the workflow.

## Technology Stack Requirements

- Backend: Python FastAPI with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js 16+ with App Router
- Authentication: Better Auth (JWT-based, stateless)
- Environment: All auth secrets must be shared via environment variables
- API Design: RESTful endpoints with consistent error handling and response formats

## Development Workflow

- All code must be generated through Claude Code commands (e.g., /sp.specify, /sp.plan, /sp.tasks, /sp.implement)
- Specifications must be reviewed and approved before planning
- Task breakdowns must include acceptance criteria and test scenarios
- Multi-user task isolation must be validated during implementation
- Frontend-backend communication must be exclusively through authenticated API calls
- All changes must follow the red-green-refactor cycle with proper testing

## Governance

This constitution governs all development activities for the Todo Full-Stack Web Application; All team members must comply with these principles; Amendments require explicit documentation and approval through the /sp.constitution command; Version control and audit trails must be maintained for all changes.

**Version**: 1.0.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2025-12-22
