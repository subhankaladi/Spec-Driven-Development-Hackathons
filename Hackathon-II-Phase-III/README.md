# Todo Full-Stack Web Application

This is a todo application built with FastAPI, SQLModel, and Neon PostgreSQL as part of the Spec-Driven Development Hackathon Phase II.

## Backend Foundation & Persistence

This feature implements the backend foundation for the Todo application with CRUD operations for tasks.

### Features

- Create, read, update, and delete todo tasks
- Data persistence using SQLModel and PostgreSQL
- RESTful API endpoints
- Proper error handling and validation

### Tech Stack

- Python 3.11
- FastAPI
- SQLModel
- Pydantic
- Neon PostgreSQL (with SQLite for development)

### API Endpoints

- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks` - Get all tasks
- `GET /api/v1/tasks/{id}` - Get a specific task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `GET /` - Root endpoint
- `GET /health` - Health check

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (optional, defaults to SQLite):
   ```
   DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
   ```
4. Run the application: `uvicorn backend.src.api.main:app --reload`

### Running Tests

```bash
pytest
```

### Environment Variables

- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `NEON_DATABASE_URL`: Neon PostgreSQL connection string (optional)

## Authentication & API Security

This feature implements authentication and API security using JWT tokens for user identification and access control.

### Features

- JWT-based authentication for all API endpoints
- User-specific data access (users can only access their own tasks)
- Cross-user access prevention
- Token validation and expiration checking
- Proper error handling for authentication failures

### JWT Configuration

- Algorithm: HS256 (configurable)
- Default expiration: 7 days (configurable)
- Secret key stored in environment variables

### API Security

- All task endpoints require valid JWT authentication
- Users can only access, modify, or delete their own tasks
- Invalid/expired tokens return 401 Unauthorized
- Cross-user access attempts return 403 Forbidden

### Environment Variables

- `JWT_SECRET`: Secret key for signing JWT tokens (defaults to development key)
- `JWT_ALGORITHM`: Algorithm for JWT signing (defaults to HS256)
- `JWT_EXPIRATION_DELTA`: Token expiration time in seconds (defaults to 604800 = 7 days)

### API Endpoints (Authentication Required)

All existing task endpoints now require authentication:

- `POST /api/v1/tasks` - Create a new task (requires valid JWT)
- `GET /api/v1/tasks` - Get all tasks for authenticated user
- `GET /api/v1/tasks/{id}` - Get a specific task (must belong to authenticated user)
- `PUT /api/v1/tasks/{id}` - Update a specific task (must belong to authenticated user)
- `DELETE /api/v1/tasks/{id}` - Delete a specific task (must belong to authenticated user)

### Authentication Setup

1. The application automatically validates JWT tokens on all protected endpoints
2. Include the JWT token in the Authorization header as: `Authorization: Bearer <token>`
3. The application will extract the user ID from the token's `sub` claim
4. Requests are validated against the user ID to ensure data access is limited to the authenticated user's own data

### Testing Authentication

Authentication can be tested using the comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_auth_utils.py  # Test JWT utilities
```