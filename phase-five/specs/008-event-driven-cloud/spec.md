# Feature Specification: Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform

**Feature Branch**: `008-event-driven-cloud`
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Phase V – Advanced Event-Driven Cloud Deployment for Todo Platform"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Platform Engineer Deploys Todo App to Local Kubernetes (Priority: P1)

A platform engineer needs to deploy the entire Todo application (frontend, backend, and all microservices) to a local Kubernetes cluster (Minikube) with Kafka event streaming and Dapr service mesh, demonstrating a production-ready local environment without code modifications.

**Why this priority**: This is the foundation for all cloud deployments and validates the event-driven architecture works end-to-end locally before moving to production cloud platforms. It demonstrates operational readiness.

**Independent Test**: Deploy full system to Minikube with `helm install`, verify all services are running, Kafka topics exist, Dapr sidecars are healthy, and the Todo app is accessible via frontend.

**Acceptance Scenarios**:

1. **Given** Minikube cluster with Dapr control plane and Kafka installed, **When** platform engineer runs `helm install todo-system ./helm/charts`, **Then** all pods reach Running state within 5 minutes and health checks pass
2. **Given** deployed system, **When** frontend is accessed via browser, **Then** user can create, read, update, and delete tasks without errors
3. **Given** deployed system, **When** any service pod crashes and restarts, **Then** event consumers reconnect and process pending messages without data loss
4. **Given** deployed system, **When** logs are streamed from any service pod, **Then** centralized logging aggregates all logs with pod/service identifiers

---

### User Story 2 - Cloud Engineer Promotes Todo App to Production Kubernetes (Priority: P1)

A cloud engineer needs to deploy the same Todo application from staging to a production Kubernetes cluster (AKS, GKE, or Oracle OKE) using identical Helm charts, with production-grade secrets management, observability, and no manual kubectl commands.

**Why this priority**: This ensures consistency between local and cloud environments (no code changes needed) and demonstrates production readiness for hackathon judges evaluating system design.

**Independent Test**: Deploy to production Kubernetes cluster using same Helm charts as local deployment, verify all services are healthy with production secrets configured, and the application remains operational under realistic traffic patterns.

**Acceptance Scenarios**:

1. **Given** production Kubernetes cluster with Dapr and managed Kafka, **When** cloud engineer runs `helm install todo-system ./helm/charts --values prod-values.yaml`, **Then** all pods are Running and no manual kubectl apply commands are required
2. **Given** deployed system with configured external secrets store, **When** database credentials are rotated, **Then** services reconnect automatically within 30 seconds without pod restarts
3. **Given** deployed system, **When** traffic reaches 1000 requests/second, **Then** system maintains p95 latency under 500ms and no requests are dropped
4. **Given** deployed system with monitoring enabled, **When** a service becomes unavailable, **Then** alert is triggered within 10 seconds and appears in monitoring dashboard

---

### User Story 3 - Todo User Creates Recurring Task with Smart Reminders (Priority: P1)

A Todo app user needs to create a task that recurs daily, and when they complete the current occurrence, the next day's task is automatically created via event-driven workflow, with reminders triggering at precise scheduled times without polling.

**Why this priority**: This is a core feature differentiator from basic Todo apps and showcases the event-driven architecture benefits to end users. It requires Kafka for reliability and Dapr Jobs for exact-time reminders.

**Independent Test**: Create recurring daily task, complete it, verify next occurrence is created, receive reminder notification at scheduled time, and trace the event through Kafka topic to confirm async processing.

**Acceptance Scenarios**:

1. **Given** logged-in user in Todo frontend, **When** user creates task with title "Daily standup" and recurrence rule "daily at 9:00 AM", **Then** task is stored with recurrence metadata and Kafka event is published
2. **Given** task with daily recurrence, **When** task status changes to "completed", **Then** Recurring Task Service consumes event, generates next occurrence within 2 seconds, and publishes new task-created event
3. **Given** task with due_at 9:00 AM and remind_at 8:50 AM, **When** scheduled time arrives, **Then** Dapr Jobs API triggers reminder event exactly at 8:50 AM (within 5-second precision)
4. **Given** reminder event published, **When** Notification Service consumes event, **Then** user receives notification within 3 seconds and audit log records the event

---

### User Story 4 - System Administrator Monitors Event Flow in Production (Priority: P2)

A system administrator needs to trace a single Todo event (task creation → recurring task generation → reminder trigger → notification delivery) across all microservices using centralized logs, metrics, and traces without accessing individual pod logs.

**Why this priority**: Operational observability is critical for production systems. Demonstrates system design evaluation capability for hackathon judges.

**Independent Test**: Enable distributed tracing, create a task, verify complete event chain is visible in tracing dashboard with latencies at each step, and verify alerts trigger based on threshold violations.

**Acceptance Scenarios**:

1. **Given** system with Prometheus metrics enabled, **When** dashboard is accessed, **Then** metrics show task creation rate, event processing latency, Kafka consumer lag, and service availability per microservice
2. **Given** distributed tracing enabled, **When** task event is published, **Then** trace follows event through Kafka consumer → Recurring Task Service → state store → Kafka producer with timing at each step
3. **Given** Audit Log Service consuming events, **When** task is created/updated/deleted, **Then** audit log entry is created within 1 second with user ID, timestamp, and change details
4. **Given** health checks enabled, **When** a critical service becomes unhealthy, **Then** alert fires within 10 seconds and shows in monitoring UI

---

### User Story 5 - Backend Developer Adds New Task Priority Feature (Priority: P2)

A backend developer needs to extend the Todo schema to support task priorities (low/medium/high), ensure the frontend receives priority data, and maintain event-driven consistency without writing Kafka client code or direct database queries outside the core service.

**Why this priority**: Demonstrates extensibility of the event-driven architecture. Shows that Dapr abstraction enables new features without modifying core infrastructure.

**Independent Test**: Add priority field to task schema, update frontend to display and filter by priority, publish task-with-priority event, verify consumers can access priority via Dapr state store, and existing features still work.

**Acceptance Scenarios**:

1. **Given** task schema, **When** developer adds priority enum field (low/medium/high), **Then** existing tasks default to "medium" and API accepts priority in create/update requests
2. **Given** frontend with priority field, **When** task is created with priority, **Then** priority is included in Kafka event payload and persisted in state store
3. **Given** WebSocket Sync Service listening to task-updates topic, **When** task priority changes, **Then** real-time update is broadcast to connected frontend clients within 500ms
4. **Given** frontend with priority filters, **When** user filters by "high" priority, **Then** only high-priority tasks are displayed and filter state is persisted

---

### User Story 6 - CI/CD Pipeline Automates Deployment (Priority: P2)

A DevOps engineer needs to configure GitHub Actions to automatically build Docker images, validate Kubernetes manifests, and deploy to both local Minikube and production cluster on each commit, with no manual intervention required.

**Why this priority**: Demonstrates production-grade CI/CD practices. Validates reproducibility and automation capability for hackathon evaluation.

**Independent Test**: Push code to feature branch, verify GitHub Actions pipeline runs, builds images, pushes to registry, deploys to test cluster, and runs integration tests within 10 minutes.

**Acceptance Scenarios**:

1. **Given** feature branch pushed to GitHub, **When** GitHub Actions workflow triggers, **Then** code is linted, Docker images are built, and images are pushed to registry
2. **Given** images pushed to registry, **When** manifest validation step runs, **Then** Helm templates are validated and Kubernetes manifests are checked for policy compliance
3. **Given** manifests validated, **When** deployment step executes, **Then** Helm chart is deployed to test cluster and deployment waits for all pods to become Ready
4. **Given** deployment complete, **When** integration tests run, **Then** tests verify task creation, recurring task generation, and reminder delivery end-to-end

---

### Edge Cases

- What happens when Kafka broker is unavailable? Services must buffer events and retry on reconnection without losing data.
- How does system handle task completion while recurring task generation is in flight? Events must be idempotent; duplicate task creation must be detected and skipped.
- What happens if Dapr sidecar becomes unavailable? Service must fail gracefully and reconnect when sidecar becomes healthy.
- How does system handle clock skew between services for exact-time reminders? Reminder time must use server-side timestamps; Dapr Jobs API must handle scheduling across time zones.
- What happens if a consumer service crashes with unprocessed Kafka messages? Consumer offset tracking must be reset safely to replay missed events without duplicating side effects.

## Requirements *(mandatory)*

### Functional Requirements

**Core Backend Extensions**

- **FR-001**: Tasks MUST support due_at and remind_at timestamp fields
- **FR-002**: Tasks MUST support priority field with values (low, medium, high)
- **FR-003**: Tasks MUST support tags (list of string identifiers) and tag-based filtering
- **FR-004**: Tasks MUST support recurrence rules (daily, weekly, monthly) with next occurrence auto-generation
- **FR-005**: System MUST search tasks by title and description substring match
- **FR-006**: System MUST sort tasks by due_at, priority, creation_at with ascending/descending order

**Event-Driven Architecture**

- **FR-007**: Core Todo Service MUST publish task lifecycle events (task-created, task-updated, task-deleted, task-completed) to Kafka topic "task-events"
- **FR-008**: Kafka topics MUST be provisioned: task-events, reminders, task-updates
- **FR-009**: All inter-service communication MUST use Dapr service invocation HTTP/gRPC APIs (no direct service-to-service calls)
- **FR-010**: Recurring Task Service MUST consume task-completed events and generate next recurrence within 2 seconds
- **FR-011**: Recurring Task Service MUST use Dapr state store API (no direct database connection) for reading task configuration
- **FR-012**: Notification Service MUST consume reminder events and publish notifications (exact mechanism not specified)
- **FR-013**: Audit Log Service MUST consume all task events and create audit trail entries
- **FR-014**: WebSocket Sync Service MUST consume task-updates events and broadcast real-time updates to connected frontend clients

**Dapr Integration**

- **FR-015**: Dapr Pub/Sub component MUST abstract Kafka (no Kafka client libraries in application code)
- **FR-016**: Dapr State Store component MUST persist service state to external PostgreSQL
- **FR-017**: Dapr Secrets Store component MUST provide database credentials, API keys, and configuration
- **FR-018**: Dapr Jobs API MUST trigger reminders at exact scheduled times (within 5-second precision) without polling
- **FR-019**: Services MUST declare Dapr sidecars with health checks and must reconnect on sidecar restart

**Deployment & Infrastructure**

- **FR-020**: System MUST deploy to Minikube with Dapr control plane and Kafka running in cluster
- **FR-021**: System MUST deploy to production Kubernetes (AKS, GKE, or Oracle OKE) with identical Helm charts as local deployment
- **FR-022**: Helm charts MUST support environment-specific values files (local-values.yaml, prod-values.yaml) without code changes
- **FR-023**: System MUST configure external secrets store (HashiCorp Vault or cloud-native alternative) for production credentials
- **FR-024**: System MUST support managed Kafka services (Redpanda, Confluent Cloud, or self-hosted) via Dapr configuration
- **FR-025**: Database connection pooling MUST be configured for Dapr sidecar connections (no connection storms)

**CI/CD Pipeline**

- **FR-026**: GitHub Actions workflow MUST build Docker images for all services
- **FR-027**: GitHub Actions workflow MUST validate Kubernetes manifests and Helm templates
- **FR-028**: GitHub Actions workflow MUST deploy to test Kubernetes cluster
- **FR-029**: GitHub Actions workflow MUST run integration tests (task creation, recurring generation, reminder delivery)
- **FR-030**: GitHub Actions workflow MUST support manual approval before production deployment

**Observability**

- **FR-031**: System MUST export Prometheus metrics for: task creation rate, event processing latency, Kafka consumer lag, service availability
- **FR-032**: System MUST support distributed tracing (OpenTelemetry or cloud-native alternative) showing event flow across services
- **FR-033**: System MUST collect centralized logs with pod/service identifiers
- **FR-034**: Health checks MUST report service and dependency health (Kafka, PostgreSQL, Dapr sidecar)

### Key Entities

- **Task**: Represents a user todo item with id, title, description, due_at, remind_at, priority, tags, recurrence_rule, user_id, status, created_at, updated_at
- **Recurrence Rule**: Represents recurrence pattern with frequency (daily/weekly/monthly), next_occurrence_at, end_date
- **Task Event**: Published to Kafka with event_type (created/updated/deleted/completed), task_id, user_id, timestamp, event_data
- **Reminder**: Scheduled event with remind_at timestamp, task_id, user_id, notification_method
- **Audit Log**: Record of all task events with user_id, action, timestamp, change_data, service_name
- **Service Health**: Status of each microservice and its dependencies (Kafka, PostgreSQL, Dapr)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All services deploy to Minikube and reach Ready state within 5 minutes with zero manual kubectl commands
- **SC-002**: Identical Helm charts deploy to production (AKS/GKE/OKE) without code or configuration modifications
- **SC-003**: Recurring task is generated within 2 seconds of parent task completion
- **SC-004**: Reminder is triggered at scheduled time within ±5 second precision
- **SC-005**: System sustains 1000 concurrent users with p95 latency under 500ms for task operations
- **SC-006**: Kafka consumer lag for all topics is zero during steady state
- **SC-007**: CI/CD pipeline completes full build, test, and deployment cycle in under 10 minutes
- **SC-008**: All microservices maintain 99.9% uptime during standard operations (excluding planned maintenance)
- **SC-009**: Distributed trace shows complete event journey from producer to final consumer with timing at each step
- **SC-010**: Zero task events are lost when any single service pod crashes and restarts
- **SC-011**: Frontend receives real-time updates within 500ms of task state change (via WebSocket Sync Service)
- **SC-012**: Search queries return results within 1 second for 100,000 task dataset
- **SC-013**: All infrastructure code (Helm, Dapr configs, Kubernetes manifests) is version-controlled with no manual kubectl apply in production

## Assumptions

- **Existing System**: Phase III/IV Todo app (Next.js frontend, FastAPI backend, Neon PostgreSQL) is production-ready and will not be rewritten
- **Kubernetes Expertise**: Platform engineers have intermediate Kubernetes knowledge (Helm, namespaces, RBAC)
- **Cloud Platform Selection**: Exactly one production cloud platform will be chosen (AKS/GKE/OKE) by the team; no multi-cloud deployment required
- **Kafka Message Volume**: Current Todo application traffic is under 10,000 events/minute; Kafka and Dapr are sufficient without additional optimizations
- **Event Idempotency**: All consumers are designed to handle duplicate event delivery (idempotency keys, database unique constraints)
- **Database Access**: Only Core Todo Service queries PostgreSQL directly; all other services access data via Dapr state store
- **Secrets Management**: Production secrets are stored securely (Vault, cloud-native secrets); no credentials in code or Helm values files
- **Observability Stack**: Prometheus + centralized logging (ELK, Loki, or cloud-native) are available; no custom monitoring required
- **Service Mesh**: Dapr provides service discovery and inter-service communication; no separate service mesh (Istio) is required

## Constraints

- No Kafka client libraries in application code (all via Dapr Pub/Sub)
- No direct database connections from non-core services (all via Dapr state store)
- All task lifecycle events must be published to Kafka topics (no synchronous service calls for task workflows)
- CI/CD pipeline must not use manual kubectl commands (deploy via Helm only)
- Identical Helm charts and Dapr configurations must work on both local (Minikube) and production (AKS/GKE/OKE) clusters
- No UI redesign; existing Next.js frontend must work without modifications
- Cloud deployment must be single-region (no multi-region failover in scope)

## Out of Scope

- Mobile application development
- UI/UX redesign or new frontend pages
- Vendor-specific lock-in features (cloud provider-specific APIs)
- Complex notification channels (SMS, WhatsApp, email integration)
- Advanced Kafka features (schema registry, protocol buffers)
- Multi-region active-active replication
- Custom machine learning models or AI features
- Integration with third-party Todo services
