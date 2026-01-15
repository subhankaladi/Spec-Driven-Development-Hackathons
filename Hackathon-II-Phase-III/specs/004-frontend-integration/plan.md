# Implementation Plan: Frontend Web Application & Integration

**Branch**: `004-frontend-integration` | **Date**: 2025-12-27 | **Spec**: [specs/004-frontend-integration/spec.md](spec.md)
**Input**: Feature specification from `/specs/004-frontend-integration/spec.md`

## Summary

Implement a complete frontend web application for the Todo app using Next.js 16+ App Router with Better Auth for authentication. The implementation includes sign-up/sign-in flows, JWT-based session management, a secure API client, and a responsive task management UI. All API requests will be authenticated with JWT tokens.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Next.js 16.1.1, React 19.2.3, Better Auth, React Hook Form, Tailwind CSS 4
**Storage**: localStorage for JWT tokens, backend API for data persistence
**Testing**: Jest with React Testing Library
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend)
**Performance Goals**: Dashboard load < 5s, visual feedback < 300ms
**Constraints**: Stateless authentication, mobile-first responsive design
**Scale/Scope**: Single-user dashboard, ~100 tasks per user typical

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Development: Complete specification exists at specs/004-frontend-integration/spec.md
- ✅ Zero Manual Coding: Implementation will be achieved exclusively through Claude Code
- ✅ Security-First Design: JWT authentication on every API call, no unauthenticated requests
- ✅ Deterministic and Reproducible Outputs: Using established frontend structure
- ✅ Full-Stack Architecture Standards: Using Next.js 16+ App Router with Better Auth as required
- ✅ End-to-End Agentic Workflow: Following spec → plan → tasks → implementation workflow

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── frontend-routes.md
│   └── api-client-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Home/landing page
│   ├── not-found.tsx           # 404 page
│   ├── error.tsx               # Error boundary
│   ├── auth/
│   │   ├── signin/
│   │   │   └── page.tsx        # Sign-in page
│   │   └── signup/
│   │       └── page.tsx        # Sign-up page
│   └── dashboard/
│       ├── layout.tsx          # Dashboard layout (protected)
│       └── page.tsx            # Task dashboard
├── components/
│   ├── ui/
│   │   ├── Button.tsx          # Reusable button
│   │   ├── Input.tsx           # Form input
│   │   ├── Modal.tsx           # Modal dialog
│   │   ├── Spinner.tsx         # Loading spinner
│   │   └── Toast.tsx           # Notification toast
│   ├── auth/
│   │   ├── SignInForm.tsx      # Sign-in form
│   │   ├── SignUpForm.tsx      # Sign-up form
│   │   └── AuthGuard.tsx       # Route protection
│   └── tasks/
│       ├── TaskList.tsx        # Task list container
│       ├── TaskCard.tsx        # Individual task card
│       ├── TaskForm.tsx        # Create/edit task form
│       ├── TaskFilter.tsx      # Filter controls
│       ├── EmptyState.tsx      # No tasks message
│       └── DeleteConfirm.tsx   # Delete confirmation modal
├── lib/
│   ├── auth.ts                 # Better Auth client setup
│   ├── api-client.ts           # Authenticated API client
│   └── utils.ts                # Utility functions
├── hooks/
│   ├── useAuth.ts              # Auth state hook
│   ├── useTasks.ts             # Tasks data hook
│   └── useToast.ts             # Toast notification hook
├── types/
│   └── index.ts                # TypeScript types
├── middleware.ts               # Route protection middleware
└── tailwind.config.ts          # Tailwind configuration
```

**Structure Decision**: Single frontend project using Next.js App Router pattern. Components organized by feature (auth, tasks) with shared UI components. Hooks for state management. Middleware for route protection.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Plan

### Phase 1: Setup & Configuration

#### 1.1 Install Dependencies
- **Action**: Install Better Auth, React Hook Form
- **Files**: `frontend/package.json`

#### 1.2 Configure Environment
- **Action**: Create `.env.local` with API URL and auth secrets
- **Files**: `frontend/.env.local`, `frontend/.env.example`

#### 1.3 Configure Better Auth
- **Action**: Set up Better Auth client with JWT support
- **Files**: `frontend/lib/auth.ts`

#### 1.4 Configure API Client
- **Action**: Create authenticated fetch wrapper
- **Files**: `frontend/lib/api-client.ts`

### Phase 2: Authentication (User Story 1)

#### 2.1 Auth Types
- **Action**: Define TypeScript types for auth
- **Files**: `frontend/types/index.ts`

#### 2.2 Auth Hook
- **Action**: Create useAuth hook for auth state
- **Files**: `frontend/hooks/useAuth.ts`

#### 2.3 Sign-In Page
- **Action**: Create sign-in form and page
- **Files**: `frontend/app/auth/signin/page.tsx`, `frontend/components/auth/SignInForm.tsx`

#### 2.4 Sign-Up Page
- **Action**: Create sign-up form and page
- **Files**: `frontend/app/auth/signup/page.tsx`, `frontend/components/auth/SignUpForm.tsx`

#### 2.5 Route Protection
- **Action**: Create middleware and AuthGuard component
- **Files**: `frontend/middleware.ts`, `frontend/components/auth/AuthGuard.tsx`

#### 2.6 Layout with Auth Provider
- **Action**: Wrap app with auth provider
- **Files**: `frontend/app/layout.tsx`

### Phase 3: Task Dashboard (User Stories 2-4)

#### 3.1 Task Types
- **Action**: Define TypeScript types for tasks
- **Files**: `frontend/types/index.ts`

#### 3.2 Tasks Hook
- **Action**: Create useTasks hook for task operations
- **Files**: `frontend/hooks/useTasks.ts`

#### 3.3 UI Components
- **Action**: Create reusable UI components
- **Files**: `frontend/components/ui/*.tsx`

#### 3.4 Task List Component
- **Action**: Create task list with loading/error/empty states
- **Files**: `frontend/components/tasks/TaskList.tsx`

#### 3.5 Task Card Component
- **Action**: Create task card with edit/delete/complete actions
- **Files**: `frontend/components/tasks/TaskCard.tsx`

#### 3.6 Task Form Component
- **Action**: Create task form for create/edit
- **Files**: `frontend/components/tasks/TaskForm.tsx`

#### 3.7 Dashboard Page
- **Action**: Create dashboard page with task management
- **Files**: `frontend/app/dashboard/page.tsx`, `frontend/app/dashboard/layout.tsx`

### Phase 4: Delete Tasks (User Story 5)

#### 4.1 Delete Confirmation Modal
- **Action**: Create confirmation dialog
- **Files**: `frontend/components/tasks/DeleteConfirm.tsx`

#### 4.2 Integrate Delete Flow
- **Action**: Add delete functionality to TaskCard
- **Files**: `frontend/components/tasks/TaskCard.tsx`

### Phase 5: Error Handling (User Story 6)

#### 5.1 Toast Notifications
- **Action**: Create toast component and hook
- **Files**: `frontend/components/ui/Toast.tsx`, `frontend/hooks/useToast.ts`

#### 5.2 Error Boundary
- **Action**: Create app-level error boundary
- **Files**: `frontend/app/error.tsx`

#### 5.3 API Error Handling
- **Action**: Enhance API client with error mapping
- **Files**: `frontend/lib/api-client.ts`

### Phase 6: Polish & Validation

#### 6.1 Responsive Design
- **Action**: Ensure all components are mobile-friendly
- **Files**: All component files

#### 6.2 Loading States
- **Action**: Add loading indicators to all async operations
- **Files**: All component files

#### 6.3 Home Page
- **Action**: Create landing page for unauthenticated users
- **Files**: `frontend/app/page.tsx`

#### 6.4 404 Page
- **Action**: Create not-found page
- **Files**: `frontend/app/not-found.tsx`

## Dependencies

| Artifact | Status | Path |
|----------|--------|------|
| Feature Spec | ✅ Complete | `specs/004-frontend-integration/spec.md` |
| Research | ✅ Complete | `specs/004-frontend-integration/research.md` |
| Data Model | ✅ Complete | `specs/004-frontend-integration/data-model.md` |
| Route Contract | ✅ Complete | `specs/004-frontend-integration/contracts/frontend-routes.md` |
| API Client Contract | ✅ Complete | `specs/004-frontend-integration/contracts/api-client-contract.md` |
| Quickstart | ✅ Complete | `specs/004-frontend-integration/quickstart.md` |
| Tasks | ⏳ Pending | `specs/004-frontend-integration/tasks.md` |

## Next Steps

1. Run `/sp.tasks` to generate task breakdown
2. Run `/sp.implement` to execute implementation
3. Validate against acceptance criteria in quickstart.md
