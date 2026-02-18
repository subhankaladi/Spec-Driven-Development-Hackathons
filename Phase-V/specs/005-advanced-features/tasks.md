# Tasks: Advanced Features

**Feature**: Advanced Features (Recurring Tasks, Due Dates & Reminders, Priorities, Tags, Search, Filter, Sort, Kafka, Dapr)
**Branch**: `005-advanced-features`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup & Environment

- [ ] T001 Set up development environment with Python 3.11, Node.js 18+, Docker, and Dapr
- [ ] T002 Install Dapr runtime and initialize with `dapr init`
- [ ] T003 Create Kafka Docker Compose file for local development
- [ ] T004 Update backend requirements.txt with new dependencies (SQLModel, Kafka client, Dapr SDK)
- [ ] T005 Update frontend package.json with any new dependencies for advanced features
- [ ] T006 [P] Create Alembic migration files for advanced feature database schema

## Phase 2: Foundational Components

- [ ] T010 Extend existing Task model with new fields (due_date, priority, parent_template_id) in backend/src/models/task.py
- [ ] T011 Create RecurringTaskTemplate model in backend/src/models/recurring_task.py
- [ ] T012 Create Reminder model in backend/src/models/reminder.py
- [ ] T013 Create Tag model in backend/src/models/tag.py
- [ ] T014 Create TaskTag junction model in backend/src/models/task_tag.py
- [ ] T015 Create TaskEventLog model in backend/src/models/event_log.py
- [ ] T016 Create database indexes for new tables based on data-model.md specifications
- [ ] T017 Update TaskInstance schema in backend/src/api/schemas/task.py with new fields
- [ ] T018 Create RecurringTaskTemplate schema in backend/src/api/schemas/recurring.py
- [ ] T019 Create Reminder schema in backend/src/api/schemas/reminder.py
- [ ] T020 Create Tag schema in backend/src/api/schemas/tag.py
- [ ] T021 Create Search schema in backend/src/api/schemas/search.py
- [ ] T022 Create Dapr client utilities in backend/src/dapr/client.py
- [ ] T023 Create Dapr configuration in backend/src/dapr/config.py
- [ ] T024 Create Kafka producer utilities in backend/src/events/producers/
- [ ] T025 Create Kafka consumer utilities in backend/src/events/consumers/
- [ ] T026 Update backend configuration with Kafka and Dapr settings in backend/src/config.py

## Phase 3: [US1] Recurring Tasks Management

**Goal**: Enable users to create tasks that repeat on a schedule (daily, weekly, monthly, yearly) so they don't have to manually recreate routine activities.

**Independent Test**: Create a recurring task and verify that new instances are automatically generated according to the schedule. Delivers immediate value by reducing manual task creation.

- [ ] T030 [US1] Create RecurringTaskService in backend/src/services/recurring_service.py
- [ ] T031 [US1] Implement recurring task creation logic with RFC 5545 RRULE validation
- [ ] T032 [US1] Implement recurring task retrieval logic with user isolation
- [ ] T033 [US1] Implement recurring task update logic with pattern modification
- [ ] T034 [US1] Implement recurring task deletion logic with instance cleanup
- [ ] T035 [US1] Create recurring task endpoints in backend/src/api/routes/recurring.py
- [ ] T036 [US1] Implement GET /users/{user_id}/recurring-tasks endpoint
- [ ] T037 [US1] Implement POST /users/{user_id}/recurring-tasks endpoint
- [ ] T038 [US1] Implement GET /users/{user_id}/recurring-tasks/{template_id} endpoint
- [ ] T039 [US1] Implement PUT /users/{user_id}/recurring-tasks/{template_id} endpoint
- [ ] T040 [US1] Implement PATCH /users/{user_id}/recurring-tasks/{template_id} endpoint
- [ ] T041 [US1] Implement DELETE /users/{user_id}/recurring-tasks/{template_id} endpoint
- [ ] T042 [US1] Create recurring task scheduler to generate new instances based on patterns
- [ ] T043 [US1] Implement logic to handle recurrence pattern changes affecting future instances
- [ ] T044 [P] [US1] Create RecurringTaskForm component in frontend/src/components/tasks/RecurringTaskForm.tsx
- [ ] T045 [P] [US1] Create recurrence pattern input UI with frequency and interval options
- [ ] T046 [P] [US1] Update task creation page to include recurring task options
- [ ] T047 [P] [US1] Update task detail page to show recurrence information
- [ ] T048 [P] [US1] Create useRecurringTask hook in frontend/src/lib/hooks/useRecurringTask.ts
- [ ] T049 [P] [US1] Create recurring task API client in frontend/src/lib/api/recurring.ts
- [ ] T050 [P] [US1] Update task types with recurring task fields in frontend/src/types/recurring.ts
- [ ] T051 [US1] Create tests for recurring task service functionality
- [ ] T052 [US1] Create tests for recurring task API endpoints
- [ ] T053 [US1] Create frontend component tests for recurring task UI

## Phase 4: [US2] Due Dates & Reminders

**Goal**: Allow users to assign due dates to tasks and receive timely reminders to ensure important deadlines are met.

**Independent Test**: Set a due date and reminder for a task, then verify that the user receives notification at the specified time. Delivers immediate value by helping users meet deadlines.

- [ ] T060 [US2] Create ReminderService in backend/src/services/reminder_service.py
- [ ] T061 [US2] Implement reminder creation logic with validation (reminder_time before due_date)
- [ ] T062 [US2] Implement reminder retrieval logic with user isolation
- [ ] T063 [US2] Implement reminder update logic for rescheduling
- [ ] T064 [US2] Implement reminder deletion logic
- [ ] T065 [US2] Create reminder endpoints in backend/src/api/routes/reminders.py
- [ ] T066 [US2] Implement GET /users/{user_id}/reminders endpoint
- [ ] T067 [US2] Implement POST /users/{user_id}/reminders endpoint
- [ ] T068 [US2] Implement PUT /users/{user_id}/reminders/{reminder_id} endpoint
- [ ] T069 [US2] Implement DELETE /users/{user_id}/reminders/{reminder_id} endpoint
- [ ] T070 [US2] Create reminder scheduler to trigger notifications at specified times
- [ ] T071 [US2] Implement reminder delivery mechanism (email/push/sms)
- [ ] T072 [US2] Update TaskService to handle due date assignments and overdue status
- [ ] T073 [P] [US2] Create Reminder UI component in frontend/src/components/tasks/DatePicker.tsx with reminder options
- [ ] T074 [P] [US2] Create reminders section in task detail page
- [ ] T075 [P] [US2] Create useReminders hook in frontend/src/lib/hooks/useReminders.ts
- [ ] T076 [P] [US2] Create reminder API client in frontend/src/lib/api/reminders.ts
- [ ] T077 [P] [US2] Update task types with reminder fields in frontend/src/types/reminder.ts
- [ ] T078 [P] [US2] Update TaskCard component to show due dates and overdue status
- [ ] T079 [P] [US2] Update dashboard to highlight overdue tasks
- [ ] T080 [US2] Create tests for reminder service functionality
- [ ] T081 [US2] Create tests for reminder API endpoints
- [ ] T082 [US2] Create frontend component tests for reminder UI

## Phase 5: [US3] Task Prioritization & Tagging

**Goal**: Enable users to assign priority levels (high, medium, low) and tags to tasks to better organize and categorize their work.

**Independent Test**: Create tasks with different priorities and tags, then verify they can be filtered and sorted accordingly. Delivers value by improving task organization and visibility.

- [ ] T090 [US3] Create TagService in backend/src/services/tag_service.py
- [ ] T091 [US3] Implement tag creation logic with user isolation and uniqueness validation
- [ ] T092 [US3] Implement tag retrieval logic with user filtering
- [ ] T093 [US3] Implement tag update logic
- [ ] T094 [US3] Implement tag deletion logic with association cleanup
- [ ] T095 [US3] Create tag endpoints in backend/src/api/routes/tags.py
- [ ] T096 [US3] Implement GET /users/{user_id}/tags endpoint
- [ ] T097 [US3] Implement POST /users/{user_id}/tags endpoint
- [ ] T098 [US3] Implement PUT /users/{user_id}/tags/{tag_id} endpoint
- [ ] T099 [US3] Implement DELETE /users/{user_id}/tags/{tag_id} endpoint
- [ ] T100 [US3] Update TaskService to handle priority assignments and tag associations
- [ ] T101 [US3] Implement many-to-many relationship between tasks and tags using TaskTag junction
- [ ] T102 [US3] Update task creation endpoint to accept tags
- [ ] T103 [US3] Update task update endpoint to manage tag associations
- [ ] T104 [P] [US3] Create PrioritySelector component in frontend/src/components/tasks/PrioritySelector.tsx
- [ ] T105 [P] [US3] Create TagManager component in frontend/src/components/tasks/TagManager.tsx
- [ ] T106 [P] [US3] Update TaskCard component to display priority indicators and tags
- [ ] T107 [P] [US3] Update task creation form to include priority and tag inputs
- [ ] T108 [P] [US3] Update task detail page to manage tags
- [ ] T109 [P] [US3] Create tag API client in frontend/src/lib/api/tags.ts
- [ ] T110 [P] [US3] Update task types with priority and tag fields in frontend/src/types/task.ts
- [ ] T111 [US3] Create tests for tag service functionality
- [ ] T112 [US3] Create tests for tag API endpoints
- [ ] T113 [US3] Create tests for task-tag relationship functionality
- [ ] T114 [US3] Create frontend component tests for priority and tag UI

## Phase 6: [US4] Advanced Search, Filter & Sort

**Goal**: Allow users to search, filter, and sort their tasks using multiple criteria to quickly find specific items.

**Independent Test**: Create multiple tasks with different attributes, then use search, filter, and sort functions to find specific subsets. Delivers value by improving task discovery efficiency.

- [ ] T120 [US4] Create SearchService in backend/src/services/search_service.py
- [ ] T121 [US4] Implement full-text search functionality using PostgreSQL capabilities
- [ ] T122 [US4] Implement filtering logic by priority, tags, due dates, and completion status
- [ ] T123 [US4] Implement sorting logic by due date, priority, creation date, and title
- [ ] T124 [US4] Implement compound filtering with multiple criteria
- [ ] T125 [US4] Implement pagination for search results
- [ ] T126 [US4] Create search endpoints in backend/src/api/routes/search.py
- [ ] T127 [US4] Implement POST /users/{user_id}/tasks/search endpoint
- [ ] T128 [US4] Update GET /users/{user_id}/tasks endpoint with advanced filtering options
- [ ] T129 [US4] Create SearchBar component in frontend/src/components/tasks/SearchBar.tsx
- [ ] T130 [P] [US4] Create FilterPanel component in frontend/src/components/tasks/FilterPanel.tsx
- [ ] T131 [P] [US4] Create SortControls component in frontend/src/components/tasks/SortControls.tsx
- [ ] T132 [P] [US4] Update task list page to incorporate search, filter, and sort functionality
- [ ] T133 [P] [US4] Create useAdvancedSearch hook in frontend/src/lib/hooks/useAdvancedSearch.ts
- [ ] T134 [P] [US4] Create search API client in frontend/src/lib/api/search.ts
- [ ] T135 [P] [US4] Update task types with search result fields in frontend/src/types/search.ts
- [ ] T136 [US4] Create tests for search service functionality
- [ ] T137 [US4] Create tests for search API endpoints
- [ ] T138 [US4] Create frontend component tests for search/filter/sort UI

## Phase 7: [US5] Event-Driven Task Processing

**Goal**: Process task-related events asynchronously using Kafka to improve scalability and responsiveness.

**Independent Test**: Trigger task events and verify they are processed asynchronously through the event stream. Improves system reliability and performance.

- [ ] T140 [US5] Create EventService in backend/src/services/event_service.py
- [ ] T141 [US5] Implement Kafka producer for task lifecycle events (creation, update, completion)
- [ ] T142 [US5] Implement event schema validation using Avro format
- [ ] T143 [US5] Create Kafka consumers for processing task events
- [ ] T144 [US5] Implement retry mechanism with exponential backoff for failed events
- [ ] T145 [US5] Implement idempotent event processing to handle duplicates
- [ ] T146 [US5] Update existing services to publish events to Kafka when appropriate
- [ ] T147 [US5] Create TaskEventLog functionality for audit trail
- [ ] T148 [US5] Implement dead letter queue for failed events
- [ ] T149 [US5] Create tests for event publishing functionality
- [ ] T150 [US5] Create tests for event consumption and processing
- [ ] T151 [US5] Create integration tests for end-to-end event flow

## Phase 8: [US6] Distributed Runtime with Dapr

**Goal**: Leverage Dapr for distributed application runtime to improve resilience and scalability.

**Independent Test**: Verify that services communicate reliably through Dapr sidecars and that the system remains resilient during partial failures.

- [ ] T160 [US6] Integrate Dapr service invocation for inter-service communication
- [ ] T161 [US6] Implement Dapr state management for consistent data access
- [ ] T162 [US6] Integrate Dapr pub/sub for event-driven communication
- [ ] T163 [US6] Implement circuit breaker patterns through Dapr for service resilience
- [ ] T164 [US6] Update main application to initialize Dapr components
- [ ] T165 [US6] Create Dapr component configuration files for state store and pub/sub
- [ ] T166 [US6] Update deployment configurations to include Dapr sidecars
- [ ] T167 [US6] Create tests for Dapr integration functionality
- [ ] T168 [US6] Create integration tests for Dapr-based service communication

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T180 Update existing task endpoints to support new advanced features (due dates, priorities, tags)
- [ ] T181 Add comprehensive error handling for all new features
- [ ] T182 Add logging for all new services and endpoints
- [ ] T183 Update API documentation with new endpoints and schemas
- [ ] T184 Create comprehensive integration tests covering all user stories
- [ ] T185 Update frontend to handle new task fields and relationships in all relevant components
- [ ] T186 Add proper loading states and error handling in frontend for new features
- [ ] T187 Create utility functions for date/time handling and recurrence calculations in frontend
- [ ] T188 Update frontend routing to support new advanced features
- [ ] T189 Conduct end-to-end testing of all user stories
- [ ] T190 Update README files with documentation for new features
- [ ] T191 Perform performance testing to ensure scalability requirements are met
- [ ] T192 Conduct security review to ensure user isolation is maintained across all new features

## Dependencies

### User Story Completion Order
1. **US1 (P1)**: Recurring Tasks Management - Foundation for task creation with recurrence
2. **US2 (P1)**: Due Dates & Reminders - Builds on basic task functionality
3. **US3 (P2)**: Task Prioritization & Tagging - Enhances task organization
4. **US4 (P2)**: Advanced Search, Filter & Sort - Depends on US3 for tag filtering
5. **US5 (P3)**: Event-Driven Task Processing - Can be implemented in parallel after core features
6. **US6 (P3)**: Distributed Runtime with Dapr - Infrastructure layer that can be integrated last

### Parallel Execution Opportunities
- **US1 & US2**: Can be developed in parallel as they operate on different aspects of tasks
- **US3 & US4**: Can be developed in parallel as tagging and search are largely independent
- **US5 & US6**: Can be developed in parallel as they represent different infrastructure concerns
- **Frontend components**: Can be developed in parallel with backend services once APIs are defined

## Implementation Strategy

### MVP Scope (US1-US2)
Focus on the highest priority features (P1) to deliver immediate value:
- Recurring tasks management
- Due dates & reminders
- Basic priority assignment

### Incremental Delivery
- Phase 1-2: Foundation and setup
- Phase 3: Recurring tasks (P1)
- Phase 4: Due dates & reminders (P1)
- Phase 5: Prioritization & tagging (P2)
- Phase 6: Search, filter & sort (P2)
- Phase 7-8: Infrastructure enhancements (P3)
- Phase 9: Polish and integration

This approach allows for early delivery of core functionality while maintaining the ability to incrementally add more advanced features.