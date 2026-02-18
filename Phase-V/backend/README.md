# Task API Backend

A RESTful API for task management with user isolation, built with FastAPI and SQLModel.

## Features

- Create, read, update, and delete tasks
- User-scoped data access for multi-user isolation
- Paginated task lists
- RESTful API design with proper HTTP status codes
- Neon Serverless PostgreSQL database

## Quick Start

### Prerequisites

- Python 3.11+
- Neon Serverless PostgreSQL database

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Initialize Database

```bash
# Run migrations
alembic upgrade head
```

### Run Development Server

```bash
uvicorn src.main:app --reload
```

Server will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/{user_id}/tasks` | Create a new task |
| GET | `/users/{user_id}/tasks` | List all tasks for a user |
| GET | `/users/{user_id}/tasks/{task_id}` | Get a specific task |
| PUT | `/users/{user_id}/tasks/{task_id}` | Update a task (full) |
| PATCH | `/users/{user_id}/tasks/{task_id}` | Update a task (partial) |
| DELETE | `/users/{user_id}/tasks/{task_id}` | Delete a task |

## Project Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Task SQLModel entity
│   │   └── database.py      # Database connection
│   ├── api/
│   │   ├── routes/
│   │   │   └── tasks.py     # Task endpoints
│   │   └── schemas/
│   │       ├── task.py      # Pydantic schemas
│   │       └── errors.py    # Error schemas
│   ├── main.py              # FastAPI app
│   └── config.py            # Configuration
├── tests/
│   ├── conftest.py
│   ├── test_crud.py
│   └── test_user_isolation.py
├── alembic/
│   └── versions/
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```
