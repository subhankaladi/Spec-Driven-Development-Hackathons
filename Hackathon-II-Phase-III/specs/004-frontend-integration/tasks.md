---
description: "Task list for Frontend Web Application & Integration implementation"
---

# Tasks: Frontend Web Application & Integration

**Input**: Design documents from `/specs/004-frontend-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in this feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` at repository root
- Paths shown below follow the established project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [x] T001 Install Better Auth and React Hook Form dependencies in frontend/package.json
- [x] T002 [P] Create environment configuration file in frontend/.env.example
- [x] T003 [P] Create TypeScript types for auth and tasks in frontend/types/index.ts
- [x] T004 Configure Better Auth client with JWT support in frontend/lib/auth.ts
- [x] T005 Create authenticated API client with auto-headers in frontend/lib/api-client.ts
- [x] T006 [P] Create utility functions in frontend/lib/utils.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create reusable Button component in frontend/components/ui/Button.tsx
- [x] T008 [P] Create reusable Input component in frontend/components/ui/Input.tsx
- [x] T009 [P] Create reusable Spinner component in frontend/components/ui/Spinner.tsx
- [x] T010 [P] Create reusable Modal component in frontend/components/ui/Modal.tsx
- [x] T011 Create useAuth hook for auth state management in frontend/hooks/useAuth.tsx
- [x] T012 Create route protection middleware in frontend/middleware.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Sign In (Priority: P1) 🎯 MVP

**Goal**: Implement authentication flow allowing users to sign up, sign in, and sign out

**Independent Test**: Can be fully tested by attempting to create a new account with valid credentials, signing in, verifying the user sees their dashboard, and confirming unauthenticated access is blocked.

### Implementation for User Story 1

- [x] T013 [US1] Create SignInForm component with validation in frontend/components/auth/SignInForm.tsx
- [x] T014 [P] [US1] Create SignUpForm component with validation in frontend/components/auth/SignUpForm.tsx
- [x] T015 [US1] Create sign-in page in frontend/app/auth/signin/page.tsx
- [x] T016 [P] [US1] Create sign-up page in frontend/app/auth/signup/page.tsx
- [x] T017 [US1] Create AuthGuard component for protected routes in frontend/components/auth/AuthGuard.tsx
- [x] T018 [US1] Update root layout with auth provider in frontend/app/layout.tsx
- [x] T019 [US1] Add sign-out functionality to layout header in frontend/components/Header.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task List and Dashboard View (Priority: P1)

**Goal**: Display authenticated user's tasks in a clear dashboard with loading, error, and empty states

**Independent Test**: Can be fully tested by signing in, viewing the task list, verifying only the user's own tasks are displayed, and confirming the interface adapts to different screen sizes.

### Implementation for User Story 2

- [x] T020 [US2] Create useTasks hook for task data fetching in frontend/hooks/useTasks.ts
- [x] T021 [US2] Create TaskList container component in frontend/components/tasks/TaskList.tsx
- [x] T022 [P] [US2] Create TaskCard component for individual tasks in frontend/components/tasks/TaskCard.tsx
- [x] T023 [P] [US2] Create EmptyState component for no tasks in frontend/components/tasks/EmptyState.tsx
- [x] T024 [US2] Create dashboard layout with protection in frontend/app/dashboard/layout.tsx
- [x] T025 [US2] Create dashboard page with task list in frontend/app/dashboard/page.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Create New Task (Priority: P1)

**Goal**: Enable authenticated users to create new tasks with title and optional description

**Independent Test**: Can be fully tested by signing in, creating a new task with title and description, and verifying it appears in the task list.

### Implementation for User Story 3

- [x] T026 [US3] Create TaskForm component for create/edit in frontend/components/tasks/TaskForm.tsx
- [x] T027 [US3] Add createTask function to useTasks hook in frontend/hooks/useTasks.ts
- [x] T028 [US3] Integrate task creation flow in dashboard page in frontend/app/dashboard/page.tsx

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Update and Complete Tasks (Priority: P1)

**Goal**: Allow users to edit task details and toggle completion status

**Independent Test**: Can be fully tested by editing an existing task's details, toggling its completion status, and verifying the changes persist.

### Implementation for User Story 4

- [x] T029 [US4] Add updateTask function to useTasks hook in frontend/hooks/useTasks.ts
- [x] T030 [US4] Add toggleComplete function to useTasks hook in frontend/hooks/useTasks.ts
- [x] T031 [US4] Add edit mode to TaskCard component in frontend/components/tasks/TaskCard.tsx
- [x] T032 [US4] Add completion toggle UI to TaskCard component in frontend/components/tasks/TaskCard.tsx
- [x] T033 [US4] Integrate edit flow with TaskForm in frontend/app/dashboard/page.tsx

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Enable task deletion with confirmation dialog

**Independent Test**: Can be fully tested by deleting a task and verifying it no longer appears in the task list.

### Implementation for User Story 5

- [x] T034 [US5] Create DeleteConfirm modal component in frontend/components/tasks/DeleteConfirm.tsx
- [x] T035 [US5] Add deleteTask function to useTasks hook in frontend/hooks/useTasks.ts
- [x] T036 [US5] Integrate delete flow with confirmation in TaskCard in frontend/components/tasks/TaskCard.tsx

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Error Handling and Recovery (Priority: P2)

**Goal**: Provide clear error feedback with retry options

**Independent Test**: Can be fully tested by simulating network errors and verifying appropriate error messages are displayed with recovery options.

### Implementation for User Story 6

- [x] T037 [US6] Create Toast notification component in frontend/components/ui/Toast.tsx
- [x] T038 [US6] Create useToast hook for notifications in frontend/hooks/useToast.tsx
- [x] T039 [US6] Create error boundary page in frontend/app/error.tsx
- [x] T040 [US6] Enhance API client with error mapping and retry in frontend/lib/api-client.ts
- [x] T041 [US6] Integrate toast notifications in dashboard via Providers in frontend/components/Providers.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T042 [P] Create home/landing page for unauthenticated users in frontend/app/page.tsx
- [x] T043 [P] Create 404 not-found page in frontend/app/not-found.tsx
- [x] T044 [P] Create TaskFilter component for filtering tasks in frontend/components/tasks/TaskFilter.tsx
- [x] T045 Verify responsive design on all components (320px-1920px)
- [x] T046 Verify loading states on all async operations
- [x] T047 Run quickstart.md validation for frontend integration features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Authentication first
- **User Story 2 (Phase 4)**: Depends on US1 - Need auth to view dashboard
- **User Story 3 (Phase 5)**: Depends on US2 - Need dashboard to create tasks
- **User Story 4 (Phase 6)**: Depends on US2 - Need task list to edit tasks
- **User Story 5 (Phase 7)**: Depends on US2 - Need task list to delete tasks
- **User Story 6 (Phase 8)**: Depends on Foundational - Can run after foundation
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Depends on User Story 1 (needs auth)
- **User Story 3 (P1)**: Depends on User Story 2 (needs dashboard)
- **User Story 4 (P1)**: Depends on User Story 2 (needs task list)
- **User Story 5 (P2)**: Depends on User Story 2 (needs task list)
- **User Story 6 (P2)**: Can run after Foundational (independent of task features)

### Within Each User Story

- Types/models before services/hooks
- Hooks before components
- Components before pages
- Core implementation before integration

### Parallel Opportunities

- T002, T003, T006 can run in parallel (Setup phase)
- T007, T008, T009, T010 can run in parallel (UI components)
- T013, T014 can run in parallel (auth forms)
- T015, T016 can run in parallel (auth pages)
- T022, T023 can run in parallel (task components)
- T042, T043, T044 can run in parallel (polish phase)

---

## Parallel Example: Foundational Phase

```bash
# Launch UI components together:
Task: "Create reusable Button component in frontend/components/ui/Button.tsx"
Task: "Create reusable Input component in frontend/components/ui/Input.tsx"
Task: "Create reusable Spinner component in frontend/components/ui/Spinner.tsx"
Task: "Create reusable Modal component in frontend/components/ui/Modal.tsx"

# Then sequentially:
Task: "Create useAuth hook for auth state management in frontend/hooks/useAuth.ts"
Task: "Create route protection middleware in frontend/middleware.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test sign-up/sign-in independently
5. Complete Phase 4: User Story 2 (Dashboard)
6. **STOP and VALIDATE**: Test task viewing
7. Complete Phase 5: User Story 3 (Create Tasks)
8. **STOP and VALIDATE**: Test task creation

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Authentication works
3. Add User Story 2 → Test independently → Dashboard visible
4. Add User Story 3 → Test independently → Can create tasks (MVP!)
5. Add User Story 4 → Test independently → Can edit tasks
6. Add User Story 5 → Test independently → Can delete tasks
7. Add User Story 6 → Test independently → Error handling works
8. Polish phase → Final validation

---

## Task Summary

| Phase | Task Count | Key Deliverables |
|-------|------------|------------------|
| Setup | 6 | Dependencies, types, auth client, API client |
| Foundational | 6 | UI components, useAuth hook, middleware |
| User Story 1 | 7 | Auth forms, auth pages, route protection |
| User Story 2 | 6 | useTasks hook, TaskList, TaskCard, dashboard |
| User Story 3 | 3 | TaskForm, create flow integration |
| User Story 4 | 5 | Update/toggle functions, edit mode |
| User Story 5 | 3 | DeleteConfirm, delete flow |
| User Story 6 | 5 | Toast, error boundary, error handling |
| Polish | 6 | Home page, 404, filter, validations |

**Total Tasks**: 47
**Parallel Opportunities**: 14 tasks marked [P]
**MVP Scope**: Phases 1-5 (28 tasks) - Authentication + Dashboard + Create Tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing frontend structure with Next.js 16+ already in place
