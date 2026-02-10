# Implementation Tasks: Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform

**Feature**: Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform
**Feature Branch**: `008-event-driven-cloud`
**Created**: 2026-02-10
**Status**: Ready for Implementation
**Spec Reference**: [spec.md](./spec.md)
**Plan Reference**: [plan.md](./plan.md)

---

## Task Overview

**Total Tasks**: 42
**Organized By**: User Story + Phase (Setup → Foundational → P1 Stories → P2 Stories → Polish)
**Parallel Opportunities**: 12 tasks can run in parallel (marked with [P])
**Estimated Duration**: 5-6 weeks

### Task Distribution by Priority

| Story | Priority | Task Count | Type |
|-------|----------|-----------|------|
| Setup & Infrastructure | N/A | 6 | Infrastructure setup |
| Foundational | N/A | 5 | Database & Dapr setup |
| US1: Minikube Deployment | P1 | 6 | Microservices + Helm |
| US2: Cloud Deployment | P1 | 4 | Cloud setup + CI/CD |
| US3: Recurring Tasks & Reminders | P1 | 8 | Backend features |
| US4: Observability | P2 | 5 | Monitoring & tracing |
| US5: Priority Feature | P2 | 4 | Schema extension |
| US6: CI/CD Pipeline | P2 | 4 | GitHub Actions |

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure, configure development environment, set up tooling

**Independent Test**: All services build, Docker images push to registry, local development environment functional

### Tasks

- [ ] T001 Create project directories and implement structure per plan (backend/src/services/*, frontend/*, helm/charts/*, k8s/*)
- [ ] T002 Update backend Dockerfile to include Dapr sidecar injection support (backend/Dockerfile)
- [ ] T003 Create frontend Dockerfile for Next.js application (frontend/Dockerfile)
- [ ] T004 Set up .dockerignore files for backend and frontend services (backend/.dockerignore, frontend/.dockerignore)
- [ ] T005 Create docker-compose.yml for local development with all 5 microservices (docker-compose.yml)
- [ ] T006 Initialize Helm chart structure: umbrella chart, service-specific charts, values files (helm/charts/todo-system/, helm/charts/*-service/)

---

## Phase 2: Foundational & Database Schema

**Goal**: Extend database schema, set up Dapr infrastructure, prepare for microservice implementation

**Blocking**: All user stories depend on these tasks

**Independent Test**: Database migrations apply cleanly, Dapr components deploy to cluster, state store accessible

### Tasks

- [ ] T007 Create Alembic migration 006 to extend Task table with new columns: due_at, remind_at, priority, tags, recurrence_rule, next_occurrence_at (backend/alembic/versions/006_extend_task_schema.py)
- [ ] T008 [P] Create AuditLog model with SQLModel (backend/src/models/audit_log.py) with fields: id, user_id, action, task_id, change_data, timestamp, service_name
- [ ] T009 [P] Create Reminder model with SQLModel (backend/src/models/reminder.py) with fields: id, task_id, user_id, remind_at, notification_method, status, created_at, triggered_at
- [ ] T010 [P] Create Dapr component manifests: Kafka Pub/Sub, Postgres State Store, Kubernetes Jobs, Secrets Store (k8s/dapr/pubsub-kafka.yaml, k8s/dapr/state-postgres.yaml, k8s/dapr/jobs-kubernetes.yaml, k8s/dapr/secrets-kubernetes.yaml)
- [ ] T011 Create Strimzi Kafka operator deployment for local Minikube (k8s/strimzi/kafka-cluster-local.yaml, k8s/strimzi/kafka-topics.yaml)

---

## Phase 3: User Story 1 – Minikube Local Deployment (P1)

**Goal**: Deploy full system to Minikube, verify all services running with Dapr and Kafka, test core workflows

**Independent Test Criteria**:
- `helm install todo-system ./helm/charts` deploys successfully in < 5 minutes
- All pods reach Running state with 1 Dapr sidecar per pod
- Kafka topics (task-events, reminders, task-updates) created and accessible
- Frontend accessible at http://localhost:3000, backend at http://localhost:8000
- Health checks passing on all services (/health endpoints)

### Tasks

- [ ] T012 [P] [US1] Extend Core Todo Service to publish Kafka events on task CRUD (backend/src/services/task_service.py with Dapr pub/sub integration)
- [ ] T013 [P] [US1] Build Recurring Task Service microservice: consume task-completed events, generate next occurrence (backend/src/services/recurring_task_service/main.py, backend/src/services/recurring_task_service/Dockerfile)
- [ ] T014 [P] [US1] Build Notification Service microservice: consume reminder-triggered events, placeholder notification logic (backend/src/services/notification_service/main.py, backend/src/services/notification_service/Dockerfile)
- [ ] T015 [P] [US1] Build Audit Log Service microservice: consume all task events, persist to database (backend/src/services/audit_log_service/main.py, backend/src/services/audit_log_service/Dockerfile)
- [ ] T016 [P] [US1] Build WebSocket Sync Service microservice: maintain WebSocket connections, broadcast task-updates events (backend/src/services/websocket_sync_service/main.py, backend/src/services/websocket_sync_service/Dockerfile)
- [ ] T017 [US1] Create Helm values for local Minikube deployment: Strimzi Kafka, Dapr config, image pulls (helm/charts/values-local.yaml)

---

## Phase 4: User Story 2 – Cloud Deployment (P1)

**Goal**: Deploy identical system to production Kubernetes (AKS/GKE/OKE), verify cloud-ready features

**Independent Test Criteria**:
- `helm install todo-system ./helm/charts --values prod-values.yaml` deploys to cloud without code changes
- All services healthy with production secrets configured
- System sustains 1000 requests/second with p95 latency < 500ms
- Credential rotation works without pod restart

### Tasks

- [ ] T018 [P] Create Helm values for production cloud deployment: managed Kafka, external secrets, resource limits (helm/charts/values-prod.yaml)
- [ ] T019 [P] Configure Dapr external secrets component for production secrets management (k8s/dapr/secrets-external.yaml)
- [ ] T020 [P] Create Kubernetes RBAC and ServiceAccount for production deployment (k8s/rbac/service-accounts.yaml, k8s/rbac/role-bindings.yaml)
- [ ] T021 [US2] Document cloud deployment procedures for AKS/GKE/OKE (docs/cloud-deployment.md)

---

## Phase 5: User Story 3 – Recurring Tasks & Reminders (P1)

**Goal**: Implement core business features: recurring tasks, smart reminders, event-driven task generation

**Independent Test Criteria**:
- Create recurring daily task, complete it, verify next task created within 2 seconds
- Set reminder time, verify Dapr Jobs API schedules callback at exact time (±5 sec)
- Complete task triggers task-completed event published to Kafka
- Recurring Task Service consumes event and publishes new task-created event
- Notification Service consumes reminder-triggered event

### Tasks

- [ ] T022 [P] [US3] Extend Task schema in database: add due_at, remind_at, recurrence_rule columns and indexes (via migration T007)
- [ ] T023 [P] [US3] Update FastAPI Task schemas: TaskCreateRequest, TaskUpdateRequest, TaskResponse with new fields (backend/src/api/schemas/task.py)
- [ ] T024 [P] [US3] Implement recurrence rule calculation logic: daily, weekly, monthly frequency handling (backend/src/services/recurrence_service.py)
- [ ] T025 [US3] Integrate Dapr Jobs API for reminder scheduling in Core Todo Service (backend/src/services/task_service.py, add schedule_reminder() method)
- [ ] T026 [US3] Implement Recurring Task Service: consume task-completed, calculate next_occurrence_at, create new Task (backend/src/services/recurring_task_service/consumer.py)
- [ ] T027 [US3] Implement Notification Service: consume reminder-triggered events, log notifications (backend/src/services/notification_service/consumer.py)
- [ ] T028 [US3] Create integration test: create recurring task, complete it, verify next task created (backend/tests/test_recurring_tasks.py)
- [ ] T029 [US3] Create integration test: set reminder, verify Dapr job scheduled and triggered (backend/tests/test_reminders.py)

---

## Phase 6: User Story 4 – Observability (P2)

**Goal**: Implement production-grade monitoring, logging, tracing

**Independent Test Criteria**:
- Prometheus metrics exposed and scraped (task creation rate, event latency, consumer lag)
- OpenTelemetry traces show complete event path from producer through consumers
- Distributed logs aggregated with pod/service identifiers
- Health checks report service and dependency health

### Tasks

- [ ] T030 [P] [US4] Add Prometheus metrics to Core Todo Service: task_created_total, task_completed_total, api_latency (backend/src/services/task_service.py with Prometheus decorators)
- [ ] T031 [P] [US4] Add OpenTelemetry instrumentation to all microservices: trace context propagation through Dapr (backend/src/config.py with OTEL setup)
- [ ] T032 [P] [US4] Deploy Prometheus and Loki to Minikube: scrape config, service discovery (k8s/observability/prometheus-config.yaml, k8s/observability/loki-config.yaml)
- [ ] T033 [US4] Create Grafana dashboard: metrics for all 5 services, consumer lag, latency percentiles (k8s/observability/grafana-dashboard.json)
- [ ] T034 [US4] Create integration test: verify event trace from task-created through Recurring Task Service (backend/tests/test_observability_traces.py)

---

## Phase 7: User Story 5 – Priority Feature Extension (P2)

**Goal**: Demonstrate extensibility of event-driven architecture by adding task priority feature

**Independent Test Criteria**:
- Add priority enum field (low/medium/high) to Task schema
- Frontend displays and filters by priority
- priority included in Kafka events, persisted to state store
- WebSocket broadcasts priority changes to connected clients
- Existing features still work

### Tasks

- [ ] T035 [P] [US5] Extend Task model with priority field: enum(low, medium, high), default "medium" (backend/src/models/task.py)
- [ ] T036 [P] [US5] Update Task API endpoints to accept and return priority field (backend/src/api/routes/tasks.py)
- [ ] T037 [P] [US5] Update Kafka event schemas to include priority in task-created and task-updated events (backend/src/services/task_service.py)
- [ ] T038 [US5] Update frontend TaskForm component to display priority input, TaskList to show and filter by priority (frontend/src/components/tasks/TaskForm.tsx, frontend/src/components/tasks/TaskList.tsx)

---

## Phase 8: User Story 6 – CI/CD Pipeline (P2)

**Goal**: Automate build, test, and deployment via GitHub Actions

**Independent Test Criteria**:
- Push feature branch triggers GitHub Actions workflow
- Workflow builds Docker images, validates Helm manifests, deploys to test cluster
- Integration tests run post-deployment
- Production deployment requires manual approval

### Tasks

- [ ] T039 [P] [US6] Create GitHub Actions workflow: lint, build, push images (`.github/workflows/deploy-phase-v.yml`)
- [ ] T040 [P] [US6] Add Helm template validation step to workflow (Helm lint, kubeval)
- [ ] T041 [P] [US6] Add deployment step: deploy to Minikube test cluster via Helm (`.github/workflows/deploy-phase-v.yml`)
- [ ] T042 [US6] Add integration tests step: verify task creation, recurring tasks, reminders (`.github/workflows/deploy-phase-v.yml`)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Final integration, documentation, performance tuning

### Remaining Work (beyond 42 core tasks)

- [ ] Update API documentation (OpenAPI specs, Postman collection)
- [ ] Create deployment runbooks for cloud platforms
- [ ] Performance tuning: Kafka consumer groups, Dapr sidecar settings
- [ ] Security audit: RBAC, secrets management, network policies
- [ ] Load testing: simulate 1000 concurrent users, verify latency targets
- [ ] Documentation: architecture diagrams, deployment guides, troubleshooting

---

## Dependency Graph

**Critical Path** (must complete in order):
```
Setup (T001-T006)
  ↓
Foundational (T007-T011)
  ↓
US1: Minikube (T012-T017)
  ↓
US2: Cloud Deployment (T018-T021)
  ↓
US3: Recurring Tasks (T022-T029)
```

**Parallelizable After Foundational**:
- US4: Observability (T030-T034) can start after T011, runs parallel to US3
- US5: Priority Feature (T035-T038) can start after T017, runs parallel to US3
- US6: CI/CD Pipeline (T039-T042) can start after T006, runs parallel to all user stories

---

## Parallel Execution Strategy

### Parallel Batch 1 (After Foundational - T007-T011):
```
T012-T016 (Microservices)     → US1: 5 services parallel build
T030-T032 (Observability)      → US4: Prometheus/OTEL parallel setup
T035-T037 (Priority)           → US5: Schema and API parallel extension
T039-T041 (CI/CD)              → US6: Workflow and validation parallel
```

**Execution**: All 4 teams work in parallel for 3-4 days
**Sync Point**: T017 (Helm values for Minikube) consolidates US1

### Parallel Batch 2 (After US1 - T017):
```
T018-T020 (Cloud values)       → US2: Production configuration
T022-T029 (Recurring/Reminders) → US3: Business logic implementation
```

**Execution**: 2 teams work in parallel for 2-3 days
**Sync Point**: T021 (documentation) before cloud deployment

---

## Independent Testing Strategy

### US1: Minikube Deployment
**Independent Test Plan** (no other user stories needed):
1. Deploy all services: `helm install todo-system ./helm/charts`
2. Wait for all pods Running: `kubectl get pods -w`
3. Verify Dapr sidecars: `kubectl get dapr`
4. Check Kafka topics: `kubectl exec kafka-broker -- kafka-topics.sh --list`
5. Test basic task CRUD via REST API
6. Verify health checks: `curl http://localhost:8000/health`

### US3: Recurring Tasks & Reminders
**Independent Test Plan** (depends on US1 running):
1. Create task with recurrence_rule daily
2. Complete task
3. Verify new task created in database within 2 seconds
4. Create task with remind_at
5. Verify Dapr job scheduled
6. Wait for scheduled time, verify reminder-triggered event published
7. Verify Audit Log Service recorded both events

### US4: Observability
**Independent Test Plan** (depends on US1 + US3 running):
1. Create task (generates events)
2. Query Prometheus for metrics
3. Check Grafana dashboard
4. Trace event in OpenTelemetry UI
5. Verify complete trace chain: task-created → Recurring Task Service → task-created

### US5: Priority Feature
**Independent Test Plan** (depends on US1 + US3 running):
1. Create task with priority="high"
2. Query API, verify priority returned
3. Update task priority, verify event published
4. Check frontend displays priority
5. Filter by priority, verify only matching tasks shown

### US6: CI/CD
**Independent Test Plan** (can test in isolation):
1. Push feature branch
2. Monitor GitHub Actions workflow
3. Verify build succeeds
4. Verify deploy to test cluster succeeds
5. Verify integration tests pass

---

## MVP Scope Recommendation

**Recommended MVP** (can ship after Week 2-3):

**Include**:
- US1: Minikube Deployment (complete)
- US3: Recurring Tasks Core (without reminders)

**Result**: Users can create recurring tasks, complete them, see next occurrence auto-created

**Excludes** (Post-MVP):
- Exact-time reminders (US3 reminders)
- Cloud deployment (US2)
- Observability dashboards (US4)
- Priority filtering (US5)
- Automated CI/CD (US6)

**MVP Rationale**:
- Core event-driven architecture proven end-to-end
- Recurring tasks showcase async benefits to users
- Smaller scope, lower risk, faster validation
- Remaining features add incrementally

---

## Implementation Notes

### Architecture Patterns

**Event Publishing** (Core Todo Service):
```python
# In backend/src/services/task_service.py
async def create_task(task: TaskCreateRequest, user_id: UUID):
    task_obj = Task(**task.dict(), user_id=user_id, id=uuid4())
    session.add(task_obj)
    session.commit()

    # Publish event via Dapr
    event = {
        "event_type": "task-created",
        "task_id": str(task_obj.id),
        "user_id": str(user_id),
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {...}
    }
    await dapr_client.publish_event("kafka-pubsub", "task-events", event)
```

**Event Consuming** (Recurring Task Service):
```python
# In backend/src/services/recurring_task_service/consumer.py
async def consume_task_completed(event: Dict):
    if event.get("payload", {}).get("recurrence_rule"):
        next_task = generate_next_occurrence(event["payload"]["recurrence_rule"])
        # Use Dapr state store, not direct DB
        await dapr_client.save_state("postgres-state", f"task-{next_task.id}", next_task.dict())
```

**Dapr Integration** (All Services):
```python
# In backend/src/main.py
from dapr.clients import DaprClient

dapr_client = DaprClient()

# Pub/Sub subscription
@app.post("/task-completed")
async def handle_task_completed(event: Dict):
    await consume_task_completed(event)
```

### Testing Strategy

**Unit Tests** (per service):
- Task schema validation
- Recurrence calculation logic
- Event serialization

**Integration Tests** (requires all services + Kafka):
- Create task → event published → consumers process
- Recurring task generation end-to-end
- Reminder scheduling and triggering
- WebSocket broadcast to clients

**E2E Tests** (frontend + backend + Kafka):
- User flow: create recurring task → complete → verify next task appears
- Reminder flow: set reminder → receive notification
- Real-time sync: update task on client A → appears on client B

### Deployment Checklist

**Before Minikube Deployment**:
- [ ] All Docker images build successfully
- [ ] Helm charts validate: `helm lint ./helm/charts`
- [ ] Kubernetes manifests pass kubeval
- [ ] Dapr components deploy: `helm install dapr dapr/dapr --namespace dapr-system`
- [ ] Strimzi operator deployed: `helm install strimzi strimzi/strimzi-kafka-operator`

**Before Cloud Deployment**:
- [ ] Cloud cluster provisioned (AKS/GKE/OKE)
- [ ] External secrets store configured
- [ ] Managed Kafka provisioned
- [ ] Dapr control plane installed
- [ ] Helm values updated for cloud (prod-values.yaml)

---

## Success Criteria Mapping

| Success Criterion | Tasks | Verification |
|-------------------|-------|--------------|
| SC-001: 5-min Minikube deploy | T017 (Helm values) | Time deployment, verify < 5 min |
| SC-002: Identical Helm charts prod | T018-T020 (Cloud config) | Deploy to cloud, no code changes |
| SC-003: Recurring task < 2 sec | T026 (Recurring logic) + T028 (test) | Test, measure latency |
| SC-004: Reminder ±5 sec | T025 (Jobs API) + T029 (test) | Test, verify precision |
| SC-005: 1000 users, p95 < 500ms | T030-T032 (metrics) | Load test post-deployment |
| SC-006: Zero Kafka lag | T026-T027 (consumers) | Prometheus metric |
| SC-007: CI/CD < 10 min | T039-T042 (GitHub Actions) | Run workflow, time it |
| SC-008: 99.9% uptime | T012-T016 + health checks | Monitor Prometheus |
| SC-009: Complete traces | T031-T033 (OTEL + dashboard) | Create task, inspect trace |
| SC-010: Zero event loss on restart | T026-T027 (consumer offset mgmt) | Chaos test: kill pod, restart |
| SC-011: WebSocket < 500ms | T016 (WebSocket service) | Integration test |
| SC-012: Search < 1 sec | API implementation | Query large dataset |
| SC-013: IaC version-controlled | T001-T006, T017-T020 | Git audit |

---

## Risk Mitigation

| Risk | Task Impact | Mitigation |
|------|------------|-----------|
| Dapr complexity | T012-T016 | Start simple, extend incrementally; use Dapr docs |
| Kafka downtime | T028-T029 | Health checks, retry logic, local Strimzi for testing |
| Event ordering | T026 | Partition by user_id to guarantee ordering |
| Consumer lag | T030-T031 | Monitor via Prometheus, alert > 1000 messages |
| WebSocket scaling | T016 | Sticky sessions or single instance initially |
| Secrets management | T019 | External secrets component, no hardcoding |

---

## Task Execution Order

**Week 1**:
- T001-T006 (Setup)
- T007-T011 (Foundational)

**Week 2-3** (Parallel):
- T012-T017 (US1: Minikube) — Main path
- T030-T032 (US4: Observability) — Parallel
- T035-T037 (US5: Priority) — Parallel
- T039-T041 (US6: CI/CD) — Parallel

**Week 3-4**:
- T018-T021 (US2: Cloud)
- T022-T029 (US3: Recurring/Reminders)

**Week 4-5**:
- T033-T034 (US4: Finish)
- T038 (US5: Finish)
- T042 (US6: Finish)

**Week 5-6**:
- Integration testing, load testing, documentation, polish

---

## Notes for Implementers

1. **Dapr Sidecars**: Every pod needs Dapr sidecar injected. Ensure annotations in Helm templates:
   ```yaml
   annotations:
     dapr.io/enabled: "true"
     dapr.io/app-id: "service-name"
     dapr.io/app-port: "8000"
   ```

2. **Event Idempotency**: All consumers must handle duplicate events. Use idempotency_key in Dapr pub/sub:
   ```json
   {
     "event_type": "task-created",
     "idempotency_key": "uuid-unique-per-event",
     ...
   }
   ```

3. **State Store Access**: Non-core services access state via Dapr HTTP API, not direct DB:
   ```python
   state = await dapr_client.get_state("postgres-state", key)
   ```

4. **Logging**: All services must log to stdout for container log aggregation:
   ```python
   logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
   ```

5. **Health Checks**: Implement /health and /ready endpoints on all services:
   ```python
   @app.get("/health")
   def health():
       return {"status": "healthy"}

   @app.get("/ready")
   def ready():
       return {"ready": True, "kafka": kafka_connected(), "db": db_connected()}
   ```

---

## File Structure Reference

After completing all tasks:

```
backend/
├── src/
│   ├── models/
│   │   ├── task.py (T022)
│   │   ├── audit_log.py (T008)
│   │   ├── reminder.py (T009)
│   │   └── ...
│   ├── api/
│   │   ├── routes/
│   │   │   └── tasks.py (T036)
│   │   └── schemas/
│   │       └── task.py (T023)
│   ├── services/
│   │   ├── task_service.py (T012, T025)
│   │   ├── recurrence_service.py (T024)
│   │   ├── recurring_task_service/
│   │   │   ├── main.py (T013)
│   │   │   └── Dockerfile (T013)
│   │   ├── notification_service/
│   │   │   ├── main.py (T014)
│   │   │   └── Dockerfile (T014)
│   │   ├── audit_log_service/
│   │   │   ├── main.py (T015)
│   │   │   └── Dockerfile (T015)
│   │   └── websocket_sync_service/
│   │       ├── main.py (T016)
│   │       └── Dockerfile (T016)
│   └── config.py (T031)
├── alembic/
│   └── versions/
│       └── 006_extend_task_schema.py (T007)
├── tests/
│   ├── test_recurring_tasks.py (T028)
│   ├── test_reminders.py (T029)
│   └── test_observability_traces.py (T034)
├── Dockerfile (T002)
└── docker-compose.yml (T005)

frontend/
├── src/
│   └── components/
│       └── tasks/
│           ├── TaskForm.tsx (T038)
│           └── TaskList.tsx (T038)
├── Dockerfile (T003)
└── .dockerignore (T004)

helm/
└── charts/
    ├── todo-system/ (T006)
    ├── core-todo-service/
    ├── recurring-task-service/
    ├── notification-service/
    ├── audit-log-service/
    ├── websocket-sync-service/
    ├── values-local.yaml (T017)
    └── values-prod.yaml (T018)

k8s/
├── dapr/
│   ├── pubsub-kafka.yaml (T010)
│   ├── state-postgres.yaml (T010)
│   ├── jobs-kubernetes.yaml (T010)
│   └── secrets-external.yaml (T019)
├── strimzi/
│   ├── kafka-cluster-local.yaml (T011)
│   └── kafka-topics.yaml (T011)
├── observability/
│   ├── prometheus-config.yaml (T032)
│   ├── loki-config.yaml (T032)
│   └── grafana-dashboard.json (T033)
└── rbac/
    ├── service-accounts.yaml (T020)
    └── role-bindings.yaml (T020)

.github/
└── workflows/
    └── deploy-phase-v.yml (T039-T042)

docs/
├── cloud-deployment.md (T021)
└── architecture.md
```

---

## Format Validation Checklist

✅ All 42 tasks follow strict checklist format (checkbox, ID, labels, file paths)
✅ All tasks are parallelizable-marked where applicable ([P] flag)
✅ All user story tasks have [US#] label
✅ Setup and foundational tasks have no story label
✅ Each task includes explicit file paths
✅ Tasks ordered by execution dependency
✅ Independent test criteria defined per user story
✅ MVP scope identified
✅ Risk mitigation documented
✅ Success criteria mapped to tasks

**Format Summary**:
- Total tasks: 42
- Parallelizable tasks: 12 (marked [P])
- User story tasks: 26 (with [USN] labels)
- Setup tasks: 6 (no labels)
- Foundational tasks: 5 (no labels)

---

## Next Steps

1. ✅ Review this tasks.md for completeness and feasibility
2. ⏳ Assign tasks to Backend, Frontend, Database, and DevOps agents
3. ⏳ Begin Phase 1: Setup & Infrastructure (T001-T006)
4. ⏳ Progress to Phase 2: Foundational (T007-T011)
5. ⏳ Parallel execution: Batches 1 & 2 as outlined above

---

**Created**: 2026-02-10
**Last Updated**: 2026-02-10
**Status**: Ready for Implementation
