# Kafka Configuration for Task Management System

## Overview
This document describes the Kafka configuration for the task management system, including topics, producers, consumers, and integration with the application services.

## Kafka Topics

### Task Events Topic
```properties
# Topic: task-events
# Purpose: General task lifecycle events (created, updated, completed, deleted)
# Partitions: 3
# Replication Factor: 1 (for development; 3 for production)
# Retention: 7 days
# Cleanup Policy: delete

task-events.num.partitions=3
task-events.replication.factor=1
task-events.retention.ms=604800000  # 7 days
task-events.cleanup.policy=delete
task-events.min.insync.replicas=1
```

### Reminder Events Topic
```properties
# Topic: reminder-events
# Purpose: Reminder scheduling and processing events
# Partitions: 3
# Replication Factor: 1 (for development; 3 for production)
# Retention: 3 days
# Cleanup Policy: delete

reminder-events.num.partitions=3
reminder-events.replication.factor=1
reminder-events.retention.ms=259200000  # 3 days
reminder-events.cleanup.policy=delete
reminder-events.min.insync.replicas=1
```

### Recurring Task Events Topic
```properties
# Topic: recurring-task-events
# Purpose: Events related to recurring task generation and processing
# Partitions: 3
# Replication Factor: 1 (for development; 3 for production)
# Retention: 7 days
# Cleanup Policy: delete

recurring-task-events.num.partitions=3
recurring-task-events.replication.factor=1
recurring-task-events.retention.ms=604800000  # 7 days
recurring-task-events.cleanup.policy=delete
recurring-task-events.min.insync.replicas=1
```

## Kafka Server Configuration

### server.properties
```properties
# Kafka Server Properties for Task Management System

# Server Basics
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://localhost:9092
listener.security.protocol.map=PLAINTEXT:PLAINTEXT
inter.broker.listener.name=PLAINTEXT

# Log Basics
log.dirs=/tmp/kafka-logs
num.partitions=3
num.recovery.threads.per.data.dir=1

# Log Retention
log.retention.hours=168  # 7 days
log.segment.bytes=1073741824  # 1GB
log.retention.check.interval.ms=300000  # 5 minutes

# Zookeeper
zookeeper.connect=localhost:2181
zookeeper.connection.timeout.ms=18000

# Socket Settings
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600  # 100MB

# Replication Settings
default.replication.factor=1
min.insync.replicas=1
replica.lag.time.max.ms=30000

# Performance Tuning
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Compression
compression.type=producer

# Offset Management
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
```

## Kafka Consumer Configuration

### Consumer Properties
```properties
# Consumer Properties for Task Management System

# Consumer Basics
bootstrap.servers=localhost:9092
group.id=task-service-group

# Deserialization
key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
value.deserializer=org.apache.kafka.common.serialization.StringDeserializer

# Performance
fetch.min.bytes=1024
fetch.max.wait.ms=500
max.partition.fetch.bytes=1048576

# Consumer Group
session.timeout.ms=30000
heartbeat.interval.ms=10000
max.poll.records=100
max.poll.interval.ms=300000  # 5 minutes

# Offset Management
enable.auto.commit=true
auto.commit.interval.ms=1000
auto.offset.reset=latest

# Security
security.protocol=PLAINTEXT
sasl.mechanism=PLAIN