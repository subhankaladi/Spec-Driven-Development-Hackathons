"""AI Agent service for natural language task management using OpenAI SDK.

This service integrates OpenAI's chat completions API with function calling
to enable conversational task management. The agent is stateless, rebuilding
conversation context from the database on every request.
"""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
import json
import logging

from openai import OpenAI
from sqlmodel import Session

from ..config import settings
from ..models.tool_invocation import ToolInvocation
from .conversation_service import (
    create_conversation,
    create_message,
    get_conversation_messages,
    update_conversation_timestamp,
)
from .mcp_tools import create_task, list_tasks, update_task, delete_task

logger = logging.getLogger(__name__)

# System prompt that instructs the agent on its role and capabilities
SYSTEM_PROMPT = """You are a helpful task management assistant. Your role is to help users manage their todo tasks through natural language conversation.

You have access to the following capabilities:
- Create new tasks with a title and optional description
- List existing tasks (all tasks or filter by completion status)
- Update tasks (modify title, description, or completion status)
- Delete tasks

When users ask you to perform task operations, use the appropriate function tools available to you. Always:
1. Confirm successful operations with a friendly message
2. Ask for clarification when the user's request is ambiguous
3. Provide helpful information about the tasks when listing them
4. Be conversational and natural in your responses
5. If a task title is mentioned but multiple tasks match, ask the user to clarify which one

Examples of user requests and how to handle them:

**Creating Tasks:**
- "Create a task to buy milk" → Use create_task with title "Buy milk"
- "Add 'Review quarterly report' to my tasks" → Use create_task with title "Review quarterly report"

**Listing Tasks:**
- "Show me my tasks" / "List my tasks" / "What tasks do I have?" → Use list_tasks to retrieve all tasks
- "Show my completed tasks" → Use list_tasks with is_completed=True
- "Show incomplete tasks" / "What's left to do?" → Use list_tasks with is_completed=False

**Updating Tasks (with task identification):**
- "Mark 'Buy milk' as complete" → First list_tasks to find the task ID, then use update_task with is_completed=True
- "Complete the milk task" → First list_tasks to find tasks matching "milk", then update_task with is_completed=True
- "Rename 'Buy milk' to 'Buy groceries'" → First list_tasks to find the task ID, then use update_task with new title
- "Update the description for 'Project review'" → First list_tasks to find task, then update_task with new description
- "Mark task as incomplete" → If task reference is vague, ask which task or list tasks first

**Handling Ambiguous Task References:**
When the user mentions a task to update but the reference is unclear:
1. FIRST, use list_tasks to retrieve the user's current tasks
2. Look for tasks that match the user's description (by title keywords)
3. If EXACTLY ONE task matches → Proceed with the update using that task's ID
4. If MULTIPLE tasks match → Ask user to clarify which one (e.g., "I found 2 tasks with 'groceries': 'Buy groceries' and 'Plan grocery list'. Which one would you like to update?")
5. If NO tasks match → Inform user and ask for clarification (e.g., "I couldn't find a task matching 'xyz'. Would you like to see all your tasks?")

**Examples of disambiguation:**
- User: "Mark the grocery task as done"
  → First list_tasks, find tasks with "grocery" in title
  → If multiple found: "I found 2 grocery tasks: 'Buy groceries' and 'Grocery shopping list'. Which one should I mark as complete?"
  → If one found: Mark it complete and confirm
  → If none found: "I couldn't find a grocery task. Would you like to see all your tasks?"

- User: "Rename the report task"
  → First list_tasks, find tasks with "report" in title
  → If multiple: "I found 3 report tasks: 'Write monthly report', 'Review quarterly report', and 'Submit expense report'. Which one would you like to rename?"

**Deleting Tasks (with confirmation workflow):**
CRITICAL: NEVER delete a task without explicit user confirmation. Always follow the two-step delete process:

Step 1 - Identify and Request Confirmation:
- User: "Delete 'Buy milk'" or "Remove the grocery task"
- Agent: First use list_tasks to find the matching task(s)
- If exactly ONE task matches:
  → Respond: "I found the task 'Buy milk' (created on [date]). Are you sure you want to delete it? This action cannot be undone. Please confirm."
- If MULTIPLE tasks match:
  → Ask for clarification: "I found 2 tasks with 'grocery': 'Buy groceries' and 'Grocery list'. Which one would you like to delete?"
- If NO tasks match:
  → Inform user: "I couldn't find a task matching '[description]'. Would you like to see all your tasks?"

Step 2 - Execute After Confirmation:
- User: "Yes" / "Confirm" / "Do it" / "Delete it" / "Sure" (affirmative confirmation)
- Agent: Execute delete_task with the task_id from Step 1
- Respond: "I've deleted the task '[task title]'. The task has been permanently removed from your list."

NEVER execute delete_task in the first message - ALWAYS ask for confirmation first.

Examples of the two-step delete workflow:
1. User: "Delete my milk task"
   Agent: [List tasks, find "Buy milk"] "I found the task 'Buy milk' (created on Jan 15). Are you sure you want to delete it? This action cannot be undone."
   User: "Yes, delete it"
   Agent: [Execute delete_task] "I've deleted the task 'Buy milk'. The task has been permanently removed from your list."

2. User: "Remove the project task"
   Agent: [List tasks, find 2 matches] "I found 2 project-related tasks: 'Review project proposal' and 'Submit project report'. Which one would you like to delete?"
   User: "The report one"
   Agent: "I found the task 'Submit project report'. Are you sure you want to delete it? This action cannot be undone."
   User: "Yes"
   Agent: [Execute delete_task] "I've deleted the task 'Submit project report'. The task has been permanently removed."

When listing tasks, format them in a clear, readable way:
- If there are no tasks, let the user know their list is empty
- For each task, show the title, completion status, and description if available
- Use bullet points or numbered lists for better readability
- Distinguish between completed and incomplete tasks clearly
- If the list is long, summarize the count and ask if they want more details

Task Identification Strategy (IMPORTANT):
1. ALWAYS list tasks first when user mentions a task by title/description for update/delete
2. Match tasks by searching for keywords in the title (case-insensitive)
3. Validate exactly one match before proceeding with update/delete
4. When in doubt, ask the user to clarify - NEVER guess which task they mean

Delete Operation Safety Rules (CRITICAL):
1. NEVER call delete_task without explicit user confirmation
2. ALWAYS implement the two-step delete process:
   - First step: Identify task and ask "Are you sure? This cannot be undone."
   - Second step: After user confirms (yes/confirm/do it/sure), execute delete_task
3. Show task details (title, creation date) before asking for confirmation
4. Use the same task identification strategy as update operations (list first, match, clarify if ambiguous)
5. After deletion, confirm the task has been permanently removed

Be helpful, concise, and always validate that operations were successful before confirming to the user."""


def _build_openai_messages(
    conversation_messages: List[Any],
    new_user_message: str
) -> List[Dict[str, str]]:
    """Build OpenAI messages format from conversation history.

    Args:
        conversation_messages: List of Message objects from database
        new_user_message: Current user message to add

    Returns:
        List of message dicts in OpenAI format with role and content
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for msg in conversation_messages:
        messages.append({
            "role": msg.role,  # 'user' or 'assistant' (our 'agent' maps to 'assistant')
            "content": msg.content
        })

    # Add new user message
    messages.append({
        "role": "user",
        "content": new_user_message
    })

    return messages


def _get_openai_tools() -> List[Dict[str, Any]]:
    """Get OpenAI function tool definitions for MCP tools.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (required, 1-255 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks for the authenticated user with optional filtering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_completed": {
                            "type": "boolean",
                            "description": "Filter by completion status (omit for all tasks)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return (1-100, default 10)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to update (UUID format)"
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
                    "required": ["task_id"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to delete (UUID format)"
                        }
                    },
                    "required": ["task_id"],
                    "additionalProperties": False
                }
            }
        }
    ]


def _execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    user_id: UUID,
    session: Session
) -> Dict[str, Any]:
    """Execute an MCP tool function with the given arguments.

    Args:
        tool_name: Name of the MCP tool to execute
        tool_args: Arguments to pass to the tool
        user_id: UUID of the authenticated user
        session: Database session

    Returns:
        dict: Tool execution result

    Raises:
        ValueError: If tool_name is not recognized
    """
    # Add user_id to tool arguments (all MCP tools require it)
    tool_args_with_user = {**tool_args, "user_id": user_id, "session": session}

    # Execute the appropriate MCP tool
    if tool_name == "create_task":
        return create_task(
            title=tool_args.get("title"),
            description=tool_args.get("description"),
            **{"user_id": user_id, "session": session}
        )
    elif tool_name == "list_tasks":
        return list_tasks(
            user_id=user_id,
            session=session,
            is_completed=tool_args.get("is_completed"),
            limit=tool_args.get("limit", 10)
        )
    elif tool_name == "update_task":
        return update_task(
            task_id=UUID(tool_args["task_id"]),
            user_id=user_id,
            session=session,
            title=tool_args.get("title"),
            description=tool_args.get("description"),
            is_completed=tool_args.get("is_completed")
        )
    elif tool_name == "delete_task":
        return delete_task(
            task_id=UUID(tool_args["task_id"]),
            user_id=user_id,
            session=session
        )
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def process_message(
    user_message: str,
    user_id: UUID,
    session: Session,
    conversation_id: Optional[UUID] = None
) -> Tuple[str, UUID, UUID, List[Dict[str, Any]]]:
    """Process a user message through the AI agent and return response.

    This function implements the core agent workflow:
    1. Load or create conversation
    2. Load conversation history from database
    3. Build OpenAI messages with system prompt and history
    4. Call OpenAI API with function tools
    5. Execute any tool calls via MCP tools
    6. Persist user message and agent response to database
    7. Return agent response and metadata

    Args:
        user_message: The user's message text (max 5000 characters)
        user_id: UUID of the authenticated user (from JWT)
        session: Database session for transaction management
        conversation_id: Optional existing conversation ID (None creates new)

    Returns:
        tuple: (agent_response_text, conversation_id, message_id, tool_invocations)
            - agent_response_text: str - The agent's text response
            - conversation_id: UUID - The conversation ID (existing or new)
            - message_id: UUID - The ID of the agent's message
            - tool_invocations: List[dict] - List of tool invocations with details

    Raises:
        ValueError: If user_message exceeds 5000 characters
        OpenAIError: If OpenAI API call fails
    """
    # Validate message length
    if len(user_message) > 5000:
        raise ValueError("Message content exceeds maximum length of 5000 characters")

    # Initialize OpenAI client
    client = OpenAI(api_key=settings.openai_api_key)

    # Load or create conversation
    if conversation_id is None:
        conversation = create_conversation(
            user_id=user_id,
            title=None,  # Let first message define the conversation
            session=session
        )
        conversation_id = conversation.id
        conversation_messages = []
    else:
        conversation_messages = get_conversation_messages(
            conversation_id=conversation_id,
            session=session
        )

    # Build OpenAI messages format
    messages = _build_openai_messages(conversation_messages, user_message)

    # Get tool definitions
    tools = _get_openai_tools()

    # Call OpenAI API with function calling
    logger.info(f"Calling OpenAI API for user {user_id}, conversation {conversation_id}")
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Let the model decide when to use tools
        max_tokens=settings.agent_max_tokens,
        temperature=0.7  # Balanced between creative and deterministic
    )

    # Extract the assistant message
    assistant_message = response.choices[0].message
    tool_invocations = []

    # Process tool calls if any
    if assistant_message.tool_calls:
        logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool calls")

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

            try:
                # Execute the MCP tool
                tool_result = _execute_tool(tool_name, tool_args, user_id, session)

                tool_invocations.append({
                    "tool_name": tool_name,
                    "input_params": json.dumps(tool_args),
                    "output_result": json.dumps(tool_result),
                    "success": True,
                    "error_message": None
                })

                logger.info(f"Tool {tool_name} executed successfully")

            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {str(e)}")
                tool_invocations.append({
                    "tool_name": tool_name,
                    "input_params": json.dumps(tool_args),
                    "output_result": None,
                    "success": False,
                    "error_message": str(e)
                })

        # If tools were called, make a second API call to get the final response
        # Add tool results to messages
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Add tool results
        for i, tool_call in enumerate(assistant_message.tool_calls):
            tool_invocation = tool_invocations[i]
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_invocation["output_result"] if tool_invocation["success"]
                          else f"Error: {tool_invocation['error_message']}"
            })

        # Get final response from agent
        final_response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=settings.agent_max_tokens,
            temperature=0.7
        )

        agent_response_text = final_response.choices[0].message.content
    else:
        # No tool calls, use the assistant's direct response
        agent_response_text = assistant_message.content

    # Persist user message to database
    user_msg = create_message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        session=session
    )

    # Persist agent response to database
    agent_msg = create_message(
        conversation_id=conversation_id,
        role="agent",
        content=agent_response_text,
        session=session
    )

    # Persist tool invocations to database
    for invocation in tool_invocations:
        tool_invocation_record = ToolInvocation(
            message_id=agent_msg.id,
            tool_name=invocation["tool_name"],
            input_params=invocation["input_params"],
            output_result=invocation.get("output_result"),
            success=invocation["success"],
            error_message=invocation.get("error_message")
        )
        session.add(tool_invocation_record)

    # Commit tool invocations
    if tool_invocations:
        session.commit()
        logger.info(f"Persisted {len(tool_invocations)} tool invocations to database")

    # Update conversation timestamp
    update_conversation_timestamp(conversation_id, session)

    logger.info(f"Message processed successfully. Agent message ID: {agent_msg.id}")

    return (
        agent_response_text,
        conversation_id,
        agent_msg.id,
        tool_invocations
    )
