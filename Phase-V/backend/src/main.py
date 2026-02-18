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
from .api.routes.chat import router as chat_router
from .api.routes.recurring import router as recurring_router
from .api.routes.reminders import router as reminders_router
from .api.routes.tags import router as tags_router
from .api.routes.search import router as search_router

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
    logger.info("Starting Task API Backend with Advanced Features...")
    init_db()
    
    # Initialize Kafka producer (optional - app can run without Kafka)
    event_producer = None
    event_consumer = None
    try:
        from .events.producers.task_producer import get_event_producer
        event_producer = await get_event_producer()
        
        # Initialize Kafka consumer
        from .events.consumers.task_consumer import get_event_consumer
        event_consumer = await get_event_consumer()
        
        # Register event handlers
        from .events.consumers.task_consumer import (
            handle_task_created,
            handle_task_updated,
            handle_task_completed,
            handle_reminder_scheduled,
            handle_recurring_task_generated
        )
        
        event_consumer.register_handler("task.created", handle_task_created)
        event_consumer.register_handler("task.updated", handle_task_updated)
        event_consumer.register_handler("task.completed", handle_task_completed)
        event_consumer.register_handler("reminder.scheduled", handle_reminder_scheduled)
        event_consumer.register_handler("recurring_task.generated", handle_recurring_task_generated)
        
        logger.info("Kafka services initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Kafka services: {e}. App will run without event streaming.")
    
    # Start background tasks for recurring tasks and reminders
    import asyncio
    from .services.recurring_service import get_recurring_task_service
    from .services.reminder_service import get_reminder_service
    from .config import settings
    from .models.database import get_session

    async def background_task_runner():
        """Background task runner for recurring tasks and reminders."""
        from .models.database import engine
        from sqlmodel import Session
        while True:
            try:
                # Generate recurring task instances
                with Session(engine) as session:
                    recurring_service = get_recurring_task_service(session)
                    recurring_service.generate_task_instances()
                
                # Process pending reminders
                with Session(engine) as session:
                    reminder_service = get_reminder_service(session)
                    reminder_service.process_pending_reminders()
                
                # Wait before next iteration
                await asyncio.sleep(settings.recurring_task_check_interval)
            except Exception as e:
                logger.error(f"Error in background task runner: {e}")
                # Wait before next iteration even if there's an error
                await asyncio.sleep(settings.recurring_task_check_interval)
    
    # Start the background task
    asyncio.create_task(background_task_runner())
    
    logger.info("Application startup complete with advanced features")

    yield

    # Shutdown
    if event_producer:
        await event_producer.disconnect()
    if event_consumer:
        await event_consumer.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Task API with Advanced Features",
    description="RESTful API for task management with user isolation and advanced features (recurring tasks, due dates & reminders, priorities, tags, search)",
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

# Include API routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/users/{user_id}/tasks", tags=["tasks"])
app.include_router(recurring_router, prefix="/users/{user_id}/recurring-tasks", tags=["recurring-tasks"])
app.include_router(reminders_router, prefix="/users/{user_id}/reminders", tags=["reminders"])
app.include_router(tags_router, prefix="/users/{user_id}/tags", tags=["tags"])
app.include_router(search_router, prefix="/users/{user_id}/search", tags=["search"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])


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
