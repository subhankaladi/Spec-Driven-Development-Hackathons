<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- List of modified principles:
  - PRINCIPLE_1_NAME → Strict Spec-Driven Development
  - PRINCIPLE_2_NAME → Accuracy and Completeness
  - PRINCIPLE_3_NAME → Consistency Across Phases
  - PRINCIPLE_4_NAME → AI-First Tooling
  - PRINCIPLE_5_NAME → Sequential Phased-Based Development
- Added sections:
  - Principle 6: Stateless Tooling with Persistent State
  - Principle 7: Cloud Native Practices
  - Principle 8: Progressive Feature Rollout
  - Principle 9: Reproducibility
  - Key Standards
  - Constraints
  - Success Criteria
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->
# 5-Phase Evolution of Todo Application (Console → Web → AI Chatbot → Kubernetes → Cloud) Constitution

## Core Principles

### I. Strict Spec-Driven Development
No manual coding. Every feature requires a clear Spec + refined implementation loop.

### II. Accuracy and Completeness
All feature implementations must be accurate and complete as defined in their respective specifications.

### III. Consistency Across Phases
Consistency in specifications, architecture, APIs, and database schemas must be maintained across all development phases.

### IV. AI-First Tooling
The project will exclusively use Claude Code for code generation and Spec-Kit Plus, OpenAI Chatbot/Agents, and MCP for development and automation.

### V. Sequential Phased-Based Development
The 5 project phases must be completed sequentially.

### VI. Stateless Tooling with Persistent State
MCP tools must be stateless. All application state is to be managed in a PostgreSQL database.

### VII. Cloud Native Practices
Cloud deployments must adhere to Kubernetes best practices, using Helm charts for packaging. Event-driven pipelines will be implemented using Dapr and Kafka.

### VIII. Progressive Feature Rollout
Intermediate and Advanced features are only allowed to be implemented in Phase V.

### IX. Reproducibility
All phases of the project must be fully reproducible from their specifications with zero manual code writing.

## Key Standards
- Every feature requires a clear Spec + refined implementation loop.
- Code must be generated exclusively through Claude Code.
- APIs must follow REST conventions.
- MCP tools must be stateless; all state in PostgreSQL.
- Cloud deployments must use Kubernetes best practices and Helm charts.

## Constraints
- 5 Phases must be completed sequentially:
  1. Python console app (in-memory)
  2. Full-stack web app with Neon PostgreSQL + Better Auth
  3. AI Chatbot using MCP Server + OpenAI Agents SDK
  4. Local Kubernetes deployment (Minikube, Docker, Helm)
  5. Cloud deployment (DOKS/GKE/AKS) + Dapr + Kafka
- Intermediate & Advanced features are only allowed in Phase V.
- All specs must be written in Markdown.

## Success Criteria
- The Console, Web, AI Chatbot, and Kubernetes versions are all fully functional.
- Natural-language task management works via MCP + Agents.
- Local & Cloud Kubernetes deployments succeed without errors.
- Dapr + Kafka integrations operate event-driven pipelines.
- All phases are reproducible from spec with zero manual code writing.

## Governance
This constitution is the single source of truth for project principles and standards. All development activities must comply with it. Amendments require documentation, review, and an approved migration plan.

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06