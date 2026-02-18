# Kafka Configuration for Task Management System

## Overview
This document describes the Kafka setup for the event-driven architecture in the task management system. Kafka is used to handle task-related events asynchronously, enabling scalability and resilience.

## Topics

### task-events
- **Purpose**: General task lifecycle events (created, updated, completed, deleted)
- **Partitions**: 3
- **Replication Factor**: 1 (for development; 3 for production)
- **Retention**: 7 days
- **Key**: user_id (to ensure ordering for same user's events)
- **Value**: JSON with event details

### reminder-events
- **Purpose**: Reminder scheduling and processing events
- **Partitions**: 3
- **Replication Factor**: 1 (for development; 3 for production)
- **Retention**: 3 days
- **Key**: user_id
- **Value**: JSON with reminder details

### recurring-task-events
- **Purpose**: Events related to recurring task generation and processing
- **Partitions**: 3
- **Replication Factor**: 1 (for development; 3 for production)
- **Retention**: 7 days
- **Key**: user_id
- **Value**: JSON with recurring task details

## Event Schemas

### Task Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "task.created|task.updated|task.completed|task.deleted",
  "user_id": "uuid",
  "task_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "title": "string",
    "description": "string",
    "due_date": "ISO 8601 datetime",
    "priority": "low|medium|high",
    "is_completed": "boolean"
  }
}
```

### Reminder Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "reminder.scheduled|reminder.sent|reminder.failed",
  "user_id": "uuid",
  "task_id": "uuid",
  "reminder_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "reminder_time": "ISO 8601 datetime",
    "method": "email|push|sms",
    "status": "string"
  }
}
```

### Recurring Task Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "recurring_task.created|recurring_task.updated|recurring_task.instance_generated",
  "user_id": "uuid",
  "template_id": "uuid",
  "timestamp": "ISO 8601 datetime",
  "data": {
    "title": "string",
    "recurrence_pattern": "object",
    "start_date": "ISO 8601 datetime",
    "end_date": "ISO 8601 datetime",
    "instance_id": "uuid"  // for instance_generated events
  }
}
```

## Producer Configuration

### Python Producer (using aiokafka)
```python
from aiokafka import AIOKafkaProducer
import json

producer = AIOKafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None,
    acks='all',  # Wait for all replicas to acknowledge
    compression_type='gzip',  # Compress messages
    retries=3,  # Retry failed sends
    linger_ms=5,  # Batch messages for 5ms
    batch_size=16384  # Batch size in bytes
)
```

### Connection Settings
- **Bootstrap Servers**: `localhost:9092` (development) or `kafka-cluster:9092` (production)
- **Security Protocol**: `PLAINTEXT` (development) or `SASL_SSL` (production)
- **SASL Mechanism**: `PLAIN` or `SCRAM-SHA-256/512` (if using SASL)
- **Client ID**: `task-service-producer` or `reminder-service-producer`

## Consumer Configuration

### Python Consumer (using aiokafka)
```python
from aiokafka import AIOKafkaConsumer
import json

consumer = AIOKafkaConsumer(
    'task-events',
    'reminder-events',
    'recurring-task-events',  # Subscribe to all relevant topics
    bootstrap_servers=['localhost:9092'],
    group_id='task-processing-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')) if v else None,
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    auto_offset_reset='latest',  # Start from latest messages
    enable_auto_commit=True,  # Auto-commit offsets
    auto_commit_interval_ms=1000,  # Commit every 1 second
    max_poll_records=100,  # Max records per poll
    max_poll_interval_ms=300000  # Max time between polls (5 minutes)
)
```

### Consumer Groups
- **task-processing-group**: For processing task lifecycle events
- **reminder-processing-group**: For processing reminder events
- **recurring-task-group**: For processing recurring task events

## Dapr Integration

### Dapr Pub/Sub Component Configuration
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "dapr-consumer-group"
  - name: clientID
    value: "dapr-kafka-client"
  - name: authRequired
    value: "false"
```

### Topic Subscriptions via Dapr
The application can subscribe to Kafka topics through Dapr without direct Kafka client integration:

```python
from dapr.ext.grpc import App
app = App()

@app.subscribe(pubsub_name='task-pubsub', topic='task-events')
def handle_task_events(event_data):
    # Process task event
    pass
```

## Monitoring and Operations

### Key Metrics to Monitor
- **Consumer Lag**: Difference between latest offset and consumer's current offset
- **Throughput**: Messages per second being produced/consumed
- **Error Rates**: Failed message processing rates
- **Processing Latency**: Time between message production and consumption

### Health Checks
- Producer can connect to Kafka cluster
- Consumer can read from subscribed topics
- Event processing is happening without excessive lag

## Development Setup

### Docker Compose for Local Development
```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_INIT_LIMIT: 5
      ZOOKEEPER_SYNC_LIMIT: 2
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
      KAFKA_NUM_PARTITIONS: 3
    depends_on:
      - zookeeper

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
      KAFKA_CLUSTERS_0_SCHEMAREGISTRYURL: http://schema-registry:8081
    depends_on:
      - kafka
```

### Environment Variables
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TASK_EVENTS_TOPIC=task-events
KAFKA_REMINDER_EVENTS_TOPIC=reminder-events
KAFKA_RECURRING_TASK_EVENTS_TOPIC=recurring-task-events
KAFKA_CONSUMER_GROUP_ID=task-service-group
KAFKA_AUTO_OFFSET_RESET=latest
```

## Production Considerations

### Scaling
- Increase partitions for high-throughput topics
- Use multiple consumer instances in the same consumer group
- Monitor for consumer rebalancing issues

### Security
- Enable SSL/TLS encryption
- Use SASL authentication (PLAIN, SCRAM, etc.)
- Implement ACLs for topic access control

### Data Retention
- Configure appropriate retention policies based on business needs
- Consider log compaction for events where only the latest value matters

### Backup and Recovery
- Regular backup of Kafka metadata
- Replication across multiple availability zones
- Disaster recovery procedures for topic restoration