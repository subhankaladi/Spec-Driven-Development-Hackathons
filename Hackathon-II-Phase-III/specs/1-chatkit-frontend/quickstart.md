# Quickstart: ChatKit Frontend & Secure Deployment

**Feature**: 1-chatkit-frontend
**Date**: 2026-01-10

## Prerequisites

- Node.js >= 18.0
- Backend API running (FastAPI)
- Valid JWT for a test user
- OpenAI ChatKit domain allowlist configured

## Environment Variables

```bash
VITE_BACKEND_URL=http://localhost:8000
VITE_CHATKIT_DOMAIN=your-domain.chatkit.com
```

## Install Dependencies

```bash
cd frontend
npm install
```

## Run Frontend

```bash
npm run dev
```

## Test Chat Interface

1. Access the chat interface in browser
2. Authenticate with JWT (automatically attached to requests)
3. Send a message: "Add task: Buy milk"
4. Verify response confirms task was added

Expected response:
```
Added 'Buy milk' to your task list.
```

## Domain Allowlist Validation

1. Ensure your domain is allowlisted in OpenAI ChatKit
2. Configure VITE_CHATKIT_DOMAIN environment variable
3. Test that the chat interface loads properly
4. Attempt access from non-allowlisted domain (should fail)

## Security Validation

- Try accessing without JWT → expect authentication error
- Try with JWT for user A but manipulate to access user B's data → expect 403

## Validation Results

- ✅ Frontend successfully connects to backend API
- ✅ JWT authentication works correctly with token attachment to requests
- ✅ Chat interface loads and processes messages
- ✅ Conversation history persists across page refreshes
- ✅ Domain allowlist validation functions properly
- ✅ Error handling and logging implemented correctly
- ✅ All required environment variables validated