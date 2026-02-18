# Advanced Task Management System

This project implements advanced task management features including recurring tasks, due dates & reminders, task prioritization & tagging, advanced search/filter/sort, and event-driven architecture with Kafka and Dapr.

## Features

- **Recurring Tasks**: Create tasks that repeat on a schedule (daily, weekly, monthly, yearly)
- **Due Dates & Reminders**: Assign due dates to tasks and receive timely reminders
- **Task Prioritization & Tagging**: Assign priority levels and tags to tasks for better organization
- **Advanced Search/Filter/Sort**: Powerful search capabilities with multiple filter and sort options
- **Event-Driven Architecture**: Uses Kafka for asynchronous event processing
- **Distributed Runtime**: Leverages Dapr for resilience and scalability

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (for production)
- Kafka (for event streaming)
- Dapr (for distributed runtime)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/username/task-management-system.git
cd task-management-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and other settings

# Run database migrations
alembic upgrade head

# Install Dapr (if not already installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
dapr init
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend API URL

# Run the development server
npm run dev
```

### 4. Running with Docker

#### Development Mode
```bash
# Start all services with Docker Compose
docker-compose -f deploy/docker-compose.dev.yml up -d

# Or start individual services
docker-compose up -d db kafka zookeeper redis
```

#### Production Mode
```bash
# Start all services in production mode
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### 5. Running with Kafka and Dapr

```bash
# Start Kafka cluster
docker-compose -f kafka-docker-compose.yml up -d

# Start Dapr placement service
dapr placement

# Run the backend with Dapr
dapr run --app-id task-backend --app-port 8000 -- uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Task Management
- `GET /api/v1/users/{user_id}/tasks` - Get all tasks for a user
- `POST /api/v1/users/{user_id}/tasks` - Create a new task
- `GET /api/v1/users/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/users/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` - Delete a task

### Recurring Tasks
- `POST /api/v1/users/{user_id}/recurring-tasks` - Create a recurring task template
- `GET /api/v1/users/{user_id}/recurring-tasks/{template_id}` - Get a recurring task template
- `PUT /api/v1/users/{user_id}/recurring-tasks/{template_id}` - Update a recurring task template
- `DELETE /api/v1/users/{user_id}/recurring-tasks/{template_id}` - Delete a recurring task template

### Reminders
- `POST /api/v1/users/{user_id}/reminders` - Create a reminder
- `GET /api/v1/users/{user_id}/reminders` - Get all reminders for a user
- `DELETE /api/v1/users/{user_id}/reminders/{reminder_id}` - Delete a reminder

### Tags
- `POST /api/v1/users/{user_id}/tags` - Create a tag
- `GET /api/v1/users/{user_id}/tags` - Get all tags for a user
- `POST /api/v1/users/{user_id}/tasks/{task_id}/tags/{tag_id}` - Add a tag to a task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}/tags/{tag_id}` - Remove a tag from a task

### Search
- `POST /api/v1/users/{user_id}/tasks/search` - Search tasks with filters and sorting

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/task_db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TASK_EVENTS_TOPIC=task-events
KAFKA_REMINDER_EVENTS_TOPIC=reminder-events
KAFKA_RECURRING_TASK_EVENTS_TOPIC=recurring-task-events
REDIS_URL=redis://localhost:6379
DAPR_APP_ID=task-backend
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_KAFKA_UI_URL=http://localhost:8080
NEXT_PUBLIC_DAPR_ENABLED=true
```

## Kafka Topics

The system uses the following Kafka topics:
- `task-events` - Task lifecycle events (created, updated, completed, deleted)
- `reminder-events` - Reminder scheduling and processing events
- `recurring-task-events` - Recurring task generation events

## Dapr Components

The system uses the following Dapr components:
- State store for persistent data
- Pub/sub for event-driven communication
- Secret store for secure configuration
- Service invocation for inter-service communication

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Running Linters
```bash
# Backend linting
cd backend
flake8 src/
black --check src/

# Frontend linting
cd frontend
npm run lint
```

## Architecture

### Backend Architecture
- FastAPI for the web framework
- SQLModel for database modeling
- PostgreSQL for data persistence
- Kafka for event streaming
- Dapr for distributed runtime capabilities

### Frontend Architecture
- Next.js 16+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- React Query for state management

## Deployment

### Production Deployment
For production deployment, use the production Docker Compose file:

```bash
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### Kubernetes Deployment
Kubernetes manifests are available in the `deploy/k8s/` directory:

```bash
kubectl apply -f deploy/k8s/
```

## Troubleshooting

### Common Issues
1. **Kafka Connection Issues**: Ensure Kafka and Zookeeper are running
2. **Database Connection Issues**: Verify database URL and credentials
3. **Dapr Issues**: Make sure Dapr is initialized with `dapr init`
4. **Port Conflicts**: Check if required ports (8000, 3000, 9092, etc.) are available

### Useful Commands
```bash
# Check running containers
docker ps

# View logs
docker logs task-backend

# Check Dapr status
dapr status

# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.