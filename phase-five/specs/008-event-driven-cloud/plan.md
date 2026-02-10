# Implementation Plan: Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform

**Feature**: Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform
**Feature Branch**: `008-event-driven-cloud`
**Created**: 2026-02-10
**Status**: Draft
**Spec Reference**: [spec.md](./spec.md)

---

## Executive Summary

Phase V transforms the existing Phase III/IV Todo app into a fully event-driven, cloud-native system. The plan:
- Extends the Task model with new fields (due_at, remind_at, priority, tags, recurrence)
- Implements 5 microservices communicating via Kafka and Dapr
- Deploys locally on Minikube and to production Kubernetes (AKS/GKE/OKE)
- Automates deployment via GitHub Actions CI/CD
- Provides production-grade observability

**Scope**: Architecture finalization → Microservices build → Local deployment → Cloud deployment → CI/CD automation

---

## Phase 0: Architecture & Research

### 0.1 Current System Context

**Existing System (Phase III/IV)**:
- Frontend: Next.js 16+ with App Router (React components, server/client boundaries)
- Backend: FastAPI on Python 3.12 with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT tokens
- Current Task model: id, user_id, title, description, is_completed, created_at, updated_at

**Deployment Current State**:
- Docker containerization (backend and frontend)
- Helm charts for Kubernetes (exists in prior phases)
- Minikube local deployment support (prior phases)

**Constraints from Constitution**:
- Spec-Driven Development mandatory
- Security-first: user isolation on every operation
- Full-stack coherence required
- Agentic workflow (specialized agents for auth, frontend, backend, database)
- Traceability via PHRs
- Stateless server (no in-memory state)

### 0.2 Technical Context & Research Questions

#### Architecture Integration Points

**NEEDS CLARIFICATION: Dapr Installation & Configuration**
- Decision: Use Dapr control plane on both Minikube and production clusters
- Rationale: Dapr provides abstraction layer for Kafka, state store, jobs scheduling, and service invocation
- Alternatives considered: Direct Kafka client libraries (violates spec constraint), service mesh like Istio (heavier, not needed)
- Implementation: Install Dapr via Helm charts; configure Dapr sidecar injector for all pods

**NEEDS CLARIFICATION: Kafka Deployment Strategy**
- Decision: Use Strimzi operator on Minikube (easy local testing); managed Redpanda/Confluent on production
- Rationale: Strimzi integrates well with Kubernetes; production-ready Kafka managed services reduce operational burden
- Alternatives: Full self-hosted Strimzi everywhere (operational complexity), no local Kafka (can't test locally)
- Implementation: Strimzi Helm charts locally; production managed service integration via Dapr config

**NEEDS CLARIFICATION: Event Idempotency Pattern**
- Decision: Use idempotency keys (UUID-based deduplication) in events + database unique constraints
- Rationale: Kafka guarantees at-least-once delivery; consumers must be idempotent
- Alternatives: Exactly-once processing (complex, not worth the overhead)
- Implementation: Event producers include idempotency_key field; consumers check before applying side effects

**NEEDS CLARIFICATION: Dapr State Store Design**
- Decision: Use Dapr Postgres state store component (same Neon database as core service)
- Rationale: Single database reduces complexity; Dapr handles connection pooling and state management
- Alternatives: Separate Redis for microservice state (adds infrastructure), file-based (not scalable)
- Implementation: Configure Dapr state store with Postgres backend; services access via Dapr HTTP API

#### Event Flow & Topic Design

**task-events Topic**
- Events: task-created, task-updated, task-deleted, task-completed
- Producers: Core Todo Service
- Consumers: Recurring Task Service, Audit Log Service, WebSocket Sync Service
- Payload schema: { event_type, task_id, user_id, timestamp, event_data, idempotency_key }

**reminders Topic**
- Events: reminder-scheduled, reminder-triggered
- Producers: Core Todo Service (on task creation with due_at)
- Consumers: Notification Service
- Payload schema: { reminder_id, task_id, user_id, remind_at, notification_method }

**task-updates Topic**
- Events: task-state-changed (used for real-time sync only)
- Producers: Core Todo Service (on every task change)
- Consumers: WebSocket Sync Service
- Payload schema: { task_id, user_id, updated_fields, timestamp }

#### Recurring Task Generation Logic

**Decision**: Event-driven recurring task generation
- When task is completed → publish task-completed event
- Recurring Task Service consumes event → generates next occurrence
- Stores next task in database
- Publishes new task-created event (for audit and sync)
- Client receives update via WebSocket

**Rationale**: Asynchronous, decoupled, survives service restarts

**Implementation**:
```
Task model:
- recurrence_rule: Optional JSON { frequency: "daily|weekly|monthly", end_date?: date }
- next_occurrence_at: Optional[datetime]

When task completed:
1. Core service publishes task-completed event with recurrence_rule
2. Recurring Task Service consumes event
3. Calculates next_occurrence_at based on frequency
4. Creates new Task record with recurrence_rule
5. Publishes task-created event
```

#### Reminder Scheduling Strategy

**Decision**: Use Dapr Jobs API for exact-time scheduling
- When task created with remind_at timestamp → schedule job via Dapr
- Dapr Jobs API triggers callback at exact time
- Callback publishes reminder event to reminders topic
- Notification Service consumes and handles notification

**Rationale**:
- No polling (violates spec requirement)
- Dapr abstracts job scheduling (could be Kubernetes CronJob, managed service, etc.)
- Exact time delivery (±5 second precision acceptable per spec)

**Implementation**:
```
Dapr Jobs API call:
POST /v1.0/jobs/reminders/{reminder_id}
{
  "schedule": "2026-02-15T09:00:00Z",
  "payload": { task_id, user_id, remind_at }
}

On trigger:
- Dapr invokes callback endpoint
- Service publishes reminder event to reminders topic
- Notification Service consumes and delivers notification
```

#### Database Schema Extension

**New fields on Task model**:
- due_at: Optional[datetime] — When task is due
- remind_at: Optional[datetime] — When to send reminder
- priority: Optional[str] — "low", "medium", "high" (default: "medium")
- tags: Optional[List[str]] — Task categories/labels
- recurrence_rule: Optional[JSON] — Recurrence configuration (frequency, end_date)
- next_occurrence_at: Optional[datetime] — For recurring tasks

**Index strategy**:
- (user_id, due_at) — for sorting/filtering by due date
- (user_id, priority) — for priority filtering
- (user_id, created_at) — for creation time sorting

#### API Contract Extensions

**Current endpoints** (unchanged):
```
POST /users/{user_id}/tasks — Create task
GET /users/{user_id}/tasks — List tasks (add query params)
GET /users/{user_id}/tasks/{task_id} — Get task
PATCH /users/{user_id}/tasks/{task_id} — Update task
DELETE /users/{user_id}/tasks/{task_id} — Delete task
```

**New query parameters for GET /users/{user_id}/tasks**:
- sort_by: "due_at", "priority", "created_at"
- sort_order: "asc", "desc"
- priority: "low", "medium", "high" (filter)
- tags: "tag1,tag2" (filter by any tag)
- search: "query" (search in title and description)

**Request body extension for POST/PATCH**:
```json
{
  "title": "...",
  "description": "...",
  "due_at": "2026-02-15T09:00:00Z",
  "remind_at": "2026-02-15T08:50:00Z",
  "priority": "high",
  "tags": ["work", "urgent"],
  "recurrence_rule": {
    "frequency": "daily",
    "end_date": "2026-12-31"
  }
}
```

**Response includes new fields**:
```json
{
  "id": "...",
  "user_id": "...",
  "title": "...",
  "description": "...",
  "is_completed": false,
  "due_at": "2026-02-15T09:00:00Z",
  "remind_at": "2026-02-15T08:50:00Z",
  "priority": "high",
  "tags": ["work", "urgent"],
  "recurrence_rule": {...},
  "next_occurrence_at": null,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## Phase 1: Design & Contracts

### 1.1 Data Model Design

**Extended Task Entity**:
```
Entity: Task
Fields:
  - id: UUID (primary key)
  - user_id: UUID (foreign key, indexed)
  - title: string (1-255 chars, required)
  - description: string (optional)
  - is_completed: boolean (default: false)
  - due_at: datetime (optional)
  - remind_at: datetime (optional)
  - priority: enum("low", "medium", "high", default="medium")
  - tags: list[string] (optional, max 50 tags)
  - recurrence_rule: JSON (optional) {
      frequency: "daily"|"weekly"|"monthly",
      end_date: date (optional)
    }
  - next_occurrence_at: datetime (optional, for recurring tasks)
  - created_at: datetime (required, auto-set)
  - updated_at: datetime (required, auto-update)

Constraints:
  - user_id NOT NULL (user isolation)
  - title NOT NULL, min length 1
  - is_completed boolean NOT NULL
  - Unique index: (user_id, due_at, priority) — for efficient sorting
  - Unique index: (user_id, created_at) — for chronological queries

State Transitions:
  - created → [completed, updated, deleted]
  - completed + has_recurrence → triggers new task creation
  - deleted → audit log entry created
```

**New Audit Log Entity**:
```
Entity: AuditLog
Fields:
  - id: UUID (primary key)
  - user_id: UUID (indexed)
  - action: enum("created", "updated", "deleted", "completed")
  - task_id: UUID (references Task)
  - change_data: JSON (what changed)
  - timestamp: datetime (when action occurred)
  - service_name: string (which service recorded it)
```

**New Reminder Entity**:
```
Entity: Reminder
Fields:
  - id: UUID (primary key)
  - task_id: UUID (indexed, references Task)
  - user_id: UUID (indexed)
  - remind_at: datetime (when to trigger)
  - notification_method: string (optional, future extensibility)
  - status: enum("scheduled", "triggered", "cancelled")
  - created_at: datetime
  - triggered_at: datetime (optional)
```

### 1.2 API Contracts

**File**: `/contracts/tasks-api.openapi.yaml`

Core endpoints remain compatible:
```yaml
POST /users/{user_id}/tasks
  Request: TaskCreateRequest
  Response: 201 TaskResponse

GET /users/{user_id}/tasks
  Query: sort_by, sort_order, priority, tags, search
  Response: 200 TaskListResponse (paginated)

GET /users/{user_id}/tasks/{task_id}
  Response: 200 TaskResponse

PATCH /users/{user_id}/tasks/{task_id}
  Request: TaskUpdateRequest
  Response: 200 TaskResponse

DELETE /users/{user_id}/tasks/{task_id}
  Response: 204 No Content
```

**Kafka Event Schema**:
```yaml
task-created:
  event_type: "task-created"
  task_id: UUID
  user_id: UUID
  timestamp: ISO8601
  event_data:
    title: string
    due_at: ISO8601 (optional)
    recurrence_rule: JSON (optional)
  idempotency_key: UUID

task-completed:
  event_type: "task-completed"
  task_id: UUID
  user_id: UUID
  timestamp: ISO8601
  recurrence_rule: JSON (optional)
  idempotency_key: UUID

reminder-triggered:
  reminder_id: UUID
  task_id: UUID
  user_id: UUID
  remind_at: ISO8601
  timestamp: ISO8601
  idempotency_key: UUID
```

### 1.3 Microservices Architecture

**5 Microservices**:

1. **Core Todo Service** (extends existing backend)
   - Responsible for: Task CRUD, user isolation, event publishing
   - Published events: task-created, task-updated, task-deleted, task-completed
   - Consumed events: None (producer only)
   - Tech: FastAPI, SQLModel, Neon Postgres
   - Deployment: Single instance, stateless

2. **Recurring Task Service** (new consumer)
   - Responsible for: Generate next recurring task when previous completed
   - Consumed events: task-completed (with recurrence_rule)
   - Published events: task-created (new recurring task)
   - Tech: FastAPI, Dapr state store, Kafka consumer
   - Deployment: Single instance initially, can scale horizontally
   - No direct database access (via Dapr state store)

3. **Notification Service** (new consumer)
   - Responsible for: Handle reminder notifications
   - Consumed events: reminder-triggered
   - Published events: None (end consumer)
   - Tech: FastAPI, no persistence
   - Deployment: Can scale horizontally (load balancer)
   - Placeholder implementation: logs notifications (future: email, SMS, push)

4. **Audit Log Service** (new consumer)
   - Responsible for: Persist audit trail of all task changes
   - Consumed events: task-created, task-updated, task-deleted, task-completed
   - Published events: None (end consumer)
   - Tech: FastAPI, dedicated Postgres table (or separate DB)
   - Deployment: Single instance (write-heavy, need ordering guarantees)
   - Processes all events to maintain complete audit history

5. **WebSocket Sync Service** (new consumer, real-time)
   - Responsible for: Real-time multi-client sync via WebSocket
   - Consumed events: task-updates
   - Published events: None
   - Tech: FastAPI with WebSocket support, in-memory connection tracking
   - Deployment: Single instance initially (or sticky session load balancing)
   - Maintains WebSocket connections, broadcasts updates to connected clients

### 1.4 Dapr Component Configuration

**Pub/Sub (Kafka abstraction)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-broker:9092"
    - name: consumerGroup
      value: "dapr-consumer"
```

**State Store (Postgres)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-state
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString
```

**Jobs (Reminder Scheduling)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-jobs
spec:
  type: jobs.kubernetes
  version: v1
```

**Secrets Store**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

**Service Invocation**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: dapr-service-invocation
spec:
  type: serviceInvocation
  version: v1
  metadata:
    - name: mTLSEnabled
      value: "false"  # Can enable for production
```

### 1.5 Deployment Architecture

**Local Deployment (Minikube)**:
```
Minikube Cluster
├── Dapr Control Plane (system namespace)
├── Kafka + Zookeeper (Strimzi)
├── PostgreSQL (Neon external reference)
├── Microservices (default namespace)
│   ├── Core Todo Service (port 8000)
│   ├── Recurring Task Service (port 8001)
│   ├── Notification Service (port 8002)
│   ├── Audit Log Service (port 8003)
│   └── WebSocket Sync Service (port 8004)
├── Next.js Frontend (port 3000)
└── Prometheus + Loki (observability)
```

**Production Deployment (AKS/GKE/OKE)**:
```
Kubernetes Cluster
├── Dapr Control Plane (system namespace)
├── Managed Kafka (Redpanda Cloud or Confluent)
├── PostgreSQL (Neon external reference)
├── Microservices (production namespace)
│   ├── Core Todo Service (2 replicas)
│   ├── Recurring Task Service (2 replicas)
│   ├── Notification Service (3 replicas, load balanced)
│   ├── Audit Log Service (1 replica, write-ordered)
│   └── WebSocket Sync Service (2 replicas, sticky sessions)
├── Next.js Frontend (2 replicas)
├── Prometheus (managed or self-hosted)
├── Loki/ELK (centralized logging)
└── Ingress Controller (external access)
```

---

## Phase 2: Implementation Tasks

### 2.1 Database Schema Extension

**Task**:
1. Create Alembic migration to add new columns to Task table
2. Add indices for (user_id, due_at), (user_id, priority)
3. Create AuditLog table with schema
4. Create Reminder table with schema
5. Run migration locally and on test database

**Files to create/modify**:
- `backend/alembic/versions/006_extend_task_schema.py` — New migration
- `backend/src/models/task.py` — Add fields to Task model
- `backend/src/models/audit_log.py` — New AuditLog model
- `backend/src/models/reminder.py` — New Reminder model

### 2.2 Core Todo Service Enhancement

**Task**: Extend existing FastAPI backend to publish events and support new fields

**Changes**:
1. Extend Task schema to include new fields
2. Implement Dapr Pub/Sub client for event publishing
3. On task create/update/delete/complete → publish event
4. Add query parameters for sorting/filtering
5. Maintain backward compatibility with existing API
6. Add Dapr sidecar configuration

**Files to modify**:
- `backend/src/api/schemas/task.py` — Add new fields
- `backend/src/api/routes/tasks.py` — Add sorting, filtering, event publishing
- `backend/src/services/task_service.py` — Event publishing logic
- `backend/src/main.py` — Dapr sidecar initialization
- `backend/Dockerfile` — Dapr sidecar injection

### 2.3 Microservices Implementation

**3 Consumer Services** (Recurring Task, Notification, Audit Log, WebSocket Sync):

Each service:
1. Create new FastAPI application with Dapr integration
2. Implement Dapr pub/sub consumer for assigned topic
3. Implement business logic
4. Package in Docker
5. Create Helm chart

**Recurring Task Service** (`backend/src/services/recurring_task_service/`):
- Consumes task-completed events
- Queries Dapr state store for Task recurrence_rule
- Calculates next_occurrence_at
- Creates new Task via Dapr service invocation or direct DB insert
- Publishes task-created event

**Audit Log Service** (`backend/src/services/audit_log_service/`):
- Consumes all task events
- Transforms events to AuditLog records
- Writes to database (own connection or via Dapr state)

**Notification Service** (`backend/src/services/notification_service/`):
- Consumes reminder-triggered events
- Logs notification (placeholder implementation)
- Future: integrate email, SMS, push

**WebSocket Sync Service** (`backend/src/services/websocket_sync_service/`):
- Maintains WebSocket connections from frontend
- Consumes task-updates events
- Broadcasts updates to connected clients in real-time

### 2.4 Frontend Integration

**Task**: Update Next.js frontend to support new features

**Changes**:
1. Extend TaskForm component to include priority, tags, due_at, remind_at, recurrence_rule
2. Add filtering UI for priority, tags, search
3. Add sorting options (due_at, priority, created_at)
4. Implement WebSocket connection to WebSocket Sync Service
5. Display recurring task indicators
6. Show reminders/due dates visually

**Files to modify**:
- `frontend/src/components/tasks/TaskForm.tsx` — Add new fields
- `frontend/src/components/tasks/TaskList.tsx` — Add filtering/sorting UI
- `frontend/src/hooks/useWebSocket.ts` — New WebSocket hook
- `frontend/src/lib/api.ts` — New API calls for filtering/sorting

### 2.5 Kubernetes & Helm Charts

**Task**: Create/update Helm charts for all services

**Structure**:
```
helm/charts/
├── todo-system/ — Umbrella chart
├── core-todo-service/
├── recurring-task-service/
├── notification-service/
├── audit-log-service/
├── websocket-sync-service/
├── kafka/
└── dapr/
```

**Each chart includes**:
- Deployment manifest with Dapr sidecar injection
- Service manifest
- ConfigMap for Dapr configuration
- ResourceQuota
- Health checks (liveness, readiness)
- Logging configuration

**Environment-specific values**:
- `values-local.yaml` — Minikube settings, local Kafka
- `values-prod.yaml` — Production Kubernetes, managed Kafka

### 2.6 Dapr Configuration

**Task**: Create Dapr component manifests

**Files**:
- `k8s/dapr/pubsub-kafka.yaml` — Kafka pub/sub component
- `k8s/dapr/state-postgres.yaml` — Postgres state store
- `k8s/dapr/jobs-kubernetes.yaml` — Kubernetes jobs component
- `k8s/dapr/secrets-kubernetes.yaml` — Kubernetes secrets component
- `k8s/dapr/service-invocation.yaml` — Service invocation component

### 2.7 GitHub Actions CI/CD

**Task**: Create automated deployment pipeline

**Pipeline steps**:
1. Lint & validate specs
2. Build Docker images for all services
3. Push images to container registry
4. Validate Kubernetes manifests
5. Deploy to test Minikube cluster
6. Run integration tests
7. Optional: manual approval for production
8. Deploy to production cluster

**Workflow file**: `.github/workflows/deploy-phase-v.yml`

### 2.8 Observability

**Task**: Implement monitoring, logging, tracing

**Prometheus metrics**:
- Task creation rate (requests/sec)
- Event processing latency (ms)
- Kafka consumer lag (messages)
- Service availability (uptime %)
- API latency p50/p95/p99

**Centralized logging**:
- All services log to stdout (container logs)
- Loki or ELK aggregates logs by pod/service
- Structured JSON logs with trace IDs

**Distributed tracing**:
- Instrument all services with OpenTelemetry
- Trace ID propagates through events
- Trace shows: event publish → Kafka → consumer processing → state update

**Health checks**:
- Kubernetes liveness probe: /health
- Kubernetes readiness probe: /ready
- Health check includes: service health, Kafka connectivity, database connectivity

---

## Phase 3: Testing & Validation

### 3.1 Local Deployment Testing

1. Deploy all services to Minikube
2. Test task creation → event published to Kafka
3. Test recurring task: create recurring task → complete it → verify next task created
4. Test reminder: create task with remind_at → verify Dapr job scheduled → verify reminder event triggered
5. Test WebSocket sync: create task → verify all connected clients receive update
6. Test audit log: perform task operations → verify all recorded in audit table
7. Test observability: verify Prometheus scrapes metrics, logs appear in Loki, traces visible in tracing UI

### 3.2 Production Deployment Testing

1. Deploy to cloud Kubernetes cluster (AKS/GKE/OKE)
2. Verify same test scenarios work with production Kafka and managed services
3. Load test: simulate 1000 concurrent users
4. Verify latency < 500ms p95
5. Verify zero event loss on service restart
6. Test secrets rotation (credentials change without pod restart)
7. Verify multi-replica scaling (scale up/down, verify no data loss)

### 3.3 Integration Tests

**Test scenarios**:
1. End-to-end task creation: user creates task → API returns → event published → consumers process
2. Recurring task generation: complete recurring task → next task auto-created → visible in UI
3. Reminder delivery: create task with reminder → reminder triggers at exact time → notification sent
4. Real-time sync: create task on client A → immediately visible on client B via WebSocket
5. Audit trail: all task operations logged with user_id and timestamp

---

## Constitution Check

✅ **Spec-Driven Development**: Plan derived from approved spec; implementation will follow this plan precisely

✅ **Agentic Workflow**: Backend agent builds Core Todo and consumer services; Frontend agent builds UI; Database agent designs schema; no manual coding

✅ **Security-First Design**: User isolation enforced via JWT token in every Dapr service; task ownership checked on every operation

✅ **Deterministic Behavior**: Event-driven architecture ensures consistent state; Kafka provides ordering per partition

✅ **Full-Stack Coherence**: Frontend consumes exact API schema; backend enforces user isolation; database normalized per schema

✅ **Traceability**: All prompts recorded in PHRs; implementation decisions documented in ADRs as needed

---

## Success Criteria Mapping

| Success Criteria | Implementation Phase | Validation |
|------------------|---------------------|-----------|
| SC-001: 5-min Minikube deployment | Phase 2.5 (Helm) | Deploy and time |
| SC-002: Identical Helm charts prod-ready | Phase 2.5 | Deploy to cloud with same charts |
| SC-003: Recurring task < 2 sec | Phase 2.3 (consumer logic) | Integration test |
| SC-004: Reminder ±5 sec precision | Phase 2.3 (Dapr Jobs) | Integration test |
| SC-005: 1000 concurrent users, p95 < 500ms | Phase 3.2 | Load test |
| SC-006: Zero Kafka consumer lag | Phase 3 | Prometheus metrics |
| SC-007: CI/CD < 10 min | Phase 2.7 | GitHub Actions pipeline |
| SC-008: 99.9% uptime | Phase 3 | Availability monitoring |
| SC-009: Distributed trace complete | Phase 2.8 | OpenTelemetry trace view |
| SC-010: Zero event loss on restart | Phase 3 | Chaos test |
| SC-011: WebSocket updates < 500ms | Phase 2.4 | Integration test |
| SC-012: Search < 1 sec (100K tasks) | Phase 3 | Database query optimization |
| SC-013: IaC version-controlled | Phase 2.5/2.7 | Git audit |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Dapr complexity | Medium | High | Start with simple PubSub, extend incrementally |
| Kafka broker downtime | Low | High | Local Minikube testing before cloud; health checks |
| Event loss on restart | Low | High | Kafka persistence + consumer offset management |
| Clock skew in reminders | Low | Medium | Use server timestamp from Dapr Jobs API |
| Consumer ordering issues | Medium | Medium | Use single partition per user_id for ordered delivery |
| WebSocket connection drop | Medium | Low | Implement reconnection logic with exponential backoff |

---

## Rollout Plan

1. **Week 1-2**: Schema extension, Core Todo enhancement, Phase 0 research complete
2. **Week 2-3**: Microservices implementation (Recurring Task, Notification, Audit Log, WebSocket Sync)
3. **Week 3-4**: Helm charts, Dapr configuration, GitHub Actions pipeline
4. **Week 4**: Local Minikube deployment and testing
5. **Week 5**: Cloud deployment (AKS/GKE/OKE) and production validation
6. **Week 5-6**: Final observability tuning, load testing, documentation

---

## Next Steps

1. Review and approve this plan
2. Generate detailed implementation tasks (`.md files for each phase)
3. Assign tasks to Backend, Frontend, Database, and DevOps agents
4. Begin Phase 1 implementation: Database schema extension
5. Create Architectural Decision Records (ADRs) for significant decisions

---

## Open Questions for Review

1. **Kafka broker strategy**: Should we use Strimzi locally + managed service in production, or consistent self-hosted everywhere?
2. **Audit log storage**: Should audit logs go to separate database or same Neon instance?
3. **WebSocket scaling**: Single instance WebSocket service or sticky session load balancing?
4. **Production cloud platform**: Final decision on AKS vs GKE vs Oracle OKE?
5. **Notification delivery**: Should placeholder notification service log to stdout, or integrate with a mock service?
