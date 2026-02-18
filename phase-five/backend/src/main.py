"""FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .config import settings
from .models.database import init_db
from .api.routes import router as api_router
from .api.routes.auth import router as auth_router
from .api.middleware.rate_limit import RateLimitMiddleware, get_rate_limit_from_env

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Task API Backend...")
    init_db()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Task API",
    description="RESTful API for task management with user isolation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for BetterAuth compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose authorization headers and set-cookie for BetterAuth
    expose_headers=["Access-Control-Allow-Origin", "Set-Cookie", "Authorization"]
)

# Add rate limiting middleware for chat endpoint
rate_limit = get_rate_limit_from_env()
app.add_middleware(RateLimitMiddleware, rate_limit=rate_limit, window_seconds=60)

# Include API routes
app.include_router(auth_router)  # Auth router already has prefix="/auth"
app.include_router(api_router, prefix="/users/{user_id}/tasks", tags=["tasks"])

# Chat routes (Phase 3)
from .api.routes.chat import router as chat_router
app.include_router(chat_router, tags=["Chat"])


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": None
            }
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        port=settings.api_port,
        reload=settings.debug
    )
