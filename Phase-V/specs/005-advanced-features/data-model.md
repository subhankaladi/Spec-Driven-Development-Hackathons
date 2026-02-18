# Data Model: Advanced Features

## Overview
This document defines the data models for the advanced features including recurring tasks, due dates & reminders, task prioritization & tagging, and supporting entities for event-driven architecture.

## Entity Relationships

```
User (1) -----> (Many) TaskInstance
User (1) -----> (Many) RecurringTaskTemplate
User (1) -----> (Many) Reminder
User (1) -----> (Many) Tag

TaskInstance (Many) -----> (Many) Tag (via TaskTag junction)
RecurringTaskTemplate (1) -----> (Many) TaskInstance (generated instances)
Reminder (1) -----> (1) TaskInstance
```

## Entity Definitions

### 1. RecurringTaskTemplate
**Description**: Defines the pattern and parameters for recurring tasks

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Not Null | Unique identifier for the template |
| user_id | UUID | FK, Not Null | Owner of the recurring task |
| title | VARCHAR(255) | Not Null | Title of the recurring task |
| description | TEXT | Nullable | Description of the recurring task |
| priority | ENUM('low', 'medium', 'high') | Not Null, Default: 'medium' | Priority level |
| recurrence_pattern | JSONB | Not Null | Stores recurrence rule in RFC 5545 RRULE format |
| start_date | TIMESTAMP | Not Null | When the recurrence starts |
| end_date | TIMESTAMP | Nullable | When the recurrence ends (null for indefinite) |
| max_occurrences | INTEGER | Nullable | Max number of occurrences (null for indefinite) |
| is_active | BOOLEAN | Not Null, Default: true | Whether the recurrence is active |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |
| updated_at | TIMESTAMP | Not Null, Default: now() | Last update timestamp |

**Validation Rules**:
- recurrence_pattern must be a valid RFC 5545 RRULE
- start_date must be before end_date if end_date is provided
- max_occurrences must be positive if provided

### 2. TaskInstance
**Description**: Represents a specific occurrence of a recurring task or a one-time task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Not Null | Unique identifier for the task |
| user_id | UUID | FK, Not Null | Owner of the task |
| title | VARCHAR(255) | Not Null | Title of the task |
| description | TEXT | Nullable | Description of the task |
| priority | ENUM('low', 'medium', 'high') | Not Null, Default: 'medium' | Priority level |
| due_date | TIMESTAMP | Nullable | Due date for the task |
| is_completed | BOOLEAN | Not Null, Default: false | Completion status |
| parent_template_id | UUID | FK, Nullable | Link to recurring template if applicable |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |
| updated_at | TIMESTAMP | Not Null, Default: now() | Last update timestamp |

**Validation Rules**:
- If parent_template_id is set, the task is an instance of a recurring task
- Only tasks without a parent_template_id can be manually deleted

### 3. Reminder
**Description**: Configuration for task reminders

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Not Null | Unique identifier for the reminder |
| task_instance_id | UUID | FK, Not Null | Associated task instance |
| user_id | UUID | FK, Not Null | Owner of the reminder |
| reminder_time | TIMESTAMP | Not Null | When the reminder should trigger |
| method | ENUM('email', 'push', 'sms') | Not Null | How to deliver the reminder |
| is_sent | BOOLEAN | Not Null, Default: false | Whether reminder has been sent |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |
| updated_at | TIMESTAMP | Not Null, Default: now() | Last update timestamp |

**Validation Rules**:
- reminder_time must be before the associated task's due_date
- Each task_instance can have multiple reminders at different times

### 4. Tag
**Description**: Categories for organizing tasks

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Not Null | Unique identifier for the tag |
| user_id | UUID | FK, Not Null | Owner of the tag |
| name | VARCHAR(100) | Not Null, Unique per user | Name of the tag |
| color | VARCHAR(7) | Nullable | Color code for UI display |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |
| updated_at | TIMESTAMP | Not Null, Default: now() | Last update timestamp |

**Validation Rules**:
- Tag names must be unique per user
- Color must be a valid hex color code if provided

### 5. TaskTag (Junction Table)
**Description**: Many-to-many relationship between TaskInstance and Tag

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_instance_id | UUID | FK, PK, Not Null | Associated task instance |
| tag_id | UUID | FK, PK, Not Null | Associated tag |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |

**Validation Rules**:
- Combination of task_instance_id and tag_id must be unique

### 6. TaskEventLog
**Description**: Log of events for audit and event-driven processing

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Not Null | Unique identifier for the event |
| user_id | UUID | FK, Not Null | User associated with the event |
| task_instance_id | UUID | FK, Nullable | Task associated with the event |
| event_type | VARCHAR(50) | Not Null | Type of event (created, updated, completed, etc.) |
| payload | JSONB | Not Null | Event data in JSON format |
| processed_by_kafka | BOOLEAN | Not Null, Default: false | Whether event was processed by Kafka |
| created_at | TIMESTAMP | Not Null, Default: now() | Creation timestamp |

**Validation Rules**:
- event_type must be one of the predefined event types
- payload must conform to the schema for the event_type

## Indexes

### TaskInstance Table
- `idx_taskinstance_user_id`: Index on user_id for efficient user-based queries
- `idx_taskinstance_due_date`: Index on due_date for efficient due date queries
- `idx_taskinstance_priority`: Index on priority for efficient priority-based queries
- `idx_taskinstance_completion_status`: Index on is_completed for efficient status queries
- `idx_taskinstance_parent_template`: Index on parent_template_id for recurring task queries
- `idx_taskinstance_user_priority_due`: Composite index on (user_id, priority, due_date) for dashboard queries

### RecurringTaskTemplate Table
- `idx_recurringtasktemplate_user_id`: Index on user_id for efficient user-based queries
- `idx_recurringtasktemplate_active`: Index on is_active for efficient active template queries

### Reminder Table
- `idx_reminder_user_time`: Index on (user_id, reminder_time) for efficient reminder scheduling
- `idx_reminder_task_instance`: Index on task_instance_id for task-based queries
- `idx_reminder_sent_status`: Index on is_sent for efficient processing queries

### Tag Table
- `idx_tag_user_name`: Unique index on (user_id, name) for efficient tag lookup
- `idx_tag_user_id`: Index on user_id for efficient user-based queries

### TaskTag Table
- `idx_tasktag_task_instance`: Index on task_instance_id for task-based queries
- `idx_tasktag_tag`: Index on tag_id for tag-based queries

### TaskEventLog Table
- `idx_taskeventlog_user_created`: Index on (user_id, created_at) for user timeline queries
- `idx_taskeventlog_processed`: Index on processed_by_kafka for processing queries
- `idx_taskeventlog_event_type`: Index on event_type for event-type queries

## State Transitions

### TaskInstance States
- `created` → `in_progress` → `completed` | `cancelled`
- `created` → `overdue` (automatically when due_date passes)
- `completed` → `reopened` (for recurring tasks)

### Reminder States
- `scheduled` → `sent` | `failed`
- `sent` → `delivered` (for push/email notifications)

## API Contract Considerations

### TaskInstance Endpoints
- GET /users/{user_id}/tasks - Retrieve tasks with filtering, sorting, and pagination
- POST /users/{user_id}/tasks - Create a new one-time task
- GET /users/{user_id}/tasks/{task_id} - Retrieve a specific task
- PUT /users/{user_id}/tasks/{task_id} - Update a task completely
- PATCH /users/{user_id}/tasks/{task_id} - Partially update a task
- DELETE /users/{user_id}/tasks/{task_id} - Delete a task

### RecurringTaskTemplate Endpoints
- GET /users/{user_id}/recurring-tasks - Retrieve recurring task templates
- POST /users/{user_id}/recurring-tasks - Create a recurring task template
- GET /users/{user_id}/recurring-tasks/{template_id} - Retrieve a specific template
- PUT /users/{user_id}/recurring-tasks/{template_id} - Update a template
- PATCH /users/{user_id}/recurring-tasks/{template_id} - Partially update a template
- DELETE /users/{user_id}/recurring-tasks/{template_id} - Delete a template

### Tag Endpoints
- GET /users/{user_id}/tags - Retrieve user's tags
- POST /users/{user_id}/tags - Create a new tag
- GET /users/{user_id}/tags/{tag_id} - Retrieve a specific tag
- PUT /users/{user_id}/tags/{tag_id} - Update a tag
- DELETE /users/{user_id}/tags/{tag_id} - Delete a tag

### Search Endpoints
- POST /users/{user_id}/tasks/search - Advanced search with filters and sorting