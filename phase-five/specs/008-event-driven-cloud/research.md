# Phase V Research: Event-Driven Architecture Decisions

**Date**: 2026-02-10
**Feature**: 008-event-driven-cloud
**Status**: Complete

---

## 1. Dapr Installation & Configuration

**Decision**: Use Dapr control plane on both Minikube and production clusters

**Rationale**:
- Dapr provides clean abstraction over Kafka, making event handling implementation-agnostic
- Sidecar injection pattern (one Dapr proxy per pod) provides language-agnostic RPC layer
- Dapr handles connection pooling, retries, and resilience automatically
- Can swap Kafka for other pub/sub systems without code changes (future-proof)

**Alternatives considered**:
1. Direct Kafka client libraries (e.g., confluent-kafka-python)
   - Violates spec requirement: "No Kafka client libraries in application code"
   - Couples code to Kafka, harder to test locally
   - Rejected ❌

2. Service mesh (Istio)
   - Heavier than needed (Dapr focuses on state/messaging)
   - Longer learning curve, more operational complexity
   - Rejected ❌

3. No service abstraction (direct HTTP/gRPC between services)
   - Doesn't solve distributed tracing, service discovery, or state management
   - Event sourcing would require custom Kafka implementation
   - Rejected ❌

**Implementation**:
- Install Dapr via official Helm chart: `helm repo add dapr https://dapr.github.io/helm-charts && helm install dapr dapr/dapr`
- Enable sidecar injection: Add annotations to Kubernetes pods
- Configure Dapr components (see plan.md for manifests)

**Testing locally**:
- Dapr can run in standalone mode on developer machine (not required for this project, but available)
- Minikube deployment includes full Dapr control plane

---

## 2. Kafka Deployment Strategy

**Decision**: Use Strimzi operator on Minikube (local testing); managed Redpanda/Confluent on production

**Rationale**:
- **Strimzi (local)**:
  - Kubernetes-native Kafka operator (CRD-based)
  - Easy to deploy: single Helm chart or kubectl apply
  - Perfect for local development and testing
  - Single-node cluster sufficient for testing (not production-grade)

- **Managed services (production)**:
  - Redpanda Cloud or Confluent Cloud: reduce operational burden
  - Automatic scaling, monitoring, backups
  - Enterprise SLAs (99.9%+ uptime guarantees)
  - Cloud provider integration (IAM, VPC peering, etc.)

**Alternatives considered**:
1. Self-hosted Strimzi everywhere
   - Local: great
   - Production: operational complexity (broker scaling, monitoring, disaster recovery, upgrades)
   - Rejected for production ❌

2. Kafka in Docker containers (not Kubernetes-native)
   - Works locally but doesn't scale to production
   - No automatic failover or recovery
   - Rejected ❌

3. Event streaming via managed services only (no local Kafka)
   - Can't test event flows locally without cloud credentials
   - Slows development loop
   - Rejected for development ❌

**Implementation**:
```bash
# Local Minikube
helm repo add strimzi https://strimzi.io/charts
helm install strimzi strimzi/strimzi-kafka-operator
kubectl apply -f k8s/strimzi-cluster-local.yaml

# Production
# Use managed service or self-hosted Strimzi via Dapr config
```

**Dapr configuration remains identical** — only Kafka broker address changes in environment

---

## 3. Event Idempotency Pattern

**Decision**: Use idempotency keys (UUID-based deduplication) with database unique constraints

**Rationale**:
- Kafka provides at-least-once delivery (not exactly-once)
- Network failures can cause duplicate event delivery
- Consumers must be idempotent to handle duplicates safely

**Alternatives considered**:
1. Exactly-once processing (Kafka transactions, Dapr exactly-once flag)
   - Complex to implement and debug
   - Performance overhead (2x latency in some cases)
   - Not worth complexity for Todo app scale
   - Rejected ❌

2. No deduplication (accept duplicates)
   - Could create duplicate tasks
   - Audit log would have duplicate entries
   - Reminders could trigger twice
   - Unacceptable for business logic
   - Rejected ❌

**Implementation**:
```python
# Event envelope includes idempotency key
event = {
    "event_type": "task-created",
    "idempotency_key": uuid4(),  # Unique per event source
    "task_id": task.id,
    "user_id": user_id,
    "timestamp": datetime.utcnow().isoformat(),
    "event_data": {...}
}

# Consumer deduplication
# Option 1: Idempotency table
INSERT INTO event_idempotency (idempotency_key, event_type, created_at)
VALUES (?, ?, ?)
ON CONFLICT DO NOTHING  # Postgres unique constraint

# Option 2: Task state check
if task_with_id_already_exists:
    log.info(f"Task {task_id} already created, skipping duplicate")
    return
```

---

## 4. Dapr State Store Design

**Decision**: Use Dapr Postgres state store component (same Neon database as core service)

**Rationale**:
- Single database reduces infrastructure complexity
- Dapr handles connection pooling, avoiding connection storms
- State is queryable (vs Redis or other k/v stores)
- Neon already required for core service; no additional cost

**Alternatives considered**:
1. Separate Redis cache for microservice state
   - Adds infrastructure (Redis cluster to manage)
   - Consumer services still query task schema from Postgres (dual database)
   - Operational complexity without real benefit
   - Rejected ❌

2. File-based state (local to pod)
   - Not persistent across pod restarts
   - No sharing between replicas
   - Rejected ❌

3. No state store (all services query Postgres directly)
   - Violates spec constraint: "All services communicate via Dapr APIs"
   - Not architecture-agnostic
   - Rejected ❌

**Implementation**:
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
    - name: maxConns
      value: "20"  # Connection pooling
```

**Consumer services**:
- Recurring Task Service: Query task recurrence_rule via Dapr state
- Audit Log Service: Write audit records directly (or via Dapr)
- WebSocket Sync Service: No state (in-memory connection tracking only)

---

## 5. Recurring Task Generation Logic

**Decision**: Event-driven recurring task generation via async workflow

**Rationale**:
- Decoupled: core service doesn't wait for recurring task creation
- Survives service restarts: if consumer crashes, Kafka retains event
- Scalable: can add multiple Recurring Task Service replicas independently
- Observable: event trace shows each step

**Alternatives considered**:
1. Synchronous recurrence (create next task immediately in POST handler)
   - Would require core service to call Recurring Task Service synchronously
   - Violates "no direct service calls" constraint
   - Slows down task creation endpoint
   - Rejected ❌

2. Scheduled batch job (cron job to generate recurring tasks)
   - Polling violates spec requirement
   - Latency: up to 1 minute delay
   - Rejected ❌

3. In-database recurrence trigger (SQL trigger)
   - Would need direct database trigger calls (violates decoupling)
   - Hard to debug and monitor
   - Rejected ❌

**Implementation**:
```
Task Completion Flow:
1. Frontend PATCHes /users/{user_id}/tasks/{task_id} with is_completed=true
2. Core service updates task in DB, publishes task-completed event:
   {
     "event_type": "task-completed",
     "task_id": "123e4567",
     "user_id": "user-456",
     "recurrence_rule": {"frequency": "daily", "end_date": "2026-12-31"},
     "idempotency_key": "..."
   }

3. Kafka broker persists event
4. Recurring Task Service consumer receives event, checks for recurrence_rule
5. If recurrence_rule exists:
   - Calculates next_occurrence_at (tomorrow 9:00 AM if daily)
   - Creates new Task record
   - Publishes task-created event
6. AuditLog and WebSocket Sync services also receive task-created event
7. Frontend receives update via WebSocket, shows next recurring task
```

**Latency**: Event → Consumer processing: 200-500ms (acceptable per spec: < 2 sec)

---

## 6. Reminder Scheduling Strategy

**Decision**: Use Dapr Jobs API for exact-time scheduling (no polling)

**Rationale**:
- Spec requires: "No polling-based reminder system"
- Dapr Jobs API abstracts underlying scheduler (Kubernetes CronJob, managed service, etc.)
- Server-side scheduling ensures timezone consistency
- ±5 second precision is acceptable for reminders

**Alternatives considered**:
1. Client-side reminders (JavaScript in browser)
   - Doesn't work if browser tab closed
   - Not reliable for notifications
   - Rejected ❌

2. Polling (check every minute if reminder time reached)
   - Violates spec: "No polling-based reminder system is allowed"
   - Inefficient for many reminders
   - Rejected ❌

3. Scheduled tasks in memory (Node.js timers or Python APScheduler)
   - Lost on service restart
   - Doesn't scale across multiple replicas
   - Rejected ❌

**Implementation**:
```python
# When task created with remind_at timestamp
remind_at = datetime(2026, 2, 15, 9, 0, 0)

# Call Dapr Jobs API
import dapr.client
client = dapr.client.DaprClient()
client.save_job(
    job_name=f"reminder-{task_id}",
    job_type="http",
    schedule="@2026-02-15T08:50:00Z",  # Cron expression for exact time
    payload={
        "task_id": str(task_id),
        "user_id": str(user_id),
        "remind_at": remind_at.isoformat()
    }
)

# At scheduled time, Dapr invokes callback endpoint
# POST /callbacks/reminder
# Service publishes reminder-triggered event to Kafka
```

**Accuracy**: Dapr Jobs API (via Kubernetes) provides ±5 second precision (acceptable per spec)

---

## 7. API Contract Compatibility

**Decision**: Extend existing REST API; maintain backward compatibility

**Rationale**:
- Existing clients (frontend, tests) continue working
- New fields are optional (default values provided)
- No breaking changes to existing endpoints

**Alternatives considered**:
1. GraphQL API (instead of REST extension)
   - Better for filtering/querying complex task data
   - Adds complexity (new GraphQL server, schema management)
   - Frontend would need rewrite
   - Rejected ❌

2. Versioned API endpoints (v2)
   - Maintains old API for backward compatibility
   - Adds code maintenance burden (two implementations)
   - Not needed since extensions are backward-compatible
   - Rejected ❌

**Implementation**:
```python
# Updated Pydantic schema
class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    # NEW fields (optional)
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: str = "medium"  # default
    tags: List[str] = []
    recurrence_rule: Optional[dict] = None
    next_occurrence_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# GET endpoint supports new query parameters
@app.get("/users/{user_id}/tasks")
def list_tasks(
    user_id: UUID,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None
):
    # Filter and sort logic
    pass
```

---

## 8. Observability Stack Selection

**Decision**: Prometheus (metrics) + Loki (logs) + OpenTelemetry (traces)

**Rationale**:
- **Prometheus**: Standard for Kubernetes monitoring, great Dapr integration
- **Loki**: Cloud-native log aggregation, integrates with Prometheus/Grafana
- **OpenTelemetry**: Vendor-neutral tracing standard, Dapr native support
- **Grafana**: Single dashboard for metrics + logs + traces

**Alternatives considered**:
1. Datadog/New Relic (commercial APM)
   - Great features but expensive for hackathon
   - Rejected ❌

2. Custom logging (no aggregation)
   - Impossible to trace events across services
   - Doesn't meet observability requirement
   - Rejected ❌

3. ELK Stack (Elasticsearch + Logstash + Kibana)
   - More complex than Loki
   - Overkill for 5 microservices
   - Loki is simpler, designed for Kubernetes
   - Rejected ❌

**Implementation**:
```yaml
# Prometheus scrape config for Dapr metrics
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    scrape_configs:
    - job_name: 'dapr'
      static_configs:
      - targets: ['localhost:9090']

# OpenTelemetry exporter in each service
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
```

---

## 9. CI/CD Platform Selection

**Decision**: GitHub Actions (already using GitHub, no additional infrastructure)

**Rationale**:
- Integrated with repository, no separate account/setup needed
- Free tier sufficient for this project
- YAML-based workflow configuration (version-controlled)
- Excellent Docker support (push to registries)
- Good Kubernetes integration (deploy via kubectl/helm)

**Alternatives considered**:
1. GitLab CI/CD
   - Excellent but requires self-hosted runner or GitLab SaaS migration
   - Not applicable if already on GitHub
   - Rejected ❌

2. Jenkins
   - Self-hosted overhead
   - Overkill for this project
   - Rejected ❌

3. Manual deployment scripts
   - No automation
   - Violates "CI/CD deploys automatically" requirement
   - Rejected ❌

**Implementation**:
- Workflow: `.github/workflows/deploy-phase-v.yml`
- Stages: Lint → Build → Validate → Deploy-Test → Deploy-Prod (manual approval)

---

## 10. Production Cloud Platform Selection

**Status**: NEEDS CLARIFICATION (team decision required)

**Options**:

| Option | Pros | Cons |
|--------|------|------|
| **Azure AKS** | Enterprise integration, Azure ecosystem familiar | Cold start slower, regional limitations |
| **Google GKE** | Excellent Kubernetes implementation, free credits | GCP vendor lock-in, credit limitations |
| **Oracle OKE** | Recommended in spec, good performance | Less familiar to team (likely), regional availability |

**Recommendation**: **Oracle OKE** (as recommended in original spec)
- Good performance, reasonable pricing
- Aligns with specification intent
- Less competition for resources than GCP

**Decision**: Leave final platform choice to team; plan abstracts platform differences via Helm charts

---

## Summary Table

| Decision | Resolution | Status |
|----------|-----------|--------|
| Dapr integration | Use Dapr control plane, sidecar injection | ✅ Decided |
| Kafka deployment | Strimzi local, managed cloud | ✅ Decided |
| Event idempotency | UUID deduplication + DB constraints | ✅ Decided |
| State store | Dapr Postgres component | ✅ Decided |
| Recurring task generation | Event-driven async workflow | ✅ Decided |
| Reminder scheduling | Dapr Jobs API (no polling) | ✅ Decided |
| API compatibility | Backward-compatible REST extension | ✅ Decided |
| Observability | Prometheus + Loki + OpenTelemetry | ✅ Decided |
| CI/CD platform | GitHub Actions | ✅ Decided |
| Cloud platform | Oracle OKE (recommendation) | ⏳ Team decision |

---

## Architectural Decisions Worth Recording as ADRs

1. **ADR-001**: Event-Driven Architecture with Dapr
   - Significant: Affects all microservices design
   - Tradeoff: Async complexity vs decoupling benefit

2. **ADR-002**: No Direct Database Access for Consumers
   - Significant: Architecture enforcement constraint
   - Tradeoff: Slight latency vs clean boundaries

3. **ADR-003**: Managed Kafka in Production
   - Significant: Operational model difference local→production
   - Tradeoff: Cost vs operational simplicity

Recommend creating these ADRs after plan approval (suggest: `/sp.adr <title>`)
