# Data Model: Console Todo App

**Date**: 2025-12-06

This document defines the data structures used in the console to-do application.

## Task
The `Task` entity represents a single to-do item.

### Fields
- **id** (`int`): A unique, auto-incrementing identifier for the task.
- **title** (`str`): The title of the task.
- **description** (`str`): A detailed description of the task.
- **completed** (`bool`): The completion status of the task. Defaults to `False`.

### Validation Rules
- `title` is mandatory.

### Example
```python
{
    "id": 1,
    "title": "My first task",
    "description": "This is a description of my first task.",
    "completed": False
}
```
