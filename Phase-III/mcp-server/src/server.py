"""MCP Server entry point for Todo Tooling.

This server exposes 5 stateless, JWT-authenticated tools via MCP protocol:
- add_task: Create new task
- list_tasks: Retrieve tasks with filtering/pagination
- complete_task: Mark task as completed (idempotent)
- update_task: Modify task fields
- delete_task: Permanently remove task

Architecture:
- Low-level MCP SDK API with async handlers
- Lifespan context for database connection pooling
- Session-per-invocation (stateless)
- JWT validation before every database operation
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from mcp.server.lowlevel import Server
import mcp.types as types

from .db.session import create_db_engine
from .schemas.tool_schemas import (
    ADD_TASK_INPUT_SCHEMA,
    ADD_TASK_OUTPUT_SCHEMA,
    LIST_TASKS_INPUT_SCHEMA,
    LIST_TASKS_OUTPUT_SCHEMA,
    COMPLETE_TASK_INPUT_SCHEMA,
    COMPLETE_TASK_OUTPUT_SCHEMA,
    UPDATE_TASK_INPUT_SCHEMA,
    UPDATE_TASK_OUTPUT_SCHEMA,
    DELETE_TASK_INPUT_SCHEMA,
    DELETE_TASK_OUTPUT_SCHEMA,
)
from .tools.add_task import add_task_handler
from .tools.list_tasks import list_tasks_handler
from .tools.complete_task import complete_task_handler
from .tools.update_task import update_task_handler
from .tools.delete_task import delete_task_handler
from .utils.errors import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    AuthorizationError,
    DatabaseError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create MCP server instance
server = Server("todo-mcp-server")


@asynccontextmanager
async def lifespan_context():
    """Lifespan context manager for database connection pooling.

    Creates async database engine at startup and disposes at shutdown.
    Engine is stored in lifespan context for access by tool handlers.

    Yields:
        Dict with 'db_engine' key containing AsyncEngine instance
    """
    logger.info("Initializing MCP server lifespan context")

    # Create database engine with connection pooling
    engine = create_db_engine()
    logger.info("Database engine created with connection pool")

    try:
        # Provide engine to request handlers via context
        yield {"db_engine": engine}
    finally:
        # Cleanup: dispose engine and close all connections
        await engine.dispose()
        logger.info("Database engine disposed")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available MCP tools.

    Returns:
        List of Tool definitions with names, descriptions, and schemas
    """
    return [
        types.Tool(
            name="add_task",
            description="Create a new task for the authenticated user",
            inputSchema=ADD_TASK_INPUT_SCHEMA,
        ),
        types.Tool(
            name="list_tasks",
            description="Retrieve tasks for the authenticated user with optional filtering and pagination",
            inputSchema=LIST_TASKS_INPUT_SCHEMA,
        ),
        types.Tool(
            name="complete_task",
            description="Mark a task as completed for the authenticated user (idempotent operation)",
            inputSchema=COMPLETE_TASK_INPUT_SCHEMA,
        ),
        types.Tool(
            name="update_task",
            description="Modify task title, description, or completion status for the authenticated user",
            inputSchema=UPDATE_TASK_INPUT_SCHEMA,
        ),
        types.Tool(
            name="delete_task",
            description="Permanently remove a task from the database for the authenticated user",
            inputSchema=DELETE_TASK_INPUT_SCHEMA,
        ),
    ]


@server.call_tool()
async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Handle tool invocation requests.

    Routes tool calls to appropriate handlers with database session.

    Args:
        name: Tool name (add_task, list_tasks, complete_task, update_task, delete_task)
        arguments: Tool input parameters (includes jwt_token)

    Returns:
        List of TextContent with structured response or error

    Raises:
        ValueError: If tool name not recognized
    """
    logger.info(f"Tool invocation: {name}")

    # Get database engine from lifespan context
    ctx = server.request_context
    engine = ctx.lifespan_context["db_engine"]

    # Create new session for this invocation (stateless)
    from sqlmodel.ext.asyncio.session import AsyncSession

    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            # Route to appropriate tool handler
            if name == "add_task":
                result = await add_task_handler(arguments, session)
            elif name == "list_tasks":
                result = await list_tasks_handler(arguments, session)
            elif name == "complete_task":
                result = await complete_task_handler(arguments, session)
            elif name == "update_task":
                result = await update_task_handler(arguments, session)
            elif name == "delete_task":
                result = await delete_task_handler(arguments, session)
            else:
                raise ValueError(f"Unknown tool: {name}")

            # Convert result to MCP TextContent
            import json
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]

        except (AuthenticationError, ValidationError, NotFoundError, AuthorizationError, DatabaseError) as e:
            # Handle application-specific errors with structured response
            logger.error(f"Tool error: {name} - {type(e).__name__}: {str(e)}")

            import json
            error_response = {
                "error": type(e).__name__.replace("Error", "_ERROR").upper(),
                "message": str(e)
            }

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(error_response, indent=2)
                )
            ]

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {name} - {str(e)}", exc_info=True)

            import json
            error_response = {
                "error": "INTERNAL_ERROR",
                "message": f"An unexpected error occurred: {str(e)}"
            }

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(error_response, indent=2)
                )
            ]


async def main():
    """Main entry point for MCP server.

    Starts server with stdio transport and lifespan context management.
    """
    from mcp.server.stdio import stdio_server

    logger.info("Starting MCP Server: todo-mcp-server")
    logger.info("Registered 5 tools: add_task, list_tasks, update_task, complete_task, delete_task")

    # Run server with stdio transport and lifespan context
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
            raise_exceptions=True
        )


if __name__ == "__main__":
    asyncio.run(main())
