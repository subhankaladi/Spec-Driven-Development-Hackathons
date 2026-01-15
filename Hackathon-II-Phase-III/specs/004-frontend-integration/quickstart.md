# Quickstart: Frontend Web Application & Integration

## Prerequisites

- Node.js 18+ installed
- Backend API running at `http://localhost:8000`
- Better Auth configured with shared JWT secret

## Setup

### 1. Install Dependencies
```bash
cd frontend
npm install better-auth react-hook-form
```

### 2. Configure Environment
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-shared-jwt-secret
BETTER_AUTH_URL=http://localhost:3000
```

### 3. Start Development Server
```bash
npm run dev
```

Application runs at `http://localhost:3000`

---

## Testing User Flows

### User Story 1: Registration and Sign In

**Sign Up:**
1. Navigate to `http://localhost:3000/auth/signup`
2. Enter email: `test@example.com`
3. Enter password: `TestPass123!`
4. Confirm password: `TestPass123!`
5. Click "Sign Up"
6. **Expected**: Redirected to dashboard

**Sign In:**
1. Navigate to `http://localhost:3000/auth/signin`
2. Enter email: `test@example.com`
3. Enter password: `TestPass123!`
4. Click "Sign In"
5. **Expected**: Redirected to dashboard with user's tasks

**Sign Out:**
1. Click "Sign Out" button in header
2. **Expected**: Redirected to home page, session cleared

**Invalid Credentials:**
1. Navigate to sign-in page
2. Enter wrong password
3. Click "Sign In"
4. **Expected**: Error message displayed, remain on page

**Protected Route Access:**
1. While signed out, navigate to `http://localhost:3000/dashboard`
2. **Expected**: Redirected to sign-in page

---

### User Story 2: Task Dashboard

**View Tasks:**
1. Sign in with valid credentials
2. **Expected**: Dashboard shows list of user's tasks
3. **Expected**: Each task shows title, description (if any), completion status

**Empty State:**
1. Sign in as new user with no tasks
2. **Expected**: Empty state message: "No tasks yet. Create your first task!"

**Mobile Responsiveness:**
1. Open browser dev tools
2. Toggle device toolbar (mobile view)
3. **Expected**: Layout adapts - single column, touch-friendly buttons

**Loading State:**
1. Open Network tab in dev tools
2. Throttle to "Slow 3G"
3. Refresh dashboard
4. **Expected**: Loading spinner while tasks fetch

---

### User Story 3: Create Task

**Create Valid Task:**
1. Click "Create Task" button
2. Enter title: "Buy groceries"
3. Enter description: "Milk, eggs, bread"
4. Click "Create"
5. **Expected**: Modal closes, task appears in list

**Validation Error:**
1. Click "Create Task" button
2. Leave title empty
3. Click "Create"
4. **Expected**: Error message: "Title is required"

**Loading During Creation:**
1. Throttle network to slow
2. Create a task
3. **Expected**: Button shows loading state, form disabled

---

### User Story 4: Update and Complete Tasks

**Edit Task:**
1. Click edit icon on existing task
2. Change title to "Updated task title"
3. Click "Save"
4. **Expected**: Task updates in list

**Toggle Completion:**
1. Click checkbox on incomplete task
2. **Expected**: Task shows completed (checkbox checked, visual indicator)
3. Click checkbox again
4. **Expected**: Task shows incomplete

**Optimistic Update:**
1. Throttle network
2. Toggle task completion
3. **Expected**: UI updates immediately, confirms when API responds

---

### User Story 5: Delete Tasks

**Delete with Confirmation:**
1. Click delete icon on task
2. **Expected**: Confirmation modal appears
3. Click "Cancel"
4. **Expected**: Task remains, modal closes
5. Click delete again, then "Confirm"
6. **Expected**: Task removed from list

---

### User Story 6: Error Handling

**Network Error:**
1. Disconnect network (offline mode)
2. Try to create task
3. **Expected**: Error message: "Network error. Check your connection."
4. Reconnect network
5. Click "Retry"
6. **Expected**: Operation succeeds

**Session Expiry:**
1. Manually clear localStorage token
2. Try to create/update task
3. **Expected**: Redirected to sign-in with "Session expired" message

---

## Acceptance Criteria Validation

| Criteria | Test | Status |
|----------|------|--------|
| SC-001: Sign-up < 60s | Time the complete sign-up flow | [ ] |
| SC-002: Sign-in to dashboard < 5s | Time from sign-in click to dashboard render | [ ] |
| SC-003: 95% first-attempt task creation | Create 20 tasks, count failures | [ ] |
| SC-004: Visual feedback < 300ms | Observe loading states appear | [ ] |
| SC-005: Responsive 320px-1920px | Test at min/max widths | [ ] |
| SC-006: Error display < 2s | Time from error to message display | [ ] |
| SC-007: 100% authenticated API calls | Check Network tab for Authorization headers | [ ] |
| SC-008: No cross-user data | Sign in as different users, verify task isolation | [ ] |

---

## Common Issues

### "Network error" on all requests
- Check backend is running at configured URL
- Verify CORS is enabled on backend
- Check browser console for detailed error

### "Session expired" immediately after sign-in
- Verify JWT secret matches between frontend and backend
- Check token expiry time in backend settings

### Tasks not updating in UI
- Check React state updates in dev tools
- Verify API response format matches expected

### Styles not loading
- Run `npm run dev` (not `npm start`)
- Clear browser cache
- Check Tailwind configuration
