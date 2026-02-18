# Quickstart Guide: Advanced Features

## Overview
This guide provides instructions for setting up and running the advanced features (recurring tasks, due dates & reminders, priorities, tags, search/filter/sort, event-driven architecture with Kafka and Dapr).

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Kafka installation or access to a Kafka cluster
- Dapr runtime installed and initialized
- PostgreSQL database (Neon Serverless recommended)

## Setup Instructions

### 1. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dapr
```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr
dapr init
```

### 3. Backend Setup

#### 3.1. Set up Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3.2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3.3. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your database URL, Kafka settings, and Dapr configuration
```

#### 3.4. Set up Database
```bash
# Run migrations to create advanced feature tables
alembic upgrade head
```

#### 3.5. Start Kafka (using Docker)
```bash
# In a separate terminal
docker-compose -f kafka-docker-compose.yml up -d
```

#### 3.6. Start Backend with Dapr
```bash
# Run the backend application with Dapr sidecar
dapr run --app-id task-backend --app-port 8000 -- python src/main.py
```

### 4. Frontend Setup

#### 4.1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 4.2. Install Dependencies
```bash
npm install
```

#### 4.3. Configure Environment Variables
```bash
cp .env.local.example .env.local
# Edit .env.local with your backend API URL
```

#### 4.4. Start Frontend
```bash
npm run dev
```

## Key Components

### 1. Recurring Task Management
- **Models**: `RecurringTaskTemplate`, `TaskInstance`
- **Services**: `RecurringTaskService`
- **Endpoints**: `/users/{user_id}/recurring-tasks/*`

### 2. Due Dates & Reminders
- **Models**: `TaskInstance`, `Reminder`
- **Services**: `ReminderService`
- **Endpoints**: `/users/{user_id}/reminders/*`

### 3. Priorities & Tags
- **Models**: `TaskInstance`, `Tag`, `TaskTag`
- **Services**: `TagService`
- **Endpoints**: `/users/{user_id}/tags/*`

### 4. Advanced Search, Filter & Sort
- **Services**: `SearchService`
- **Endpoints**: `/users/{user_id}/tasks/search`

### 5. Event-Driven Architecture
- **Components**: Kafka producers/consumers
- **Events**: Task lifecycle events
- **Logging**: `TaskEventLog`

## API Usage Examples

### Create a Recurring Task
```bash
POST /users/{user_id}/recurring-tasks
Content-Type: application/json

{
  "title": "Weekly team meeting",
  "description": "Team sync meeting every Monday",
  "priority": "high",
  "recurrence_pattern": {
    "freq": "weekly",
    "interval": 1,
    "byweekday": ["MO"],
    "until": "2024-12-31"
  },
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Create a Task with Due Date and Priority
```bash
POST /users/{user_id}/tasks
Content-Type: application/json

{
  "title": "Submit quarterly report",
  "description": "Prepare and submit Q1 financial report",
  "priority": "high",
  "due_date": "2024-04-01T23:59:59Z",
  "tags": ["report", "finance", "urgent"]
}
```

### Advanced Search
```bash
POST /users/{user_id}/tasks/search
Content-Type: application/json

{
  "filters": {
    "priority": ["high", "medium"],
    "due_before": "2024-04-30T23:59:59Z",
    "tags": ["urgent", "work"]
  },
  "sort_by": "due_date",
  "sort_order": "asc",
  "page": 1,
  "page_size": 20
}
```

## Running Tests

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_recurring_tasks.py
pytest tests/test_reminders.py
pytest tests/test_search.py
```

### Frontend Tests
```bash
# Run all tests
npm test

# Run specific test files
npm run test -- src/components/tasks/RecurringTaskForm.test.tsx
```

## Dapr Configuration

### Component Files
The following Dapr component files are required:

1. **State Store** (`components/statestore.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://username:password@localhost:5432/database"
```

2. **Pub/Sub** (`components/pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "task-group"
  - name: disableTls
    value: "true"
```

## Kafka Setup

### Topics Required
- `task-events` - For task lifecycle events
- `reminder-events` - For reminder scheduling events
- `notification-events` - For notification events

### Producer Configuration
- Use JSON serialization for event payloads
- Implement retry logic with exponential backoff
- Use async producers for better performance

### Consumer Configuration
- Implement idempotent processing to handle duplicates
- Use consumer groups for scalability
- Implement dead letter queues for failed events

## Development Workflow

1. **Start Dapr Runtime**:
   ```bash
   dapr run --app-id task-backend --app-port 8000
   ```

2. **Run Migrations** (after schema changes):
   ```bash
   alembic revision --autogenerate -m "Add advanced features tables"
   alembic upgrade head
   ```

3. **Update API Contracts** (in `/contracts/` directory)

4. **Run Integration Tests**:
   ```bash
   pytest tests/integration/
   ```

## Troubleshooting

### Common Issues

1. **Dapr Sidecar Not Starting**:
   - Ensure Dapr is properly installed: `dapr --version`
   - Check if another instance is running: `dapr list`

2. **Kafka Connection Issues**:
   - Verify Kafka is running: `docker ps | grep kafka`
   - Check broker configuration in Dapr component file

3. **Database Migration Errors**:
   - Ensure PostgreSQL is accessible
   - Run `alembic current` to check current version

4. **Event Processing Delays**:
   - Check Kafka consumer lag
   - Verify sufficient consumer instances

### Useful Commands

```bash
# Check Dapr applications
dapr list

# View Dapr logs
dapr logs <app-id>

# Send test event to Kafka
dapr publish --pubsub pubsub --topic task-events --data '{"eventType": "task.created", "taskId": "123"}'

# Check Kafka topics
docker exec -it kafka-container kafka-topics.sh --list --bootstrap-server localhost:9092
```