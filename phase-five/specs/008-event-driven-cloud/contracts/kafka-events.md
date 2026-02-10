# Kafka Event Schemas for Phase V

**Document**: Event message formats for all Kafka topics
**Date**: 2026-02-10
**Version**: 1.0

---

## Overview

All events follow a standard envelope format with type-specific payload. Events are JSON-serialized and published to Kafka topics.

**Topic Architecture**:
- `task-events` — All task lifecycle events
- `reminders` — Reminder scheduling and trigger events
- `task-updates` — Real-time state change notifications for WebSocket sync

---

## Event Envelope (Common)

All events include this base structure:

```json
{
  "event_type": "task-created|task-updated|task-deleted|task-completed",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "task_id": "550e8400-e29b-41d4-a716-446655440003",
  "source_service": "core-todo-service",
  "version": "1.0"
}
```

**Field Descriptions**:
- `event_type`: Type of event (determines payload structure)
- `event_id`: Unique identifier for this event (UUID)
- `idempotency_key`: Deduplication key (UUID, must be unique per event source + user)
- `timestamp`: When event occurred (ISO 8601)
- `user_id`: User who triggered the event
- `task_id`: Task affected by event
- `source_service`: Which service published the event
- `version`: Schema version for compatibility

---

## task-events Topic

### Event: task-created

**Topic**: `task-events`
**Producer**: Core Todo Service
**Consumers**: Recurring Task Service, Audit Log Service, WebSocket Sync Service

```json
{
  "event_type": "task-created",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "title": "Daily standup",
    "description": "Team sync meeting",
    "due_at": "2026-02-11T09:00:00Z",
    "remind_at": "2026-02-11T08:50:00Z",
    "priority": "high",
    "tags": ["work", "meeting"],
    "recurrence_rule": {
      "frequency": "daily",
      "end_date": "2026-12-31"
    },
    "is_completed": false
  }
}
```

**Consumer Behavior**:
- **Recurring Task Service**: Extract recurrence_rule, store for future processing
- **Audit Log Service**: Create AuditLog entry with action="created"
- **WebSocket Sync Service**: Broadcast to connected clients for user_id

---

### Event: task-updated

**Topic**: `task-events`
**Producer**: Core Todo Service
**Consumers**: Recurring Task Service, Audit Log Service, WebSocket Sync Service

```json
{
  "event_type": "task-updated",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "previous_values": {
      "priority": "medium"
    },
    "updated_values": {
      "priority": "high",
      "due_at": "2026-02-11T10:00:00Z"
    },
    "all_fields": {
      "title": "Daily standup",
      "description": "Team sync meeting",
      "priority": "high",
      "due_at": "2026-02-11T10:00:00Z",
      "remind_at": "2026-02-11T08:50:00Z",
      "tags": ["work", "meeting"],
      "is_completed": false
    }
  }
}
```

**Consumer Behavior**:
- **Recurring Task Service**: Update stored recurrence configuration if changed
- **Audit Log Service**: Create AuditLog entry with action="updated" and change details
- **WebSocket Sync Service**: Broadcast updated fields to connected clients

---

### Event: task-completed

**Topic**: `task-events`
**Producer**: Core Todo Service
**Consumers**: Recurring Task Service, Audit Log Service, WebSocket Sync Service

```json
{
  "event_type": "task-completed",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "previous_is_completed": false,
    "is_completed": true,
    "completed_at": "2026-02-10T14:30:00Z",
    "recurrence_rule": {
      "frequency": "daily",
      "end_date": "2026-12-31"
    }
  }
}
```

**Consumer Behavior**:
- **Recurring Task Service**: If recurrence_rule exists:
  1. Calculate next_occurrence_at (tomorrow 9:00 AM)
  2. Create new Task with same recurrence_rule
  3. Publish task-created event for new task
- **Audit Log Service**: Create AuditLog entry with action="completed"
- **WebSocket Sync Service**: Broadcast completed status to clients

---

### Event: task-deleted

**Topic**: `task-events`
**Producer**: Core Todo Service
**Consumers**: Recurring Task Service, Audit Log Service, WebSocket Sync Service

```json
{
  "event_type": "task-deleted",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "title": "Daily standup",
    "reason": "user_deleted|cascade|cleanup"
  }
}
```

**Consumer Behavior**:
- **Recurring Task Service**: Remove stored recurrence configuration for this task
- **Audit Log Service**: Create AuditLog entry with action="deleted"
- **WebSocket Sync Service**: Notify clients that task was deleted

---

## reminders Topic

### Event: reminder-scheduled

**Topic**: `reminders`
**Producer**: Core Todo Service
**Consumers**: None (used for scheduling, not consumption)

```json
{
  "event_type": "reminder-scheduled",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T09:00:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "reminder_id": "550e8400-e29b-41d4-a716-446655440004",
    "remind_at": "2026-02-11T08:50:00Z",
    "title": "Daily standup",
    "notification_method": "default"
  }
}
```

**Producer Behavior**:
- After task creation with remind_at timestamp
- Call Dapr Jobs API to schedule callback at remind_at time
- Store Reminder record in database

---

### Event: reminder-triggered

**Topic**: `reminders`
**Producer**: Dapr Jobs API (via Core Todo Service callback)
**Consumers**: Notification Service

```json
{
  "event_type": "reminder-triggered",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-11T08:50:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "reminder_id": "550e8400-e29b-41d4-a716-446655440004",
    "title": "Daily standup",
    "description": "Team sync meeting",
    "notification_method": "default"
  }
}
```

**Consumer Behavior**:
- **Notification Service**: Process reminder
  - Placeholder: log notification
  - Future: Send email, SMS, push notification
  - Mark reminder as triggered in database

---

## task-updates Topic

### Event: task-state-changed

**Topic**: `task-updates`
**Producer**: Core Todo Service (fires on every task mutation)
**Consumers**: WebSocket Sync Service (real-time client updates)

```json
{
  "event_type": "task-state-changed",
  "event_id": "...",
  "idempotency_key": "...",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "...",
  "task_id": "...",
  "source_service": "core-todo-service",
  "version": "1.0",
  "payload": {
    "operation": "update|create|delete",
    "changed_fields": ["priority", "due_at"],
    "updated_values": {
      "priority": "high",
      "due_at": "2026-02-11T10:00:00Z"
    },
    "full_task": {
      "id": "...",
      "title": "Daily standup",
      "description": "Team sync meeting",
      "is_completed": false,
      "priority": "high",
      "due_at": "2026-02-11T10:00:00Z",
      "remind_at": "2026-02-11T08:50:00Z",
      "tags": ["work", "meeting"],
      "created_at": "2026-02-10T10:00:00Z",
      "updated_at": "2026-02-10T14:30:00Z"
    }
  }
}
```

**Consumer Behavior**:
- **WebSocket Sync Service**:
  1. Receive event
  2. Look up all WebSocket connections for user_id
  3. Broadcast full_task (or just changed_fields for efficiency)
  4. Connected clients receive update in real-time

---

## Event Ordering & Partitioning

**Kafka Partition Strategy**:
- Partition key: `user_id` (ensures events for one user are ordered)
- All events for a user go to same partition
- Guarantees event ordering within user scope

**Consumer Group Strategy**:
- Recurring Task Service: `recurring-task-consumer-group`
- Audit Log Service: `audit-log-consumer-group`
- WebSocket Sync Service: `websocket-sync-consumer-group`
- Each group maintains independent offset

---

## Idempotency & Deduplication

**Idempotency Key Generation**:
```python
import uuid

event = {
    "idempotency_key": str(uuid.uuid4()),  # Unique per event
    # ... rest of event
}
```

**Consumer Deduplication** (example):
```python
# Check if event already processed
INSERT INTO processed_events (
    service_name, idempotency_key, user_id, event_type, processed_at
) VALUES (?, ?, ?, ?, now())
ON CONFLICT DO NOTHING  # Postgres: unique constraint

# If no rows inserted, event was duplicate
```

---

## Backward Compatibility

**Version Field**:
- Current: `"version": "1.0"`
- Consumers MUST handle events with different versions
- Additive changes: new fields added, old consumers ignore them
- Breaking changes: increment version, handle both old and new

**Example**: Task gains new field `priority` in v1.1
```python
priority = event['payload'].get('priority', 'medium')  # Default if not present
```

---

## Monitoring & Observability

**Metrics per Topic**:
- `kafka_messages_published_total` — Total events published
- `kafka_messages_consumed_total` — Total events consumed
- `kafka_consumer_lag` — Events behind consumption
- `event_processing_latency_ms` — Time to process event

**Example Prometheus Query**:
```promql
rate(kafka_messages_consumed_total[5m])  # Events/sec consumption rate
```

**Tracing**:
- Each event includes trace context (propagated through Dapr)
- All downstream service calls inherit trace ID
- Complete trace visible from event publish → consumer processing
