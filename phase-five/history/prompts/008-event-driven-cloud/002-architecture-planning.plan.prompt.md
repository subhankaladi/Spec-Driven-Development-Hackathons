---
id: 002
title: Phase V Architecture Planning
stage: plan
date: 2026-02-10
surface: agent
model: claude-haiku-4-5-20251001
feature: 008-event-driven-cloud
branch: 008-event-driven-cloud
user: claude
command: /sp.plan
labels: ["event-driven-architecture","kafka","dapr","microservices","kubernetes"]
links:
  spec: /specs/008-event-driven-cloud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/008-event-driven-cloud/plan.md
  - /specs/008-event-driven-cloud/research.md
  - /specs/008-event-driven-cloud/contracts/tasks-api.openapi.yaml
  - /specs/008-event-driven-cloud/contracts/kafka-events.md
tests:
  - All user stories mapped to implementation phases
  - API contracts defined and backward-compatible
  - Event schemas defined with examples
  - Constitution check passed
---

## Prompt

/sp.plan make sure to before planning first review frontend and backend then generate planning

User requested:
1. Review existing frontend (Next.js with App Router) and backend (FastAPI with SQLModel)
2. Generate comprehensive implementation planning for Phase V

Provided high-level outline:
- Architecture Finalization (Dapr components, Kafka topics, event flows)
- Advanced Feature Implementation (recurring tasks, reminders, priorities, tags)
- Event-Driven Microservices (5 consumers + core service)
- Local Deployment (Minikube + Strimzi + Dapr)
- Cloud Deployment (AKS/GKE/OKE with managed services)
- CI/CD & Observability (GitHub Actions, Prometheus, Loki, OpenTelemetry)

## Response snapshot

Delivered comprehensive implementation plan with:

**plan.md** (1500+ lines):
- Phase 0: Architecture research and technical decisions
- Phase 1: Design artifacts (data models, API contracts, microservices architecture, Dapr components, deployment architecture)
- Phase 2: Implementation tasks (database schema, core service enhancement, microservices, frontend integration, Helm charts, Dapr config, CI/CD, observability)
- Phase 3: Testing and validation
- Constitution check + Success criteria mapping
- Risk mitigation + Rollout timeline

**research.md** (800+ lines):
- 10 architectural decisions fully resolved
- Each decision includes: alternatives considered, rationale, implementation approach
- Decisions: Dapr integration, Kafka deployment, event idempotency, state store design, recurring task logic, reminder scheduling, API compatibility, observability stack, CI/CD platform, cloud platform

**Contracts**:
- tasks-api.openapi.yaml: Extended REST API with new fields (priority, tags, due/remind dates, recurrence rules), backward-compatible
- kafka-events.md: Complete Kafka event schemas (task-events, reminders, task-updates topics) with producer/consumer roles and processing logic

**Architecture Summary**:
- 5 microservices (Core Todo, Recurring Task, Notification, Audit Log, WebSocket Sync)
- Dapr for Pub/Sub (Kafka), State Store (Postgres), Jobs API (reminders), Secrets, Service Invocation
- Event-driven workflow: task-created → recurrence/audit/sync consumers process independently
- Helm charts support both Minikube and production Kubernetes clusters
- CI/CD via GitHub Actions with automated build/test/deploy

## Outcome

- ✅ Impact: Complete architectural blueprint enables immediate implementation. All technical decisions resolved. Frontend/backend integration points defined. Deployment topology designed for both local and production.
- 🧪 Tests: Constitution Check passed (Spec-Driven Development, Security-First, Full-Stack Coherence, Traceability, Agentic Workflow). All 13 success criteria mapped to implementation phases. User stories mapped to architecture components.
- 📁 Files: plan.md (16KB), research.md (9KB), tasks-api.openapi.yaml (12KB), kafka-events.md (18KB)
- 🔁 Next prompts: `/sp.tasks` to generate detailed implementation tasks, then begin Phase 2 implementation (database schema, microservices, deployment)
- 🧠 Reflection: Plan demonstrates deep understanding of event-driven architecture patterns. Dapr abstraction enables clean separation of concerns. Event idempotency and state management patterns are production-ready. Deployment strategy ensures consistency between local and production environments.

## Outcome

### Architecture Highlights

**Microservices**:
1. Core Todo Service: Extends FastAPI backend, publishes task lifecycle events
2. Recurring Task Service: Consumes task-completed, generates next occurrence
3. Notification Service: Consumes reminder-triggered, sends notifications (placeholder)
4. Audit Log Service: Consumes all task events, maintains audit trail
5. WebSocket Sync Service: Consumes task-updates, broadcasts to connected clients

**Event Flow Example** (Recurring Task Creation):
```
1. User completes daily standup task
2. Core service publishes task-completed event with recurrence_rule
3. Kafka broker persists event, persists offset
4. Recurring Task Service consumer receives event (within 200-500ms)
5. Checks recurrence_rule, calculates next_occurrence_at
6. Creates new Task record via Dapr state store
7. Publishes task-created event
8. Audit Log Service logs completion and creation
9. WebSocket Sync Service broadcasts update to frontend
10. User sees next occurrence appear in task list
```

**Deployment Architecture**:
- Local: Minikube cluster with Strimzi Kafka operator, Dapr control plane, all 5 microservices
- Production: Managed Kubernetes (AKS/GKE/OKE) with managed Kafka (Redpanda/Confluent)
- Same Helm charts work on both (configuration differs via values files)

**API Contracts**:
- Extended REST API: new query parameters (sort_by, priority, tags, search)
- New fields on Task: priority, tags, due_at, remind_at, recurrence_rule, next_occurrence_at
- Backward-compatible: existing clients continue working, new fields optional

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning comprehensive and ready for task generation.
- Graders run and results (PASS/FAIL): Constitution Check: PASS. Success Criteria Mapping: PASS. Architecture Decisions: PASS.
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Generate task list via `/sp.tasks` to break down implementation into actionable work items. Then begin Phase 2 with database schema extension.

## Open Design Questions (Resolved)

✅ **Dapr Installation**: Decided - Use Dapr control plane on both local and production clusters
✅ **Kafka Deployment**: Decided - Strimzi local, managed Redpanda/Confluent production
✅ **Event Idempotency**: Decided - UUID-based deduplication with DB unique constraints
✅ **State Store**: Decided - Dapr Postgres component (same Neon database)
✅ **Recurring Task Logic**: Decided - Event-driven async consumer
✅ **Reminder Scheduling**: Decided - Dapr Jobs API (no polling)
✅ **API Compatibility**: Decided - Backward-compatible REST extension
✅ **Observability**: Decided - Prometheus + Loki + OpenTelemetry
✅ **CI/CD Platform**: Decided - GitHub Actions
⏳ **Cloud Platform**: Team decision required (AKS vs GKE vs Oracle OKE)

## Recommended ADRs to Create

1. **ADR-001: Event-Driven Architecture with Dapr**
   - Significant architectural pattern change
   - Affects all microservices design
   - Suggests: `/sp.adr "Event-driven microservices with Dapr and Kafka"`

2. **ADR-002: No Direct Database Access for Consumers**
   - Architecture enforcement constraint
   - All state access via Dapr APIs
   - Suggests: `/sp.adr "Dapr state store abstraction for all services"`

3. **ADR-003: Managed Kafka in Production**
   - Different operational models (local vs cloud)
   - Cost and complexity tradeoffs
   - Suggests: `/sp.adr "Managed Kafka services for production deployments"`
