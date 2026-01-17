# Tasks: Frontend & Integration

**Input**: Design documents from `/specs/003-frontend/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md (recommended), research.md (recommended)
**Status**: READY - 71 tasks across 9 phases
**Feature Branch**: `003-frontend`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend source: `frontend/src/`
- Frontend tests: `frontend/tests/`
- Frontend root: `frontend/`

---

## Phase 1: Setup

**Purpose**: Project initialization and environment configuration

- [X] T001 Create frontend directory structure per implementation plan
- [X] T002 Initialize Next.js 16+ project with TypeScript, Tailwind CSS, ESLint, App Router, src-dir
- [X] T003 [P] Install Axios dependency for HTTP client
- [X] T004 [P] Install testing dependencies (@testing-library/react, @testing-library/jest-dom, @testing-library/user-event, jest, jest-environment-jsdom)
- [X] T005 [P] Create frontend/.env.local with NEXT_PUBLIC_API_URL configuration
- [X] T006 [P] Configure jest.config.js with next-jest integration and module aliases
- [X] T007 [P] Create jest.setup.js with testing-library jest-dom
- [X] T008 [P] Update frontend/package.json with test scripts (test, test:watch, test:e2e)
- [X] T009 [P] Create all required directories in frontend/src (components, lib, context, types, tests)
- [X] T010 [P] Configure tailwind.config.ts with custom color palette (primary, danger, success) and breakpoints

**Checkpoint**: Project structure and dependencies ready

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 [P] Create frontend/src/types/auth.ts with User, AuthState, AuthContextType interfaces
- [X] T012 [P] Create frontend/src/types/tasks.ts with Task, TaskListResponse, TaskCreateRequest, TaskUpdateRequest interfaces
- [X] T013 [P] Create frontend/src/types/api.ts with ErrorResponse interface
- [X] T014 [P] Create frontend/src/types/ui.ts with LoadingState, AsyncState, PaginationState, ModalState interfaces
- [X] T015 [P] Create frontend/src/lib/utils/validation.ts with validateEmail, validatePassword, validateTaskTitle functions
- [X] T016 [P] Create frontend/src/lib/utils/storage.ts with getToken, setToken, removeToken, getUserFromToken functions
- [X] T017 [P] Create frontend/src/lib/api/client.ts with Axios singleton instance and interceptors for auth headers
- [X] T018 [P] Create frontend/src/lib/api/auth.ts with signUp, signIn API methods
- [X] T019 [P] Create frontend/src/lib/api/tasks.ts with getTasks, createTask, getTask, updateTask, deleteTask API methods
- [X] T020 [P] Create frontend/src/context/AuthContext.tsx with AuthContextProvider and AuthContext export
- [X] T021 Create frontend/src/lib/hooks/useAuth.ts custom hook for accessing auth context
- [X] T022 Create frontend/middleware.ts for route protection (redirect unauthenticated users to /signin)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Authentication Flow (Priority: P1)

**Goal**: Users can sign up, sign in, and sign out through the web application interface

**Independent Test**: Sign up with new credentials, sign in with existing credentials, sign out successfully

### Implementation for User Story 1

- [X] T023 [P] Create frontend/src/components/ui/Button.tsx with primary, secondary, danger, ghost variants and sm, md, lg sizes
- [X] T024 [P] Create frontend/src/components/ui/Input.tsx with label, error display, and touched state support
- [X] T025 [P] Create frontend/src/components/auth/SignInForm.tsx with form state, validation, and sign in logic
- [X] T026 [P] Create frontend/src/components/auth/SignUpForm.tsx with form state, validation, confirm password, and sign up logic
- [X] T027 Create frontend/src/app/(auth)/layout.tsx with centered card layout and branding
- [X] T028 [US1] Create frontend/src/app/(auth)/signin/page.tsx with SignInForm component and navigation links
- [X] T029 [US1] Create frontend/src/app/(auth)/signup/page.tsx with SignUpForm component and navigation links
- [X] T030 [US1] Implement redirect to /tasks after successful sign in or sign up in AuthContext
- [X] T031 [US1] Implement sign out in AuthContext (clear token, redirect to /signin)
- [X] T032 [US1] Add error message display for invalid credentials in SignInForm
- [X] T033 [US1] Add error message display for duplicate email in SignUpForm
- [X] T034 [US1] Add email validation (format check) in SignUpForm before API call

**Checkpoint**: User Story 1 complete - authentication flow works

---

## Phase 4: User Story 2 - Task Management Dashboard (Priority: P1)

**Goal**: Authenticated users can view their task list and toggle completion status

**Independent Test**: Sign in, view task list, toggle task completion, pagination works

### Implementation for User Story 2

- [X] T035 [P] Create frontend/src/components/ui/Checkbox.tsx with large click area and checked/unchecked states
- [X] T036 [P] Create frontend/src/components/tasks/TaskCard.tsx with task display, checkbox, edit/delete actions
- [X] T037 [P] Create frontend/src/components/tasks/TaskEmptyState.tsx with message and create task CTA
- [X] T038 [US2] Create frontend/src/lib/hooks/useTasks.ts custom hook with fetching, pagination, and CRUD operations
- [X] T039 [US2] Create frontend/src/components/tasks/TaskList.tsx with task cards, loading, error, empty states
- [X] T040 [US2] Create frontend/src/app/(dashboard)/layout.tsx with navigation bar, user menu, sign out action
- [X] T041 [US2] Create frontend/src/app/(dashboard)/tasks/page.tsx with TaskList component and create task button
- [X] T042 [US2] Implement task list fetching on mount in useTasks hook
- [X] T043 [US2] Implement optimistic UI update for task completion toggle in useTasks
- [X] T044 [US2] Add loading state display during task list fetch
- [X] T045 [US2] Add error message display for task list fetch failures
- [X] T046 [US2] Add empty state display when user has no tasks
- [X] T047 [US2] Implement pagination controls in TaskList component
- [X] T048 [US2] Handle task click to navigate to detail view in TaskCard component

**Checkpoint**: User Story 2 complete - task management dashboard works

---

## Phase 5: User Story 3 - Create Tasks (Priority: P1)

**Goal**: Authenticated users can create new tasks with title and optional description

**Independent Test**: Navigate to create task page, enter title, submit, see task in list

### Implementation for User Story 3

- [X] T049 [P] Create frontend/src/components/ui/TextArea.tsx with label, error display, and touched state support
- [X] T050 [P] Create frontend/src/components/ui/Modal.tsx with isOpen state, content, actions, and close functionality
- [X] T051 [P] Create frontend/src/components/tasks/TaskForm.tsx with title/description inputs, validation, submit/cancel actions
- [X] T052 [US3] Create frontend/src/app/(dashboard)/tasks/create/page.tsx with TaskForm component in create mode
- [X] T053 [US3] Implement title validation in TaskForm (required, 1-255 chars, no whitespace-only)
- [X] T054 [US3] Implement validation error display next to title input in TaskForm
- [X] T055 [US3] Implement task creation via API in TaskForm component
- [X] T056 [US3] Redirect to /tasks after successful task creation in TaskForm
- [X] T057 [US3] Display error message for task creation failures in TaskForm
- [X] T058 [US3] Disable submit button during submission in TaskForm (show loading state)
- [X] T059 [US3] Implement cancel action in TaskForm (navigate back to /tasks)

**Checkpoint**: User Story 3 complete - task creation works

---

## Phase 6: User Story 4 - Edit and Delete Tasks (Priority: P2)

**Goal**: Authenticated users can modify existing tasks and remove tasks

**Independent Test**: Edit a task and see changes, delete a task and see it removed from list

### Implementation for User Story 4

- [X] T060 [US4] Modify frontend/src/components/tasks/TaskForm.tsx to support edit mode (initialData prop)
- [X] T061 [US4] Create frontend/src/app/(dashboard)/tasks/[taskId]/page.tsx with TaskForm in edit mode
- [X] T062 [US4] Fetch task details on mount in task detail page via useTasks hook
- [X] T063 [US4] Implement task update via API in TaskForm component (PUT or PATCH)
- [X] T064 [US4] Validate title cannot be cleared (empty string) in TaskForm edit mode
- [X] T065 [US4] Display validation error when attempting to clear title in TaskForm
- [X] T066 [US4] Add delete confirmation modal in task detail page
- [X] T067 [US4] Implement task deletion via API in task detail page with confirmation
- [X] T068 [US4] Implement cancel delete action (close modal without deleting)
- [X] T069 [US4] Display error message for task update failures
- [X] T070 [US4] Display error message for task deletion failures
- [X] T071 [US4] Show loading state during task update/delete operations
- [X] T072 [US4] Update TaskCard to link to task detail page on click
- [X] T073 [US4] Add delete button to TaskCard component with confirmation modal

**Checkpoint**: User Story 4 complete - edit and delete tasks work

---

## Phase 7: User Story 5 - Responsive Design (Priority: P2)

**Goal**: Application adapts gracefully to desktop, tablet, and mobile viewports

**Independent Test**: View on mobile (320px+), tablet (640px+), desktop (1024px+), all features usable

### Implementation for User Story 5

- [X] T074 [P] Apply responsive Tailwind classes to Button component (mobile touch targets, desktop sizing)
- [X] T075 [P] Apply responsive Tailwind classes to Input component (mobile full-width, desktop constrained)
- [X] T076 [P] Apply responsive Tailwind classes to TextArea component (mobile full-width, desktop constrained)
- [X] T077 [P] Apply responsive Tailwind classes to TaskCard component (stacked on mobile, grid on desktop)
- [X] T078 [P] Apply responsive Tailwind classes to TaskList component (single column on mobile, wider on desktop)
- [X] T079 [US5] Apply responsive Tailwind classes to TaskForm component (mobile full-width, desktop constrained)
- [X] T080 [US5] Apply responsive Tailwind classes to navigation bar (simplified on mobile, full on desktop)
- [X] T081 [US5] Apply responsive Tailwind classes to SignInForm and SignUpForm (mobile full-width, desktop centered)
- [X] T082 [US5] Apply responsive Tailwind classes to auth layout (mobile simplified, desktop spacious)
- [X] T083 [US5] Test on mobile viewport (320px-640px) - ensure no horizontal scrolling
- [X] T084 [US5] Test on tablet viewport (640px-1024px) - ensure touch targets are accessible
- [X] T085 [US5] Test on desktop viewport (1024px+) - ensure layout is spacious

**Checkpoint**: User Story 5 complete - responsive design works

---

## Phase 8: User Story 6 - Loading and Error States (Priority: P2)

**Goal**: Users see appropriate feedback during loading, errors, and empty states

**Independent Test**: Intentionally trigger slow loads, network errors, and validation to see feedback

### Implementation for User Story 6

- [X] T086 [P] Create LoadingState component with spinner or skeleton UI in frontend/src/components/ui/
- [X] T087 [P] Create ErrorState component with message and retry button in frontend/src/components/ui/
- [X] T088 [US6] Implement loading state in TaskList during data fetch
- [X] T089 [US6] Implement loading state in useTasks hook during API calls
- [X] T090 [US6] Implement loading state in TaskForm during submit
- [X] T091 [US6] Implement loading state in SignInForm and SignUpForm during submit
- [X] T092 [US6] Implement error state in TaskList with user-friendly message
- [X] T093 [US6] Implement error state in TaskForm with retry button
- [X] T094 [US6] Implement error state in SignInForm and SignUpForm with retry option
- [X] T095 [US6] Implement empty state in TaskList (already have TaskEmptyState)
- [X] T096 [US6] Display validation errors next to fields in TaskForm (title, description)
- [X] T097 [US6] Display validation errors next to fields in SignInForm (email, password)
- [X] T098 [US6] Display validation errors next to fields in SignUpForm (email, password, confirmPassword)
- [X] T099 [US6] Handle 401 errors (unauthorized) by redirecting to /signin in API client interceptor
- [X] T100 [US6] Handle 403 errors (forbidden) by showing user-friendly message
- [X] T101 [US6] Handle 404 errors (not found) by showing user-friendly message
- [X] T102 [US6] Handle network errors with connection failure message and retry button
- [X] T103 [US6] Display generic error message for unexpected API failures with retry button

**Checkpoint**: User Story 6 complete - loading and error states work

---

## Phase 9: Polish

**Purpose**: Landing page, shared UI components, final integration

- [X] T104 [P] Create frontend/src/app/layout.tsx root layout with HTML5 boilerplate, meta tags, and global CSS
- [X] T105 [P] Create frontend/src/app/page.tsx landing page with branding, sign in/sign up CTAs
- [X] T106 [P] Enhance frontend/src/components/ui/Modal.tsx with close on ESC and backdrop click
- [X] T107 [P] Enhance frontend/src/components/ui/Button.tsx with loading state support
- [X] T108 Test end-to-end auth flow (landing page → sign up → tasks → sign out)
- [X] T109 Test end-to-end task CRUD flow (create, view, edit, delete, complete)
- [X] T110 Test responsive behavior on mobile viewport (320px+)
- [X] T111 Test responsive behavior on tablet viewport (640px+)
- [X] T112 Test responsive behavior on desktop viewport (1024px+)
- [X] T113 Test loading states on all pages
- [X] T114 Test error states for API failures
- [X] T115 Test empty states for no tasks scenario
- [X] T116 Verify all protected routes redirect to /signin when unauthenticated
- [X] T117 Verify user cannot access other user's tasks (backend enforces)
- [X] T118 Test form validation (empty title, invalid email, weak password)
- [X] T119 Test pagination with many tasks (create 30+ tasks and verify page controls)
- [X] T120 Verify JWT token is included in all API requests (check network tab)

**Checkpoint**: All user stories complete and polished

---

## Test Results Summary

**Test Coverage**:
- Unit tests for validation functions (testEmail, validatePassword, validateTaskTitle)
- Unit tests for storage utilities (getToken, setToken, removeToken, getUserFromToken)
- Integration tests for auth flow (sign up, sign in, sign out)
- Integration tests for task CRUD (create, read, update, delete, complete)
- Responsive tests (mobile, tablet, desktop viewports)
- E2E tests for critical user journeys

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Blocks | Blocked By |
|-------|--------|------------|
| Phase 1 (Setup) | 2, 3, 4, 5, 6, 7, 8, 9 | - |
| Phase 2 (Foundational) | 3, 4, 5, 6, 7, 8, 9 | Phase 1 |
| Phase 3 (US1 - Auth) | 4, 5, 6, 7, 8, 9 | Phase 2 |
| Phase 4 (US2 - Task Dashboard) | 5, 6, 7, 8, 9 | Phase 2, Phase 3 |
| Phase 5 (US3 - Create Tasks) | 4, 6, 7, 8, 9 | Phase 2, Phase 3, Phase 4 |
| Phase 6 (US4 - Edit/Delete) | 5, 7, 8, 9 | Phase 2, Phase 3, Phase 4, Phase 5 |
| Phase 7 (US5 - Responsive) | 8, 9 | Phase 2-6 (depends on components) |
| Phase 8 (US6 - Loading/Errors) | 9 | Phase 2-7 (integrates with components) |
| Phase 9 (Polish) | - | Phase 2-8 |

### User Story Dependencies

- **US1 (Authentication)**: Independent - foundational for other stories
- **US2 (Task Dashboard)**: Requires US1 (auth must work)
- **US3 (Create Tasks)**: Requires US1 (auth) and US2 (task list to see created task)
- **US4 (Edit/Delete)**: Requires US1 (auth) and US2 (task list to see changes)
- **US5 (Responsive Design)**: Requires US2, US3, US4 (applies to all task components)
- **US6 (Loading/Errors)**: Cross-cutting - can be implemented incrementally with each story

### Parallel Execution

Tasks marked `[P]` can run in parallel within each phase:

**Phase 1**: T002 (initializes rest), T003-T009 (independent configs and directories)
**Phase 2**: T011-T020 (independent types, utils, API files)
**Phase 3**: T023, T024, T025, T026 (independent UI components)
**Phase 4**: T035, T036, T037 (independent UI components)
**Phase 5**: T049, T050, T051 (independent UI components)
**Phase 7**: T074-T082 (independent responsive updates to components)
**Phase 8**: T086-T087 (independent state components)
**Phase 9**: T104-T107 (independent component enhancements)

---

## Implementation Complete

All 120 tasks complete when:
- Next.js 16+ application runs on http://localhost:3000
- Sign up/sign in/sign out flow works with JWT tokens
- All task CRUD operations work and reflect immediately
- Protected routes redirect unauthenticated users
- Application is responsive on mobile (320px+), tablet, desktop
- Loading states display during all API calls
- Error states display with user-friendly messages and retry options
- Empty states display helpful context
- All form validation works (empty fields, invalid formats, weak passwords)
