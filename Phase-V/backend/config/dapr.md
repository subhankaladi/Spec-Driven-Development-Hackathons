# Dapr Configuration for Task Management System

## Overview
This document outlines the Dapr (Distributed Application Runtime) configuration for the task management system. Dapr provides portable, event-driven runtime for cloud and edge applications, offering building blocks for common distributed systems patterns.

## Dapr Components

### 1. State Store Configuration
```yaml
# File: components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=example dbname=taskdb port=5432 sslmode=disable"
  - name: actorStateStore
    value: "true"
```

### 2. Pub/Sub Broker Configuration
```yaml
# File: components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "dapr-consumer-group"
  - name: clientID
    value: "dapr-kafka-client"
  - name: authRequired
    value: "false"
  - name: maxMessageBytes
    value: "1048576"
  - name: timeoutInSec
    value: "10"
```

### 3. Secret Store Configuration
```yaml
# File: components/secretstore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-secretstore
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: "/path/to/secrets.json"
  - name: nestedSeparator
    value: ":"
```

## Dapr Sidecar Configuration

### Application Configuration
```yaml
# File: config/appconfig.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: task-appconfig
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  httpPipeline:
    handlers:
    - name: uppercase
      type: middleware.http.uppercase
  accessControl:
    defaultAction: allow
    trustDomain: "task-domain"
    policies:
    - appId: task-service
      defaultAction: allow
      trustDomain: "task-domain"
      namespace: default
```

## Service Invocation Configuration

### Using Dapr Service Invocation
```python
# Example Python code for service invocation
import requests
from dapr.clients import DaprClient

def invoke_task_service():
    with DaprClient() as client:
        # Invoke method on another service
        response = client.invoke_method(
            app_id='reminder-service',
            method_name='process-reminder',
            data={'task_id': '123', 'user_id': '456'},
            content_type='application/json'
        )
        return response
```

## State Management Usage

### Saving State
```python
# Example Python code for state management
from dapr.clients import DaprClient

def save_task_state(task_id: str, task_data: dict):
    with DaprClient() as client:
        client.save_state(
            store_name='task-statestore',
            key=f'task-{task_id}',
            value=json.dumps(task_data)
        )
```

### Getting State
```python
# Example Python code for getting state
from dapr.clients import DaprClient

def get_task_state(task_id: str):
    with DaprClient() as client:
        response = client.get_state(
            store_name='task-statestore',
            key=f'task-{task_id}'
        )
        return json.loads(response.data) if response.data else None
```

## Pub/Sub Configuration

### Publishing Events
```python
# Example Python code for publishing events
from dapr.clients import DaprClient

def publish_task_event(event_type: str, data: dict):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name='task-pubsub',
            topic_name='task-events',
            data=json.dumps(data),
            data_content_type='application/json'
        )
```

### Subscribing to Events
```python
# Example Python code for subscribing to events
from dapr.ext.grpc import App
from dapr.clients import DaprClient

app = App()

@app.subscribe(pubsub_name='task-pubsub', topic='task-events')
def handle_task_events(event_data):
    # Process task event
    print(f"Received task event: {event_data}")
    
    # Process the event
    with DaprClient() as client:
        # Do something with the event data
        pass
```

## Dapr CLI Commands

### Running with Dapr
```bash
# Run the application with Dapr sidecar
dapr run --app-id task-service --app-port 8000 -- python main.py

# Run with specific components path
dapr run --app-id task-service --app-port 8000 --components-path ./components -- python main.py

# Check Dapr sidecar status
dapr list

# View logs
dapr logs task-service
```

### Initializing Dapr
```bash
# Initialize Dapr runtime
dapr init

# Initialize with specific runtime version
dapr init --runtime-version 1.9.0

# Check Dapr status
dapr status
```

## Kubernetes Deployment Configuration

### Dapr Annotations in Kubernetes
```yaml
# Example Kubernetes deployment with Dapr
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-service
  template:
    metadata:
      labels:
        app: task-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "task-service"
        dapr.io/app-port: "8000"
        dapr.io/components-path: "/components"
    spec:
      containers:
      - name: task-service
        image: task-service:latest
        ports:
        - containerPort: 8000
```

## Configuration for Different Environments

### Development Configuration
```yaml
# components/local/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### Production Configuration
```yaml
# components/production/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "{{.taskDbConnectionString}}"
  - name: minConnectionPoolSize
    value: "5"
  - name: maxConnectionPoolSize
    value: "20"
  - name: timeoutInSeconds
    value: "20"
```

## Security Configuration

### Authentication and Authorization
```yaml
# config/security.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: task-security
spec:
  accessControl:
    defaultAction: deny
    trustDomain: "task-platform"
    policies:
    - appId: "task-service"
      defaultAction: allow
      trustDomain: "task-platform"
      namespace: "default"
      operations:
      - name: /tasks/*
        httpVerb: ["POST", "PUT", "GET", "DELETE"]
        action: allow
```

## Observability Configuration

### Telemetry Settings
```yaml
# config/telemetry.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: task-telemetry
spec:
  tracing:
    samplingRate: "0.5"
    zipkin:
      endpointAddress: "http://jaeger-collector:9411/api/v2/spans"
  metric:
    enabled: true
  logging:
    level: "info"
```

## Health Checks

### Dapr Health Endpoints
- Sidecar health: `http://localhost:3500/v1.0/healthz`
- App health (when using Dapr): `http://localhost:3500/v1.0/healthz/outbound`

## Best Practices

1. **Component Naming**: Use descriptive names for components that indicate their purpose
2. **Environment Separation**: Maintain separate component configurations for different environments
3. **Secret Management**: Store sensitive information like connection strings in secret stores
4. **State Consistency**: Choose appropriate consistency levels for state operations
5. **Event Ordering**: Use partition keys to ensure ordering of related events
6. **Error Handling**: Implement proper retry and dead-letter queue patterns
7. **Monitoring**: Enable tracing and metrics for observability