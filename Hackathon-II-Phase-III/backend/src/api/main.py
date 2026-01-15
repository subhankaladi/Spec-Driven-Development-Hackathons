from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from src.api.routes import tasks, auth, chat
from src.database.session import create_db_and_tables
from src.auth.middleware import jwt_middleware
from src.utils.errors import create_error_response


app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Add middleware for JWT authentication
app.middleware("http")(jwt_middleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])




# Custom exception handlers for authentication errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_codes = {
        400: "BAD_REQUEST",
        401: "AUTH_001",
        403: "AUTH_002",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "SERVER_ERROR"
    }
    error_code = error_codes.get(exc.status_code)
    return create_error_response(
        detail=exc.detail or "An error occurred",
        error_code=error_code,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    detail = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])
    return create_error_response(
        detail=detail,
        error_code="VALIDATION_ERROR",
        status_code=422
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return create_error_response(
        detail="Internal server error",
        error_code="SERVER_ERROR",
        status_code=500
    )


@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}