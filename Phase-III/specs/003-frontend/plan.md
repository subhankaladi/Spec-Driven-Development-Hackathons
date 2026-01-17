# Implementation Plan: Frontend & Integration

**Branch**: `003-frontend` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend/spec.md`

## Summary

This plan implements a responsive web application for task management with secure authentication. The frontend integrates with the existing Task API (Spec-1) and Authentication API (Spec-2) to provide a complete user-facing application. Key features include authentication flow, task CRUD operations, responsive design, and comprehensive loading/error states.

## Technical Context

**Language/Version**: TypeScript 5.3+ (via Next.js 16+)
**Primary Dependencies**: Next.js 16+ (App Router), React 18+, Tailwind CSS, Axios (for HTTP)
**Storage**: JWT tokens in browser storage (localStorage/cookies - to be determined in research)
**Testing**: Jest + React Testing Library, Playwright (E2E)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
**Project Type**: Web application (Next.js)
**Performance Goals**: Page load <2s, API response <500ms, Task toggle <500ms
**Constraints**: Stateless frontend, JWT auth only, no direct DB access, responsive (320px+)
**Scale/Scope**: Single-user tasks, 20 tasks/page, unlimited tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | All features traceable to spec.md with user stories and requirements |
| II. Agentic Workflow | ✅ PASS | Will use Frontend Agent for all code generation |
| III. Security-First Design | ✅ PASS | JWT auth, token validation, protected routes, user isolation |
| IV. Deterministic Behavior | ✅ PASS | API contracts match backend spec, explicit error handling |
| V. Full-Stack Coherence | ✅ PASS | Integrates with existing backend (Spec-1/Spec-2), follows API contracts |
| VI. Traceability | ✅ PASS | Will create PHR for all agent invocations, documented in history/ |

### Technology Stack Compliance

| Required Technology | Selected | Notes |
|---------------------|----------|-------|
| Next.js 16+ (App Router) | Next.js 16+ | ✅ Matches constitution |
| Frontend Agent Usage | Planned | ✅ Will use for all code generation |
| Better Auth (JWT) | JWT integration | ✅ Backend provides JWT, frontend consumes |

### Security Requirements Compliance

- ✅ JWT token validation on every request (to be implemented in API client)
- ✅ Task ownership enforced by backend API (frontend respects URL structure)
- ✅ No hard-coded secrets (will use environment variables for API URL)
- ✅ Protected routes with authentication checks (middleware/client-side)

**Gate Result**: ✅ PASS - No violations detected. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend/
├── spec.md              # Feature specification (created)
├── plan.md              # This file (created)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── frontend-api.yaml # API client contract
│   └── ui-components.yaml  # UI component structure
└── checklists/
    └── requirements.md  # Specification validation (created)
```

### Source Code (repository root)

```text
frontend/               # NEW - Next.js application
├── src/
│   ├── app/            # App Router pages
│   │   ├── (auth)/     # Auth routes group
│   │   │   ├── signin/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/ # Protected routes group
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── create/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── [taskId]/
│   │   │   │       └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── layout.tsx  # Root layout
│   │   └── page.tsx    # Landing page
│   ├── components/     # Reusable UI components
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx
│   │   │   └── SignUpForm.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskEmptyState.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── TextArea.tsx
│   │       ├── Checkbox.tsx
│   │       └── Modal.tsx
│   ├── lib/
│   │   ├── api/        # API client layer
│   │   │   ├── client.ts # Axios wrapper with auth
│   │   │   ├── auth.ts  # Auth API methods
│   │   │   └── tasks.ts # Tasks API methods
│   │   ├── hooks/      # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   └── useTasks.ts
│   │   └── utils/      # Utility functions
│   │       ├── validation.ts
│   │       └── storage.ts
│   ├── types/          # TypeScript types
│   │   ├── auth.ts
│   │   ├── tasks.ts
│   │   └── api.ts
│   └── context/        # React context providers
│       └── AuthContext.tsx
├── public/             # Static assets
├── tests/              # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .env.local          # Environment variables

backend/                # EXISTS - Spec-1 & Spec-2
└── (unchanged)

phase-II/               # Documentation & configs
└── .specify/           # Development templates
```

**Structure Decision**: Selected Option 2 (Web application with separate frontend and backend). The frontend is a new Next.js 16+ application with App Router, integrating with the existing backend from Spec-1/Spec-2. The App Router allows for route groups (`(auth)`, `(dashboard)`) to organize pages logically.

## Complexity Tracking

> No violations requiring justification. All design decisions follow constitution requirements.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

**Phase 0**: See [research.md](./research.md) for architecture decisions and technical research
**Phase 1**: See [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md) for design artifacts

---

## Post-Design Constitution Check

*GATE: Must pass after Phase 1 design before proceeding to task breakdown.*

### Design Compliance Verification

| Principle | Status | Evidence from Design |
|-----------|--------|----------------------|
| I. Spec-Driven Development | ✅ PASS | All components map to user stories (US1-US6), all data models align with spec requirements |
| II. Agentic Workflow | ✅ PASS | Quickstart.md documents use of Frontend Agent for code generation |
| III. Security-First Design | ✅ PASS | JWT validation (research.md AD-002), protected routes (research.md AD-003), user isolation (data-model.md) |
| IV. Deterministic Behavior | ✅ PASS | API contracts (contracts/frontend-api.yaml) match backend spec, explicit error handling defined |
| V. Full-Stack Coherence | ✅ PASS | API client matches backend endpoints, data models align with backend contracts |
| VI. Traceability | ✅ PASS | Component hierarchy documented, clear mapping from spec → design → implementation |

### Architecture Decisions Compliance

| Requirement | Design Decision | Constitution Alignment |
|-------------|-----------------|------------------------|
| No direct DB access | API client layer (Axios) with JWT headers | ✅ All data via backend API |
| Stateless frontend | localStorage for JWT, Context for state | ✅ No server-side session |
| JWT auth only | Axios interceptor adds `Authorization: Bearer {token}` | ✅ No other auth methods |
| User isolation | Backend enforces via user_id in URL | ✅ Frontend respects URL structure |
| Responsive design | Tailwind breakpoints (320px+, 640px+, 1024px+) | ✅ Mobile-first approach |
| Loading/error states | Conditional rendering patterns | ✅ Explicit feedback mechanisms |

### Complexity Assessment

**Overall Complexity**: LOW-MEDIUM

**Rationale**:
- Standard Next.js App Router patterns (well-documented)
- No state management libraries (Context + hooks only)
- No advanced routing features (basic route groups)
- No complex integrations (REST API, JWT only)
- Clear separation of concerns (components, hooks, API)

**Constitution Principle**: "Smallest viable change, no unnecessary abstractions" - ✅ ALIGNED

### Gate Result

✅ **PASS** - All constitution requirements met. No violations. Design is approved and ready for task breakdown.

**Next Steps**:
1. Run `/sp.tasks` to generate implementation task list
2. Review task breakdown for completeness
3. Execute implementation with Frontend Agent
