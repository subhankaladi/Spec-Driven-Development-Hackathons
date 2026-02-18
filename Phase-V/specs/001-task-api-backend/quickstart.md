# Quickstart: Task API Backend

## Prerequisites

- Python 3.11+
- Neon Serverless PostgreSQL database
- Git

## Setup

### 1. Clone and Navigate

```bash
git checkout 001-task-api-backend
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: Neon PostgreSQL connection string (格式: postgresql://user:password@host/database)
- `API_HOST`: Host to bind (default: 0.0.0.0)
- `API_PORT`: Port to listen (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging verbosity (default: info)

### 5. Initialize Database

Run migrations to create tables:

```bash
alembic upgrade head
```

Or create tables directly:

```bash
python -c "from src.models.database import create_tables; create_tables()"
```

### 6. Start Development Server

```bash
uvicorn src.main:app --reload
```

Server will be available at `http://localhost:8000`

### 7. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Run Tests

```bash
pytest -v
```

### Test Coverage

```bash
pytest --cov=src --cov-report=html
```

### Integration Tests

```bash
pytest tests/ -v --integration
```

## Project Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── database.py      # DB connection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── tasks.py     # Task endpoints
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── task.py      # Pydantic schemas
│   │       └── errors.py    # Error schemas
│   ├── main.py              # FastAPI app
│   └── config.py            # Env configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_crud.py
│   └── test_user_isolation.py
├── alembic/
│   └── versions/
├── requirements.txt
├── .env.example
└── README.md
```

## Example API Usage

### Create a Task

```bash
curl -X POST "http://localhost:8000/users/{user_id}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### List Tasks

```bash
curl "http://localhost:8000/users/{user_id}/tasks?page=1&page_size=20"
```

### Get Single Task

```bash
curl "http://localhost:8000/users/{user_id}/tasks/{task_id}"
```

### Update Task

```bash
curl -X PUT "http://localhost:8000/users/{user_id}/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and supplies", "is_completed": true}'
```

### Delete Task

```bash
curl -X DELETE "http://localhost:8000/users/{user_id}/tasks/{task_id}"
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] Database connection successful
- [ ] API endpoints respond correctly
- [ ] User isolation works (cross-user requests return 404)
- [ ] Error handling returns proper status codes
- [ ] Tests pass

## Troubleshooting

### Database Connection Failed

1. Verify `DATABASE_URL` is correct
2. Check Neon firewall rules allow your IP
3. Ensure database is not paused (Neon auto-pauses after inactivity)

### Migration Errors

1. Check Alembic configuration in `alembic.ini`
2. Verify migration script syntax
3. Run `alembic stamp head` to sync migration state

### Port Already in Use

Change the port:
```bash
uvicorn src.main:app --port 8001
```

## Next Steps

After successful setup:
1. Run `/sp.tasks` to generate implementation tasks
2. Implement backend using Backend and Database agents
3. Test CRUD operations
4. Verify user isolation
5. Proceed to Spec-2 (Authentication)
