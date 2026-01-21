# Frontend Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Backend API running at `http://localhost:8000`
- Git initialized

## Installation

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies** (already done)
```bash
npm install
```

3. **Configure environment**
The `.env.local` file is already created with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode
```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

### Production Build
```bash
npm run build
npm start
```

## Testing

### Run all tests
```bash
npm test
```

### Watch mode
```bash
npm run test:watch
```

### E2E tests (if Playwright installed)
```bash
npm run test:e2e
```

## User Flow

### 1. Landing Page (/)
- View features and benefits
- Click "Sign Up" or "Sign In"

### 2. Sign Up (/signup)
- Enter email and password (min 8 chars)
- Confirm password
- Submit to create account
- Automatically redirected to tasks page

### 3. Sign In (/signin)
- Enter existing credentials
- Submit to authenticate
- Automatically redirected to tasks page

### 4. Tasks Dashboard (/tasks)
- View all your tasks
- Toggle task completion with checkbox
- Click "Edit" to modify a task
- Click "Delete" to remove a task
- Use pagination if you have >20 tasks
- Click "Create Task" button

### 5. Create Task (/tasks/create)
- Enter task title (required, 1-255 chars)
- Optionally add description
- Click "Create Task" or "Cancel"

### 6. Edit Task (/tasks/{id})
- Modify title or description
- Click "Save Changes" or "Cancel"
- Click "Delete Task" with confirmation

## API Integration

The frontend connects to these backend endpoints:

### Auth Endpoints
- `POST /auth/signup` - Create account
- `POST /auth/signin` - Get JWT token

### Task Endpoints (require JWT)
- `GET /users/{user_id}/tasks?page=1&page_size=20`
- `POST /users/{user_id}/tasks`
- `GET /users/{user_id}/tasks/{task_id}`
- `PATCH /users/{user_id}/tasks/{task_id}`
- `DELETE /users/{user_id}/tasks/{task_id}`

## Features

✅ **Authentication**
- JWT-based auth with localStorage
- Protected routes (redirect to /signin)
- Auto-logout on 401 errors

✅ **Task Management**
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Pagination (20 tasks per page)
- Optimistic UI updates

✅ **UI/UX**
- Responsive design (320px - 1920px+)
- Loading states (spinners)
- Error states (user-friendly messages)
- Empty states (helpful prompts)
- Form validation (real-time feedback)

## Architecture

```
Component Hierarchy:
├── App Layout (AuthContext Provider)
    ├── Landing Page (/)
    ├── Auth Layout
    │   ├── Sign In Page (/signin)
    │   └── Sign Up Page (/signup)
    └── Dashboard Layout (protected)
        └── Tasks
            ├── Task List (/tasks)
            ├── Create Task (/tasks/create)
            └── Edit Task (/tasks/{id})
```

## Troubleshooting

### CORS Errors
- Ensure backend is running at `http://localhost:8000`
- Check backend CORS settings allow `http://localhost:3000`

### 401 Unauthorized
- Sign out and sign in again
- Check JWT token in browser localStorage
- Verify backend is accepting the token

### Tasks Not Loading
- Check backend API is running
- Check network tab for API errors
- Verify user ID in URL matches JWT token

### Build Errors
- Delete `.next/` folder and rebuild
- Run `npm install` to ensure dependencies
- Check TypeScript errors with `npm run lint`

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
├── components/            # Reusable components
│   ├── auth/             # Auth forms
│   ├── tasks/            # Task components
│   └── ui/               # Shared UI components
├── context/              # React Context providers
├── lib/                  # Business logic
│   ├── api/             # API client
│   ├── hooks/           # Custom hooks
│   └── utils/           # Utilities
└── types/                # TypeScript types
```

## Support

For issues or questions:
1. Check IMPLEMENTATION.md for detailed documentation
2. Review plan.md and spec.md in `/specs/003-frontend/`
3. Check backend logs for API errors
4. Verify environment variables in .env.local

## Development Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **Type Safety**: TypeScript will catch errors at compile time
3. **Console Logs**: Check browser console for errors
4. **Network Tab**: Monitor API calls in browser DevTools
5. **React DevTools**: Install extension for component debugging

## Next Steps

After successful setup:
1. Sign up with a test account
2. Create a few tasks
3. Test editing and deleting
4. Test pagination (create 20+ tasks)
5. Test responsive design (resize browser)
6. Test error handling (disconnect backend)

Enjoy managing your tasks!
