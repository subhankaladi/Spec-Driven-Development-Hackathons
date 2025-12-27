# Research: Frontend Web Application & Integration

## Decision: Next.js App Router Structure
**Rationale**: Use Next.js 16+ App Router with server and client components. The App Router provides built-in support for layouts, loading states, and error boundaries which align with the spec requirements. Existing project already uses Next.js 16.1.1.
**Alternatives considered**: Pages Router - rejected as App Router is the modern standard and better suited for the spec requirements (loading states, error handling).

## Decision: Authentication Library
**Rationale**: Use Better Auth for signup/signin flows as specified in the constitution. Better Auth provides JWT-based stateless authentication that integrates well with Next.js and the existing backend JWT system.
**Alternatives considered**: NextAuth.js, Auth0 - rejected as constitution mandates Better Auth for consistency with the full-stack architecture.

## Decision: JWT Token Storage
**Rationale**: Store JWT tokens in localStorage with automatic attachment to API requests via a centralized API client. The existing auth.js utilities already implement this pattern. Will migrate to TypeScript and integrate with Better Auth.
**Alternatives considered**: HttpOnly cookies - rejected as the frontend needs access to the token for auth state checks; sessionStorage - rejected for persistence across tabs.

## Decision: State Management for Auth
**Rationale**: Use React Context for auth state management with Better Auth's built-in session hooks. This provides app-wide access to auth state without prop drilling.
**Alternatives considered**: Redux, Zustand - rejected as overkill for auth-only state management; Better Auth provides sufficient built-in state.

## Decision: API Client Pattern
**Rationale**: Create a centralized API client that wraps fetch with automatic JWT header injection, error handling, and response parsing. This ensures 100% of API calls include authentication.
**Alternatives considered**: Direct fetch calls - rejected as it's error-prone for auth headers; axios - acceptable but fetch is sufficient and reduces dependencies.

## Decision: UI Component Approach
**Rationale**: Use Tailwind CSS (already installed) for styling with responsive breakpoints. Create reusable components for task cards, forms, and loading states.
**Alternatives considered**: Component libraries (Chakra, MUI) - rejected to keep bundle size minimal; CSS modules - acceptable but Tailwind is already configured.

## Decision: Form Handling
**Rationale**: Use React Hook Form for form state management and validation. Provides good TypeScript support and minimal re-renders.
**Alternatives considered**: Formik - acceptable but heavier; native forms - acceptable for simple forms but React Hook Form provides better UX.

## Decision: Responsive Design Breakpoints
**Rationale**: Use Tailwind's default breakpoints with mobile-first approach. Primary breakpoint at 768px (md:) as specified in requirements for desktop vs mobile layouts.
**Alternatives considered**: Custom breakpoints - rejected as Tailwind defaults align with spec requirements.

## Decision: Error Handling Strategy
**Rationale**: Implement error boundaries for component-level errors, toast notifications for operation errors, and dedicated error states in UI components. Provide retry options where applicable.
**Alternatives considered**: Global error modal - rejected as too intrusive; console-only logging - rejected as doesn't meet user-facing error message requirements.

## Decision: Route Protection
**Rationale**: Implement middleware-based route protection that redirects unauthenticated users to sign-in. Use Next.js middleware for server-side checks and client-side hooks for runtime checks.
**Alternatives considered**: Client-only checks - rejected as causes flash of protected content; HOC pattern - acceptable but middleware is cleaner with App Router.
