"""OpenAI Agent service for natural language task management.

This service initializes and manages the OpenAI Agent for processing user messages
and orchestrating MCP tool calls.
"""

import os
import json
import logging
from typing import Any, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.services.task_service import TaskService

from src.models.conversation import Message
from src.config import settings

logger = logging.getLogger(__name__)


def translate_mcp_error(error_code: str, error_message: str) -> str:
    """Translate MCP error codes to user-friendly messages.

    Args:
        error_code: MCP error code (e.g., AUTHENTICATION_ERROR, AUTHORIZATION_ERROR)
        error_message: Technical error message from MCP

    Returns:
        User-friendly error message without technical codes
    """
    error_code_upper = error_code.upper()

    if "AUTHENTICATION" in error_code_upper or "UNAUTHORIZED" in error_code_upper:
        return "Your authentication token expired. Please log in again."
    elif "AUTHORIZATION" in error_code_upper or "FORBIDDEN" in error_code_upper:
        return "I don't see that task in your list."
    elif "NOT_FOUND" in error_code_upper or "NOT FOUND" in error_code_upper:
        return "I couldn't find the task you're looking for."
    elif "VALIDATION" in error_code_upper or "BAD REQUEST" in error_code_upper:
        return "That doesn't seem right. Can you try again?"
    elif "DATABASE" in error_code_upper or "CONNECTION" in error_code_upper:
        return "I'm having trouble reaching the database. Please try again in a moment."
    else:
        return "Something went wrong. Please try again later."


class AgentService:
    """Service for managing OpenAI agent interactions with MCP tools.

    This service provides natural language interface to task management
    by orchestrating OpenAI GPT models with MCP server tools.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", mcp_base_url: str = "http://localhost:8001"):
        """Initialize the agent service.

        Args:
            api_key: OpenAI API key
            model: OpenAI model name (default: gpt-4o-mini)
            mcp_base_url: Base URL for MCP server
        """
        logger.debug(f"Initializing AgentService with model={model}, mcp_base_url={mcp_base_url}")

        self.api_key = api_key
        self.model = model
        self.mcp_base_url = mcp_base_url
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = self._build_system_prompt()
        self.tools = self._register_mcp_tools()

        logger.info(f"AgentService initialized with {len(self.tools)} tools")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent.

        Returns:
            System prompt string explaining role, tools, and constraints
        """
        return """You are a friendly and helpful task management assistant. Your role is to help users manage their tasks through natural conversation.

**Available Tools:**
You have access to the following task management tools:

1. **add_task**: Create a new task
   - Parameters: title (required), description (optional)
   - Use when user wants to create, add, or make a new task

2. **list_tasks**: Retrieve user's tasks with optional filtering
   - Parameters: completed (optional boolean), page (optional), page_size (optional)
   - Use when user wants to see, view, list, or show their tasks

3. **complete_task**: Mark a task as completed
   - Parameters: task_id (required)
   - Use when user wants to complete, finish, or mark done a task

4. **update_task**: Modify task details
   - Parameters: task_id (required), title (optional), description (optional), is_completed (optional)
   - Use when user wants to edit, change, or update a task

5. **delete_task**: Permanently remove a task
   - Parameters: task_id (required)
   - Use when user wants to delete, remove, or get rid of a task

**Tool Chaining for Complex Requests:**
You can invoke multiple tools in sequence to handle complex requests:
- When a user asks to "list and delete" or "show and update", chain the tools appropriately
- Pass results from one tool to the next tool when needed
- If one tool fails, inform the user and try an alternative approach
- Example: "List my tasks and delete all completed ones"
  1. Call list_tasks to get the task list
  2. Filter for completed tasks
  3. Call delete_task for each completed task ID
  4. Show the user remaining tasks and confirm deletions

**Important Constraints:**
- You MUST use the tools to perform any task operations - you cannot create/modify/delete tasks directly
- Always confirm actions to the user after tool execution
- If a tool fails, explain the error in user-friendly terms and continue with other operations
- When listing tasks, present them in a clear, readable format
- If you need a task_id to complete/update/delete, first list the tasks to find the correct ID
- For multi-step operations, continue even if one step fails - aggregate all results at the end

**Tone and Style:**
- Be conversational and friendly
- Use natural language, avoid technical jargon
- Anticipate user needs and offer helpful suggestions
- Confirm successful actions clearly
- When handling multiple operations, provide clear summaries (e.g., "Deleted 3 tasks. 7 tasks remaining.")

Example interactions:
- User: "Add a task to buy groceries"
  You: [Use add_task tool] "I've added 'Buy groceries' to your task list!"

- User: "Show me my tasks"
  You: [Use list_tasks tool] "Here are your tasks: [list tasks in readable format]"

- User: "Mark the grocery task as done"
  You: [First list tasks to find ID, then use complete_task] "Great! I've marked 'Buy groceries' as completed."

- User: "List my tasks and delete all completed ones"
  You: [Use list_tasks, then delete_task for each completed task] "I've deleted 3 completed tasks. You have 7 tasks remaining."
"""

    def _register_mcp_tools(self) -> list[dict[str, Any]]:
        """Register MCP tools as OpenAI function definitions.

        Returns:
            List of OpenAI function tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (1-255 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve user's tasks with optional filtering and pagination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status (true for completed, false for incomplete, omit for all)"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number (default: 1)"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Items per page (1-100, default: 20)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to mark as complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task title, description, or completion status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (1-255 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            },
                            "is_completed": {
                                "type": "boolean",
                                "description": "New completion status"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "UUID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def _execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: UUID,
        session: Session
    ) -> Dict[str, Any]:
        """Execute task tool using direct database operations.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            user_id: User ID for isolation
            session: Database session

        Returns:
            Tool execution result as dict
        """
        logger.info(f"Executing tool {tool_name} with parameters: {parameters}")

        try:
            if tool_name == "add_task":
                title = parameters.get("title")
                if not title:
                    raise ValueError("Title is required for add_task")
                description = parameters.get("description")
                task_dict = TaskService.create_task(session, user_id, title, description)
                logger.info(f"Successfully created task for {tool_name}")
                return task_dict

            elif tool_name == "list_tasks":
                completed = parameters.get("completed")
                if isinstance(completed, str):
                    completed = completed.lower() == 'true'
                page = int(parameters.get("page", 1))
                page_size = int(parameters.get("page_size", 20))
                result = TaskService.get_tasks(session, user_id, completed, page, page_size)
                logger.info(f"Successfully listed tasks for {tool_name}")
                return result

            elif tool_name == "complete_task":
                task_id_str = parameters.get("task_id")
                if not task_id_str:
                    raise ValueError("task_id is required for complete_task")
                task_id = UUID(task_id_str)
                result = TaskService.complete_task(session, user_id, task_id)
                logger.info(f"Successfully completed task {task_id} for {tool_name}")
                return result

            elif tool_name == "update_task":
                task_id_str = parameters.get("task_id")
                if not task_id_str:
                    raise ValueError("task_id is required for update_task")
                task_id = UUID(task_id_str)
                title = parameters.get("title")
                description = parameters.get("description")
                is_completed = parameters.get("is_completed")
                if isinstance(is_completed, str):
                    is_completed = is_completed.lower() == 'true'
                result = TaskService.update_task(session, user_id, task_id, title, description, is_completed)
                logger.info(f"Successfully updated task {task_id} for {tool_name}")
                return result

            elif tool_name == "delete_task":
                task_id_str = parameters.get("task_id")
                if not task_id_str:
                    raise ValueError("task_id is required for delete_task")
                task_id = UUID(task_id_str)
                result = TaskService.delete_task(session, user_id, task_id)
                logger.info(f"Successfully deleted task {task_id} for {tool_name}")
                return result

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool execution failed for {tool_name}: {error_msg}")
            return {"success": False, "error": error_msg}

    async def process_user_message(
        self,
        user_message: str,
        conversation_history: list[Message],
        user_id: UUID,
        jwt_token: str,
        session: Session
    ) -> dict[str, Any]:
        """Process user message and invoke tools as needed.

        Args:
            user_message: Users text message
            conversation_history: Previous messages in conversation
            user_id: UUID of the user
            jwt_token: JWT token (unused now)
            session: Database session

        Returns:
            Dictionary with:
                - content: Agents text response
                - tool_calls: List of tool invocations with results
        """
        logger.info(f"Processing message from user {user_id}: {user_message[:100]}...")
        logger.debug(f"Conversation history contains {len(conversation_history)} messages")

        # Build conversation context
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history (excluding tool_calls for simplicity)
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call OpenAI with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        tool_calls_data = []

        # Execute tool calls if present
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                parameters = json.loads(tool_call.function.arguments)

                try:
                    # Execute tool
                    result = await self._execute_tool(
                        tool_name=tool_name,
                        parameters=parameters,
                        user_id=user_id,
                        session=session
                    )

                    tool_calls_data.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "result": result
                    })

                    # Add tool result to messages and get final response
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                except Exception as e:
                    # Handle tool execution error - translate to user-friendly message
                    error_str = str(e)
                    user_friendly_error = translate_mcp_error(error_str, error_str)

                    tool_calls_data.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "result": {"error": user_friendly_error, "success": False}
                    })

                    # Pass user-friendly error to agent for contextual response
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": user_friendly_error, "success": False})
                    })

                    # Continue with next tool (don't break sequence)

            # Get final response after tool execution
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            final_content = final_response.choices[0].message.content or "I've completed the action."

        else:
            # No tool calls, use direct response
            final_content = message.content or "I'm here to help with your tasks!"
            logger.info(f"Agent response generated without tool calls for user {user_id}")

        logger.info(f"Agent response generated for user {user_id} with {len(tool_calls_data)} tool calls")
        return {
            "content": final_content,
            "tool_calls": tool_calls_data
        }


async def get_agent_service() -> AgentService:
    """Dependency injection for AgentService.

    Returns:
        Configured AgentService instance
    """
    return AgentService(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        mcp_base_url=settings.mcp_base_url
    )
