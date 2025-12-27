# Quickstart Guide: Backend Foundation & Persistence

**Feature**: 001-backend-foundation
**Date**: 2025-12-22

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Poetry or pip for dependency management
- Neon PostgreSQL account and database URL

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   or if using Poetry:
   ```bash
   poetry install
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require"
   ```

4. **Run the application**
   ```bash
   uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Usage

### Create a Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample task", "description": "This is a sample task"}'
```

### Get All Tasks
```bash
curl -X GET http://localhost:8000/tasks
```

### Get a Specific Task
```bash
curl -X GET http://localhost:8000/tasks/1
```

### Update a Task
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task", "is_completed": true}'
```

### Delete a Task
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# After making model changes
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc