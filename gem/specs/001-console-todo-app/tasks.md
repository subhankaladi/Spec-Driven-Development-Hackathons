# Tasks: Console Todo App

**Input**: Design documents from `specs/001-console-todo-app/`
**Prerequisites**: plan.md, spec.md, data-model.md

## Phase 1: Setup (Shared Infrastructure)
- [X] T001 Create project structure: `src/todo`, `tests`
- [X] T002 Create empty Python files from `plan.md`: `src/todo/__init__.py`, `src/todo/main.py`, `src/todo/task.py`, `src/todo/repository.py`, `tests/test_todo.py`
- [X] T003 Create `requirements.txt` with `pytest`

## Phase 2: Foundational (Blocking Prerequisites)
- [X] T004 [P] Implement `Task` class in `src/todo/task.py` based on `data-model.md`
- [X] T005 Implement in-memory `TaskRepository` class in `src/todo/repository.py` with methods for `add`, `get_all`, `update`, `delete`, `get_by_id`.

## Phase 3: User Stories (P1)
**Goal**: Implement core functionality: Add, View, and Mark tasks.

### User Story 1: Add a new task
- [X] T006 [US1] In `src/todo/main.py`, implement the `add_task` functionality.

### User Story 2: View the list of tasks
- [X] T007 [US2] In `src/todo/main.py`, implement the `view_tasks` functionality.

### User Story 5: Mark a task as complete or incomplete
- [X] T008 [US5] In `src/todo/main.py`, implement the `toggle_task_status` functionality.

## Phase 4: User Stories (P2)
**Goal**: Implement secondary functionality: Update and Delete tasks.

### User Story 3: Update an existing task
- [X] T009 [US3] In `src/todo/main.py`, implement the `update_task` functionality.

### User Story 4: Delete a task
- [X] T010 [US4] In `src/todo/main.py`, implement the `delete_task` functionality.

## Phase 5: Integration and Polish
- [X] T011 Implement the main application loop in `src/todo/main.py` to tie all the functionality together.
- [X] T012 Write tests in `tests/test_todo.py` for all features.
- [X] T013 Validate `quickstart.md` instructions.

## Dependencies & Execution Order
1.  **Phase 1 & 2** must be completed first.
2.  **Phase 3 & 4** can be worked on, but the application will not be fully functional until **Phase 5**.
3.  **Phase 5** integrates everything.
