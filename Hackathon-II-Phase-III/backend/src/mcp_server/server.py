"""
MCP Server for Todo Tooling.

Main server implementation exposing 5 tools for task management.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Optional

from mcp import Server, Tool
from mcp.types import TextContent

from .config import Config
from .database import init_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=Config.MCP_LOG_LEVEL)


# Initialize MCP Server
server = Server(Config.MCP_SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for the authenticated user",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Task title (required)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 2000,
                        "description": "Optional task description"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for the authenticated user, optionally filtered by completion status",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_completed": {
                        "type": "boolean",
                        "description": "If true, return only completed tasks; if false, only incomplete; if omitted, return all"
                    }
                }
            }
        ),
        Tool(
            name="update_task",
            description="Update the title or description of a task owned by the authenticated user",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task UUID to update"
                    },
                    "title": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "New task title (optional)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 2000,
                        "description": "New task description (optional)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task UUID to complete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task owned by the authenticated user",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task UUID to delete"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to implementations."""
    # Import tool handlers (lazy import to avoid circular dependencies)
    from .tools import add_task, complete_task, delete_task, list_tasks, update_task

    handler_map = {
        "add_task": add_task.handle,
        "list_tasks": list_tasks.handle,
        "update_task": update_task.handle,
        "complete_task": complete_task.handle,
        "delete_task": delete_task.handle,
    }

    if name not in handler_map:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Unknown tool: {name}"
                }
            })
        )]

    try:
        result = await handler_map[name](arguments)
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Tool error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            })
        )]


async def main() -> None:
    """Run the MCP server."""
    # Initialize database
    await init_db()
    logger.info(f"MCP Server '{Config.MCP_SERVER_NAME}' initialized")

    # Run server on stdio
    async with server:
        logger.info("MCP Server running on stdio transport")
        # Server handles stdio input/output via transport


if __name__ == "__main__":
    asyncio.run(main())
