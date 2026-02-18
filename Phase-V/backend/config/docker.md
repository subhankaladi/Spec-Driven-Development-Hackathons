# Docker Configuration for Advanced Task Management Backend

## Overview
This document describes the Docker configuration for the backend service with advanced features including recurring tasks, due dates & reminders, task prioritization & tagging, advanced search/filter/sort, and event-driven architecture with Kafka and Dapr.

## Dockerfile

```Dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        g++ \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR ${APP_HOME}

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser ${APP_HOME}
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend API Service
  backend:
    build: .
    container_name: task-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://task_user:task_password@db:5432/task_db
      - SECRET_KEY=your-super-secret-key-change-in-production
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_TASK_EVENTS_TOPIC=task-events
      - KAFKA_REMINDER_EVENTS_TOPIC=reminder-events
      - KAFKA_RECURRING_TASK_EVENTS_TOPIC=recurring-task-events
      - DAPR_APP_ID=task-backend
      - DAPR_HTTP_PORT=3500
      - DAPR_GRPC_PORT=50001
    volumes:
      - .:/app
    depends_on:
      - db
      - kafka
    command: [
      "sh", "-c",
      "python -c \"from src.models.database import init_db; init_db()\" && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
    ]
    networks:
      - task-network

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: task-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=task_db
      - POSTGRES_USER=task_user
      - POSTGRES_PASSWORD=task_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - task-network

  # Kafka for Event Streaming
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: task-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - task-network

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: task-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    depends_on:
      - zookeeper
    networks:
      - task-network

  # Kafka UI for monitoring
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: task-kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    depends_on:
      - kafka
    networks:
      - task-network

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: task-redis
    ports:
      - "6379:6379"
    networks:
      - task-network

  # Dapr Sidecar (if running with Dapr)
  dapr-placement:
    image: daprio/dapr:latest
    container_name: dapr-placement
    ports:
      - "50005:50005"
    command: ["./placement", "-port", "50005"]
    networks:
      - task-network

volumes:
  postgres_data:

networks:
  task-network:
    driver: bridge
```

## Production Docker Compose (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  # Backend API Service (Production)
  backend:
    build: .
    container_name: task-backend-prod
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=postgresql://task_user:task_password@db:5432/task_db
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_TASK_EVENTS_TOPIC=task-events
      - KAFKA_REMINDER_EVENTS_TOPIC=reminder-events
      - KAFKA_RECURRING_TASK_EVENTS_TOPIC=recurring-task-events
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - kafka
    command: [
      "sh", "-c",
      "python -c \"from src.models.database import init_db; init_db()\" && uvicorn src.main:app --host 0.0.0.0 --port 8000"
    ]
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - task-prod-network

  # PostgreSQL Database (Production)
  db:
    image: postgres:15-alpine
    container_name: task-db-prod
    environment:
      - POSTGRES_DB=task_db
      - POSTGRES_USER=task_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./init-prod.sql:/docker-entrypoint-initdb.d/init-prod.sql
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    networks:
      - task-prod-network

  # Kafka Cluster (Production)
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SYNC_LIMIT: 2
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
        reservations:
          cpus: '0.1'
          memory: 128M
    networks:
      - task-prod-network

  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
    depends_on:
      - zookeeper
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    networks:
      - task-prod-network

  # Redis (Production)
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 256M
    networks:
      - task-prod-network

volumes:
  postgres_data_prod:

networks:
  task-prod-network:
    driver: overlay
    attachable: true
```

## Docker Compose for Development with Dapr (docker-compose.dapr.yml)

```yaml
version: '3.8'

services:
  # Backend with Dapr sidecar
  backend:
    build: .
    container_name: task-backend-dapr
    ports:
      - "8000:8000"
      - "3500:3500"  # Dapr HTTP port
      - "50001:50001" # Dapr gRPC port
    environment:
      - DATABASE_URL=postgresql://task_user:task_password@dapr-sidecar:5432/task_db
      - SECRET_KEY=your-super-secret-key-change-in-production
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - DAPR_APP_ID=task-backend
      - DAPR_HTTP_PORT=3500
      - DAPR_GRPC_PORT=50001
    volumes:
      - .:/app
    depends_on:
      - db
      - kafka
      - dapr-placement
    command: [
      "dapr", "run",
      "--app-id", "task-backend",
      "--app-port", "8000",
      "--dapr-http-port", "3500",
      "--dapr-grpc-port", "50001",
      "--components-path", "./dapr/components",
      "--log-level", "debug",
      "--", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
    ]
    networks:
      - task-network

  # Dapr Placement Service
  dapr-placement:
    image: daprio/dapr:latest
    container_name: dapr-placement-dev
    ports:
      - "50005:50005"
    command: ["./placement", "-port", "50005", "-log-level", "debug"]
    networks:
      - task-network

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: task-db-dapr
    environment:
      - POSTGRES_DB=task_db
      - POSTGRES_USER=task_user
      - POSTGRES_PASSWORD=task_password
    volumes:
      - postgres_data_dapr:/var/lib/postgresql/data
    networks:
      - task-network

  # Kafka for Event Streaming
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: dapr-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - task-network

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: dapr-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    depends_on:
      - zookeeper
    networks:
      - task-network

volumes:
  postgres_data_dapr:

networks:
  task-network:
    driver: bridge
```

## Dapr Components Configuration

### State Store Component
```yaml
# File: dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=db user=task_user password=task_password dbname=task_db port=5432 sslmode=disable"
  - name: actorStateStore
    value: "true"
```

### Pub/Sub Component
```yaml
# File: dapr/components/pubsub.yaml
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
    value: "task-service-group"
  - name: clientID
    value: "task-service"
  - name: authRequired
    value: "false"
```

## Build and Deployment Commands

### Building the Image
```bash
# Build the Docker image
docker build -t task-backend .

# Build with no cache
docker build --no-cache -t task-backend .
```

### Running with Docker Compose
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d backend db kafka

# View logs
docker-compose logs -f backend

# Scale backend service
docker-compose up -d --scale backend=3
```

### Production Deployment
```bash
# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d

# Deploy to swarm
docker stack deploy -c docker-compose.prod.yml task-stack
```

## Health Checks

### Dockerfile Health Check
```Dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Docker Compose Health Check
```yaml
  backend:
    # ... other config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Environment Variables

### .env file for Docker
```env
# Database
DATABASE_URL=postgresql://task_user:task_password@db:5432/task_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TASK_EVENTS_TOPIC=task-events
KAFKA_REMINDER_EVENTS_TOPIC=reminder-events
KAFKA_RECURRING_TASK_EVENTS_TOPIC=recurring-task-events

# Redis
REDIS_URL=redis://redis:6379

# Dapr
DAPR_APP_ID=task-backend
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

## Multi-stage Build (Optimized Dockerfile)

```Dockerfile
# Multi-stage build for optimized image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Set work directory
WORKDIR ${APP_HOME}

# Install dependencies from wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project files
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This configuration provides a complete Docker setup for the advanced task management backend with support for all the implemented features including recurring tasks, due dates & reminders, task prioritization & tagging, advanced search/filter/sort, and event-driven architecture with Kafka and Dapr integration.