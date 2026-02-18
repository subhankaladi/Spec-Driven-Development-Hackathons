# Dapr Components Configuration

## Overview
This document describes the Dapr components configuration for the task management system, including state management, pub/sub, and secret stores.

## State Store Component
```yaml
# File: dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=example dbname=dapr_state_store port=5432 sslmode=disable"
  - name: actorStateStore
    value: "true"
  - name: keyPrefix
    value: "task"
```

### Alternative Redis State Store
```yaml
# File: dapr/components/redis-statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-redis-statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "localhost:6379"
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
  - name: keyPrefix
    value: "task"
```

## Pub/Sub Component
```yaml
# File: dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
  namespace: default
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

## Secret Store Component
```yaml
# File: dapr/components/secretstore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-secretstore
  namespace: default
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: "/path/to/secrets.json"
  - name: nestedSeparator
    value: ":"
```

### Kubernetes Secret Store (for production)
```yaml
# File: dapr/components/k8s-secretstore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-k8s-secretstore
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
```

## Binding Components
```yaml
# File: dapr/components/bindings.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-http-binding
  namespace: default
spec:
  type: bindings.http
  version: v1
  metadata:
  - name: url
    value: "https://api.example.com/webhook"
  - name: method
    value: "POST"
```

## Dapr Configuration
```yaml
# File: dapr/config/config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: task-dapr-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
  metric:
    enabled: true
  httpPipeline:
    handlers: []
  accessControl:
    defaultAction: allow
    trustDomain: "task-domain"
    policies:
    - appId: "task-backend"
      defaultAction: allow
      trustDomain: "task-domain"
      namespace: "default"
  features:
    - name: InputBindingStreaming
      enabled: true
    - name: Resiliency
      enabled: true
```

## Dapr Sidecar Annotations for Kubernetes
```yaml
# Example Kubernetes deployment with Dapr annotations
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-backend
  labels:
    app: task-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-backend
  template:
    metadata:
      labels:
        app: task-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "task-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "task-dapr-config"
        dapr.io/components: "task-statestore,task-pubsub"
    spec:
      containers:
      - name: task-backend
        image: task-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
```

## Service Invocation Example
```python
# Example of using Dapr service invocation in Python
import requests
from dapr.clients import DaprClient

def invoke_reminder_service(task_data):
    with DaprClient() as client:
        # Invoke method on reminder service
        response = client.invoke_method(
            app_id='reminder-service',
            method_name='schedule-reminder',
            data={'task': task_data},
            content_type='application/json'
        )
        return response
```

## State Management Example
```python
# Example of using Dapr state management in Python
from dapr.clients import DaprClient

def save_task_state(task_id, task_data):
    with DaprClient() as client:
        client.save_state(
            store_name='task-statestore',
            key=f'task-{task_id}',
            value=json.dumps(task_data),
            state_metadata={
                "contentType": "application/json"
            }
        )

def get_task_state(task_id):
    with DaprClient() as client:
        response = client.get_state(
            store_name='task-statestore',
            key=f'task-{task_id}',
            state_metadata={
                "contentType": "application/json"
            }
        )
        return json.loads(response.data) if response.data else None
```

## Pub/Sub Example
```python
# Example of using Dapr pub/sub in Python
from dapr.clients import DaprClient

def publish_task_event(event_type, task_data):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name='task-pubsub',
            topic='task-events',
            data=json.dumps({
                'event_type': event_type,
                'task_data': task_data,
                'timestamp': datetime.utcnow().isoformat()
            }),
            data_content_type='application/json'
        )

# Subscription handler (would be in a separate file)
from dapr.ext.grpc import App
app = App()

@app.subscribe(pubsub_name='task-pubsub', topic='task-events')
def task_events_handler(event_data):
    print(f'Subscriber received: {event_data}')
    # Process the task event
```

## Security Considerations
- Use encrypted connections (TLS) for production
- Implement proper authentication for all components
- Use Kubernetes secrets for sensitive information
- Apply principle of least privilege for access control
- Regularly rotate secrets and certificates

## Production Deployment Notes
- Use dedicated namespaces for different environments
- Implement proper resource limits and requests
- Set up monitoring and alerting for Dapr sidecars
- Use production-grade state stores (PostgreSQL, Redis cluster)
- Configure appropriate backup and disaster recovery procedures