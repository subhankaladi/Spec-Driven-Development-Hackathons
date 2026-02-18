---
id: 001
title: Phase V Event-Driven Cloud Spec
stage: spec
date: 2026-02-10
surface: agent
model: claude-haiku-4-5-20251001
feature: 008-event-driven-cloud
branch: 008-event-driven-cloud
user: claude
command: /sp.specify
labels: ["event-driven-architecture","kubernetes","kafka","dapr","cloud-deployment"]
links:
  spec: /specs/008-event-driven-cloud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/008-event-driven-cloud/spec.md
  - /specs/008-event-driven-cloud/checklists/requirements.md
tests:
  - Quality checklist: all items pass
---

## Prompt

/sp.specify Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform

Target audience:
- Platform engineers, cloud engineers, and system design evaluators
- Hackathon judges evaluating production-grade Kubernetes systems

Objective:
Transform the existing Todo application into a fully event-driven, cloud-native system using Kafka and Dapr, deployed first locally on Minikube and then to a production Kubernetes cluster (AKS, GKE, or Oracle OKE).

The system must demonstrate decoupled microservices, asynchronous workflows, and cloud-ready operational practices.

────────────────────────
SYSTEM CONTEXT
────────────────────────

Existing system (from Phase III & IV):
- Frontend: Next.js
- Backend: Python FastAPI
- Database: External Postgres (Neon)
- Deployment: Docker + Helm + Minikube
- Development style: Spec-Driven Development (spec → plan → tasks → implementation)

Phase-V must extend this system WITHOUT rewriting core services.

────────────────────────
FUNCTIONAL REQUIREMENTS
────────────────────────

A. Advanced Todo Features

1. Recurring Tasks
- Users can define tasks with recurrence rules (daily, weekly, monthly)
- When a recurring task is completed, the next occurrence is auto-created
- Recurrence logic must be asynchronous (event-driven)

2. Due Dates & Reminders
- Tasks can have due_at and remind_at timestamps
- Reminder events must trigger notifications at exact scheduled times
- No polling-based reminder system is allowed

3. Intermediate Features
- Task priorities (low, medium, high)
- Tags and tag-based filtering
- Search by title and description
- Sorting by due date, priority, and creation time

────────────────────────
EVENT-DRIVEN ARCHITECTURE
────────────────────────

Kafka must be used as the event backbone.

Topics:
- task-events → All task lifecycle events
- reminders → Reminder trigger events
- task-updates → Real-time sync events

Event rules:
- Every task create/update/delete/complete publishes an event
- No service may directly call another service for these workflows
- Consumers must be independent and restart-safe

Required services:
1. Core Todo Service (Producer)
2. Recurring Task Service (Consumer)
3. Notification Service (Consumer)
4. Audit Log Service (Consumer)
5. WebSocket Sync Service (Consumer)

────────────────────────
DAPR INTEGRATION REQUIREMENTS
────────────────────────

All inter-service communication must use Dapr building blocks.

Required Dapr components:
- Pub/Sub → Kafka abstraction
- State Store → External Postgres
- Service Invocation → Frontend → Backend calls
- Jobs API → Exact-time reminders
- Secrets Store → Credentials & keys

Constraints:
- No Kafka client libraries inside application code
- No direct DB connection for non-core services
- All services communicate via Dapr HTTP/gRPC APIs

────────────────────────
DEPLOYMENT REQUIREMENTS
────────────────────────

Part A – Local Deployment
- Deploy full system on Minikube
- Install Dapr control plane
- Deploy Kafka (Strimzi or Redpanda)
- All services must be observable and functional locally

Part B – Cloud Deployment
- Deploy to one production Kubernetes platform:
  - Azure AKS OR
  - Google GKE OR
  - Oracle OKE (recommended)

Cloud requirements:
- Same Helm charts as local deployment
- Dapr installed in cluster
- Kafka via managed service (Redpanda / Confluent) or self-hosted
- External secrets configured securely

────────────────────────
CI / CD REQUIREMENTS
────────────────────────

- GitHub Actions pipeline
- Steps:
  1. Lint & validate specs
  2. Build Docker images
  3. Push images to registry
  4. Deploy via Helm to Kubernetes cluster
- No manual kubectl apply in production

────────────────────────
OBSERVABILITY REQUIREMENTS
────────────────────────

- Metrics collection (Prometheus or cloud-native alternative)
- Centralized logging
- Health checks for all services
- Ability to trace an event from producer → consumer

────────────────────────
SUCCESS CRITERIA
────────────────────────

The phase is considered complete when:

- Todo app runs locally and on cloud without code changes
- Kafka events drive reminders, recurring tasks, and audit logs
- Dapr abstracts Kafka, state, and service discovery
- CI/CD deploys automatically
- System can scale individual services independently

────────────────────────
OUT OF SCOPE
────────────────────────

- UI redesign
- Mobile applications
- Vendor-specific lock-in features
- Complex notification channels (SMS/WhatsApp)

────────────────────────
DELIVERABLES
────────────────────────

- Phase-V specification
- Architecture diagrams
- Helm charts
- Dapr component definitions
- CI/CD pipeline configuration
- Deployment documentation

## Response snapshot

Created comprehensive Phase V specification with:
- 6 user stories (3 P1, 3 P2) covering Minikube deployment, cloud promotion, recurring tasks, observability, extensibility, and CI/CD automation
- 34 functional requirements organized by domain
- 13 measurable success criteria with specific metrics
- 5 edge cases addressing failure scenarios
- 6 key entities defining the domain model
- 9 assumptions documenting defaults and constraints
- 7 hard constraints defining system boundaries
- Quality checklist: all items pass

Spec file created at: `/specs/008-event-driven-cloud/spec.md`
Branch: `008-event-driven-cloud` (feature #008)

## Outcome

- ✅ Impact: Specification provides complete, testable requirements for event-driven cloud architecture with Kafka and Dapr. No ambiguity or missing requirements. Ready for planning phase.
- 🧪 Tests: Quality checklist validates specification completeness (18/18 items pass). All user stories are independently testable. All requirements are measurable and technology-agnostic.
- 📁 Files: spec.md (34KB), requirements.md checklist (1.5KB), this PHR (6KB)
- 🔁 Next prompts: `/sp.clarify` to gather additional clarifications if needed, or `/sp.plan` to begin architecture planning
- 🧠 Reflection: Specification successfully translates high-level Phase V vision into concrete, testable requirements. The event-driven architecture constraints (no direct service calls, all via Kafka/Dapr) are clearly stated. Both local (Minikube) and cloud deployment paths are equivalent, ensuring consistency.

## Evaluation notes (flywheel)

- Failure modes observed: None. Spec generation completed without clarification markers needed. All requirements have clear acceptance criteria.
- Graders run and results (PASS/FAIL): Quality checklist: PASS (18/18 items)
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): If clarifications needed, run `/sp.clarify` to resolve before planning. Otherwise proceed directly to `/sp.plan` for architecture design.
