from __future__ import annotations

import asyncio
import os
import logging
from dataclasses import dataclass
from typing import Any, Optional

from agents import Agent, RunContextWrapper, Runner, function_tool

from src.chat.mcp_client import MCPClient
from src.models.message import Message


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a Todo assistant.

Rules:
- You MUST use the provided MCP tools for all task operations (add/list/update/complete/delete).
- Do not modify tasks in any other way.
- When the user asks for a task operation, select the single correct tool and call it.
- After tool execution, respond with a friendly confirmation and any relevant results.
- If the tool fails, explain the error clearly and suggest a next step.
"""


@dataclass
class ChatRunContext:
    user_id: str
    mcp: MCPClient


@function_tool
async def add_task(ctx: RunContextWrapper[ChatRunContext], title: str, description: Optional[str] = None) -> dict[str, Any]:
    result = await ctx.context.mcp.call_tool("add_task", {"title": title, "description": description})
    return result.__dict__


@function_tool
async def list_tasks(ctx: RunContextWrapper[ChatRunContext], filter_completed: Optional[bool] = None) -> dict[str, Any]:
    args: dict[str, Any] = {}
    if filter_completed is not None:
        args["filter_completed"] = filter_completed
    result = await ctx.context.mcp.call_tool("list_tasks", args)
    return result.__dict__


@function_tool
async def update_task(
    ctx: RunContextWrapper[ChatRunContext],
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    args: dict[str, Any] = {"task_id": task_id}
    if title is not None:
        args["title"] = title
    if description is not None:
        args["description"] = description
    result = await ctx.context.mcp.call_tool("update_task", args)
    return result.__dict__


@function_tool
async def complete_task(ctx: RunContextWrapper[ChatRunContext], task_id: str) -> dict[str, Any]:
    result = await ctx.context.mcp.call_tool("complete_task", {"task_id": task_id})
    return result.__dict__


@function_tool
async def delete_task(ctx: RunContextWrapper[ChatRunContext], task_id: str) -> dict[str, Any]:
    result = await ctx.context.mcp.call_tool("delete_task", {"task_id": task_id})
    return result.__dict__


def build_agent() -> Agent[ChatRunContext]:
    return Agent[ChatRunContext](
        name="Todo Chat Agent",
        instructions=SYSTEM_PROMPT,
        tools=[add_task, list_tasks, update_task, complete_task, delete_task],
    )


def validate_required_configs():
    """
    Validate required environment/configuration variables for the agent.
    """
    # In a real implementation, we might check for OPENAI_API_KEY
    # For now, we'll validate that the system can initialize properly
    logger.info("Validating required configurations for chat agent")

    # Check if we can import the required modules
    try:
        import agents
        import src.mcp_server.tools
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        raise ValueError(f"Required dependency not available: {e}")

    # Log that validation passed
    logger.info("Configuration validation passed")


async def run_chat_agent(user_id: str, conversation_id: str, user_message: str, history: list = None) -> dict[str, Any]:
    """
    Run the chat agent with the given user message and history, and return the response.
    """
    # Validate configuration before proceeding
    validate_required_configs()

    mcp_client = MCPClient()
    try:
        agent = build_agent()
        run_ctx = ChatRunContext(user_id=user_id, mcp=mcp_client)

        # Prepare the input with history context if available
        input_with_context = user_message
        if history:
            # Build a context string from the conversation history
            history_context = "\n".join([
                f"{msg.role.capitalize()}: {msg.content}"
                for msg in history
            ])
            input_with_context = f"Conversation history:\n{history_context}\n\nUser: {user_message}"

        result = await Runner.run(agent, input=input_with_context, context=run_ctx)

        assistant_message = (result.final_output or "").strip()
        return {
            "response_text": assistant_message,
            "conversation_id": conversation_id
        }
    finally:
        await mcp_client.aclose()
