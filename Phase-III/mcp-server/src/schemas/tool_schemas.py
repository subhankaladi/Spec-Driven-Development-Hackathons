"""JSON Schema definitions for all MCP tools.

These schemas define input and output validation for the 5 stateless tools.
Schemas match contracts defined in specs/005-mcp-server-todo-tooling/contracts/*.json
"""

# Tool: add_task (Priority: P1 - MVP)
ADD_TASK_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "jwt_token": {
            "type": "string",
            "description": "JWT authentication token with user identity"
        },
        "title": {
            "type": "string",
            "description": "Task title (1-255 characters)",
            "minLength": 1,
            "maxLength": 255
        },
        "description": {
            "type": "string",
            "description": "Optional task description"
        }
    },
    "required": ["jwt_token", "title"]
}

ADD_TASK_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique task identifier"
        },
        "user_id": {
            "type": "string",
            "format": "uuid",
            "description": "Owner user identifier"
        },
        "title": {
            "type": "string",
            "description": "Task title"
        },
        "description": {
            "type": ["string", "null"],
            "description": "Task description (null if not provided)"
        },
        "is_completed": {
            "type": "boolean",
            "description": "Completion status (always false for new tasks)"
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "Task creation timestamp (ISO 8601)"
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "Last update timestamp (ISO 8601)"
        }
    },
    "required": ["id", "user_id", "title", "description", "is_completed", "created_at", "updated_at"]
}


# Tool: list_tasks (Priority: P1 - MVP)
LIST_TASKS_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "jwt_token": {
            "type": "string",
            "description": "JWT authentication token with user identity"
        },
        "completed": {
            "type": "boolean",
            "description": "Filter by completion status (optional)"
        },
        "page": {
            "type": "integer",
            "description": "Page number (1-indexed)",
            "minimum": 1,
            "default": 1
        },
        "page_size": {
            "type": "integer",
            "description": "Items per page",
            "minimum": 1,
            "maximum": 100,
            "default": 20
        }
    },
    "required": ["jwt_token"]
}

LIST_TASKS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "description": "Array of task objects matching filter",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "user_id": {"type": "string", "format": "uuid"},
                    "title": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "is_completed": {"type": "boolean"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "user_id", "title", "description", "is_completed", "created_at", "updated_at"]
            }
        },
        "total": {
            "type": "integer",
            "description": "Total number of tasks matching filter"
        },
        "page": {
            "type": "integer",
            "description": "Current page number"
        },
        "page_size": {
            "type": "integer",
            "description": "Items per page"
        },
        "total_pages": {
            "type": "integer",
            "description": "Total number of pages"
        }
    },
    "required": ["items", "total", "page", "page_size", "total_pages"]
}


# Tool: complete_task (Priority: P2)
COMPLETE_TASK_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "jwt_token": {
            "type": "string",
            "description": "JWT authentication token with user identity"
        },
        "task_id": {
            "type": "string",
            "format": "uuid",
            "description": "Task ID to mark as complete"
        }
    },
    "required": ["jwt_token", "task_id"]
}

COMPLETE_TASK_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "title": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "is_completed": {
            "type": "boolean",
            "description": "Always true after completion",
            "const": True
        },
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp refreshed on completion"
        }
    },
    "required": ["id", "user_id", "title", "description", "is_completed", "created_at", "updated_at"]
}


# Tool: update_task (Priority: P2)
UPDATE_TASK_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "jwt_token": {
            "type": "string",
            "description": "JWT authentication token with user identity"
        },
        "task_id": {
            "type": "string",
            "format": "uuid",
            "description": "Task ID to update"
        },
        "title": {
            "type": "string",
            "description": "New title (1-255 chars, optional)",
            "minLength": 1,
            "maxLength": 255
        },
        "description": {
            "type": "string",
            "description": "New description (optional)"
        },
        "is_completed": {
            "type": "boolean",
            "description": "New completion status (optional)"
        }
    },
    "required": ["jwt_token", "task_id"]
}

UPDATE_TASK_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "title": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "is_completed": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp refreshed on update"
        }
    },
    "required": ["id", "user_id", "title", "description", "is_completed", "created_at", "updated_at"]
}


# Tool: delete_task (Priority: P3)
DELETE_TASK_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "jwt_token": {
            "type": "string",
            "description": "JWT authentication token with user identity"
        },
        "task_id": {
            "type": "string",
            "format": "uuid",
            "description": "Task ID to delete"
        }
    },
    "required": ["jwt_token", "task_id"]
}

DELETE_TASK_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "deleted": {
            "type": "boolean",
            "description": "Always true on successful deletion",
            "const": True
        },
        "task_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the deleted task"
        }
    },
    "required": ["deleted", "task_id"]
}
