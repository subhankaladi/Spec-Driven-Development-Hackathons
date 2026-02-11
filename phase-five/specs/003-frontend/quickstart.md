# Frontend & Integration Quickstart Guide

**Feature**: Frontend & Integration (003-frontend)
**Branch**: `003-frontend`
**Date**: 2026-01-07

## Prerequisites

Before starting, ensure you have:

- Node.js 18+ and npm installed
- Backend API running (Spec-1 + Spec-2 deployed)
- Environment variables configured for backend URL
- Git initialized and on the `003-frontend` branch

## Setup Instructions

### 1. Initialize Frontend Project

```bash
# From project root
cd frontend
npm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

Accept all defaults when prompted.

### 2. Install Dependencies

```bash
# Install core dependencies
npm install axios

# Install development dependencies
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom

# (Optional) E2E testing
npm install -D @playwright/test
```

### 3. Configure Environment Variables

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# (Optional) Development mode
NEXT_PUBLIC_DEBUG=true
```

### 4. Update Package.json Scripts

Update `frontend/package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test"
  }
}
```

### 5. Configure Jest

Create `frontend/jest.config.js`:

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
}

module.exports = createJestConfig(customJestConfig)
```

Create `frontend/jest.setup.js`:

```javascript
import '@testing-library/jest-dom'
```

### 6. Create Directory Structure

```bash
cd frontend/src

# Create directories
mkdir -p components/auth components/tasks components/ui
mkdir -p lib/api lib/hooks lib/utils
mkdir -p context types
mkdir -p tests/unit tests/integration tests/e2e

# Create files
touch context/AuthContext.tsx
touch lib/api/client.ts lib/api/auth.ts lib/api/tasks.ts
touch lib/hooks/useAuth.ts lib/hooks/useTasks.ts
touch lib/utils/validation.ts lib/utils/storage.ts
touch types/auth.ts types/tasks.ts types/api.ts types/ui.ts
```

### 7. Configure Tailwind CSS

The `create-next-app` command already sets up Tailwind. Customize `frontend/tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        danger: {
          500: '#ef4444',
          600: '#dc2626',
        },
        success: {
          500: '#10b981',
        },
      },
    },
  },
  plugins: [],
}
export default config
```

## Development Workflow

### Start Development Server

```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

### Run Tests

```bash
# Unit tests
npm test

# Watch mode
npm run test:watch

# E2E tests
npm run test:e2e
```

### Build for Production

```bash
npm run build
npm run start
```

## Implementation Order

Follow this order to implement features:

### Phase 1: Foundation (Day 1)

1. **Type definitions** (`src/types/`)
   - Create `auth.ts`, `tasks.ts`, `api.ts`, `ui.ts`

2. **Utilities** (`src/lib/utils/`)
   - Create `validation.ts`, `storage.ts`

3. **API Client** (`src/lib/api/`)
   - Create `client.ts` (Axios with interceptors)
   - Create `auth.ts` (auth API methods)
   - Create `tasks.ts` (tasks API methods)

### Phase 2: Authentication (Day 1-2)

4. **Auth Context** (`src/context/AuthContext.tsx`)
   - Implement global auth state
   - Provide signIn, signUp, signOut methods

5. **Auth Components** (`src/components/auth/`)
   - Create `SignInForm.tsx`
   - Create `SignUpForm.tsx`

6. **Auth Pages** (`src/app/(auth)/`)
   - Create `layout.tsx`
   - Create `sign-in/page.tsx`
   - Create `sign-up/page.tsx`

7. **Middleware** (`middleware.ts`)
   - Implement route protection

### Phase 3: Task Management (Day 2-3)

8. **Task Components** (`src/components/tasks/`)
   - Create `TaskList.tsx`
   - Create `TaskCard.tsx`
   - Create `TaskForm.tsx`
   - Create `TaskEmptyState.tsx`

9. **Task Hooks** (`src/lib/hooks/`)
   - Create `useTasks.ts`

10. **Task Pages** (`src/app/(dashboard)/`)
    - Create `layout.tsx`
    - Create `tasks/page.tsx`
    - Create `tasks/create/page.tsx`
    - Create `tasks/[taskId]/page.tsx`

### Phase 4: UI Components (Day 3-4)

11. **Shared UI Components** (`src/components/ui/`)
    - Create `Button.tsx`
    - Create `Input.tsx`
    - Create `TextArea.tsx`
    - Create `Checkbox.tsx`
    - Create `Modal.tsx`

12. **Landing Page** (`src/app/page.tsx`)
    - Create landing page with auth links

### Phase 5: Polish & Testing (Day 4-5)

13. **Responsive Design**
    - Test on mobile (320px-640px)
    - Test on tablet (641px-1024px)
    - Test on desktop (1025px+)

14. **Loading & Error States**
    - Implement loading spinners
    - Implement error messages
    - Implement empty states

15. **Testing**
    - Write unit tests for utilities
    - Write integration tests for auth flow
    - Write integration tests for task CRUD
    - Write E2E tests with Playwright

## Integration Checklist

- [ ] Backend API is running and accessible at `NEXT_PUBLIC_API_URL`
- [ ] Sign up flow works (create account, receive token)
- [ ] Sign in flow works (authenticate, redirect to dashboard)
- [ ] Sign out works (clear token, redirect to login)
- [ ] Protected routes redirect unauthenticated users
- [ ] Task list displays correctly
- [ ] Create task works and appears in list
- [ ] Update task works and reflects changes
- [ ] Delete task works and removes from list
- [ ] Toggle task completion works
- [ ] Pagination works for >20 tasks
- [ ] Loading states display during API calls
- [ ] Error messages display for API failures
- [ ] Empty state displays for no tasks
- [ ] Responsive design works on mobile
- [ ] Responsive design works on tablet
- [ ] Responsive design works on desktop
- [ ] All tests pass (unit + integration)
- [ ] E2E tests pass (critical user journeys)

## Common Issues

### CORS Errors

If you see CORS errors:

1. Check backend allows requests from `localhost:3000`
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Check browser console for specific CORS headers

### 401 Unauthorized Errors

If protected routes return 401:

1. Verify JWT token exists in localStorage
2. Check token is not expired
3. Verify `Authorization` header is sent with requests
4. Check API client interceptor is configured correctly

### Route Protection Not Working

If unauthenticated users can access protected routes:

1. Verify `middleware.ts` exists in frontend root
2. Check middleware is checking protected routes
3. Verify JWT token validation logic
4. Check `NEXT_PUBLIC_API_URL` is set

### Styling Issues

If Tailwind styles don't apply:

1. Verify `tailwind.config.ts` content paths are correct
2. Check `globals.css` includes Tailwind directives
3. Restart dev server after config changes
4. Check browser console for CSS errors

## Next Steps

After completing this quickstart:

1. Review [research.md](./research.md) for architecture decisions
2. Review [data-model.md](./data-model.md) for data structures
3. Review [contracts/](./contracts/) for API and component contracts
4. Run `/sp.tasks` to generate task breakdown
5. Run `/sp.implement` to execute implementation

## Support

For issues or questions:

1. Check the [constitution](../../.specify/memory/constitution.md) for project principles
2. Review [plan.md](./plan.md) for architecture decisions
3. Check backend API documentation in [Spec-1](../001-task-api-backend/) and [Spec-2](../002-auth-jwt/)

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-07
