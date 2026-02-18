# Kubernetes Deployment Configuration for Advanced Task Management System

## Overview
This document describes the Kubernetes deployment configuration for the task management system with advanced features including recurring tasks, due dates & reminders, task prioritization & tagging, advanced search/filter/sort, and event-driven architecture with Kafka and Dapr.

## Namespace
```yaml
# File: k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: task-management
  labels:
    name: task-management
```

## Secrets
```yaml
# File: k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: task-secrets
  namespace: task-management
type: Opaque
data:
  # Base64 encoded values
  db-password: <base64-encoded-password>
  jwt-secret: <base64-encoded-jwt-secret>
  kafka-bootstrap-servers: <base64-encoded-kafka-servers>
  dapr-secret: <base64-encoded-dapr-secret>
```

## ConfigMap
```yaml
# File: k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: task-config
  namespace: task-management
data:
  DATABASE_URL: "postgresql://task_user:$(DB_PASSWORD)@task-db:5432/task_db"
  SECRET_KEY: "$(JWT_SECRET)"
  ALGORITHM: "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: "30"
  KAFKA_BOOTSTRAP_SERVERS: "$(KAFKA_BOOTSTRAP_SERVERS)"
  KAFKA_TASK_EVENTS_TOPIC: "task-events"
  KAFKA_REMINDER_EVENTS_TOPIC: "reminder-events"
  KAFKA_RECURRING_TASK_EVENTS_TOPIC: "recurring-task-events"
  REDIS_URL: "redis://task-redis:6379"
  DEBUG: "false"
  LOG_LEVEL: "info"
  RECURRING_TASK_CHECK_INTERVAL: "300"  # 5 minutes
  REMINDER_CHECK_INTERVAL: "60"  # 1 minute
```

## PostgreSQL Deployment
```yaml
# File: k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-db
  namespace: task-management
  labels:
    app: task-db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-db
  template:
    metadata:
      labels:
        app: task-db
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "task_db"
        - name: POSTGRES_USER
          value: "task_user"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: task-secrets
              key: db-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        env:
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: task-db-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: task-db
  namespace: task-management
spec:
  selector:
    app: task-db
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-db-pvc
  namespace: task-management
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## Redis Deployment
```yaml
# File: k8s/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-redis
  namespace: task-management
  labels:
    app: task-redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-redis
  template:
    metadata:
      labels:
        app: task-redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command:
          - redis-server
          - --appendonly
          - "yes"
          - --maxmemory
          - "256mb"
          - --maxmemory-policy
          - "allkeys-lru"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: task-redis
  namespace: task-management
spec:
  selector:
    app: task-redis
  ports:
    - protocol: TCP
      port: 6379
      targetPort: 6379
  type: ClusterIP
```

## Kafka Deployment
```yaml
# File: k8s/kafka-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-zookeeper
  namespace: task-management
  labels:
    app: task-zookeeper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-zookeeper
  template:
    metadata:
      labels:
        app: task-zookeeper
    spec:
      containers:
      - name: zookeeper
        image: confluentinc/cp-zookeeper:latest
        ports:
        - containerPort: 2181
        env:
        - name: ZOOKEEPER_CLIENT_PORT
          value: "2181"
        - name: ZOOKEEPER_TICK_TIME
          value: "2000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-kafka
  namespace: task-management
  labels:
    app: task-kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-kafka
  template:
    metadata:
      labels:
        app: task-kafka
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:latest
        ports:
        - containerPort: 9092
        env:
        - name: KAFKA_BROKER_ID
          value: "1"
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: "task-zookeeper:2181"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "PLAINTEXT://task-kafka:9092"
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "1"
        - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
          value: "true"
        - name: KAFKA_NUM_PARTITIONS
          value: "3"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: task-zookeeper
  namespace: task-management
spec:
  selector:
    app: task-zookeeper
  ports:
    - protocol: TCP
      port: 2181
      targetPort: 2181
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: task-kafka
  namespace: task-management
spec:
  selector:
    app: task-kafka
  ports:
    - protocol: TCP
      port: 9092
      targetPort: 9092
  type: ClusterIP
```

## Backend Deployment with Dapr
```yaml
# File: k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-backend
  namespace: task-management
  labels:
    app: task-backend
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "task-backend"
    dapr.io/app-port: "8000"
    dapr.io/config: "task-dapr-config"
    dapr.io/components: "task-statestore,task-pubsub"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-backend
  template:
    metadata:
      labels:
        app: task-backend
    spec:
      containers:
      - name: backend
        image: task-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: task-config
        - secretRef:
            name: task-secrets
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: task-config
              key: DATABASE_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: task-backend
  namespace: task-management
spec:
  selector:
    app: task-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: task-backend-ingress
  namespace: task-management
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.taskmanagement.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: task-backend
            port:
              number: 8000
```

## Frontend Deployment
```yaml
# File: k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-frontend
  namespace: task-management
  labels:
    app: task-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: task-frontend
  template:
    metadata:
      labels:
        app: task-frontend
    spec:
      containers:
      - name: frontend
        image: task-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://api.taskmanagement.local"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: task-frontend
  namespace: task-management
spec:
  selector:
    app: task-frontend
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: task-frontend-ingress
  namespace: task-management
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: taskmanagement.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: task-frontend
            port:
              number: 3000
```

## Dapr Components
```yaml
# File: k8s/dapr-components.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
  namespace: task-management
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=task-db user=task_user password={{.Values.secrets.dbPassword}} dbname=task_db port=5432 sslmode=disable"
  - name: actorStateStore
    value: "true"
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
  namespace: task-management
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "task-kafka:9092"
  - name: consumerGroup
    value: "task-service-group"
  - name: clientID
    value: "task-service"
  - name: authRequired
    value: "false"
---
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: task-dapr-config
  namespace: task-management
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
      namespace: "task-management"
```

## Horizontal Pod Autoscaler
```yaml
# File: k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: task-backend-hpa
  namespace: task-management
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: task-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: task-frontend-hpa
  namespace: task-management
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: task-frontend
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Deployment Commands

### Apply all configurations
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/kafka-deployment.yaml
kubectl apply -f k8s/dapr-components.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/hpa.yaml
```

### Check deployment status
```bash
kubectl get pods -n task-management
kubectl get services -n task-management
kubectl get deployments -n task-management
kubectl get hpa -n task-management
```

### View logs
```bash
kubectl logs -f deployment/task-backend -n task-management
kubectl logs -f deployment/task-frontend -n task-management
```

## Dapr Sidecar Injection
With the annotations in the deployment, Dapr will automatically inject sidecars when deployed to a Dapr-enabled cluster.

## Monitoring and Observability
- Prometheus metrics available at `/metrics` endpoint
- Distributed tracing with Zipkin
- Structured logging with JSON format
- Health checks at `/health` endpoint