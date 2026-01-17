# ChatKit Frontend - Developer Quickstart

**Feature**: ChatKit Frontend & Secure Deployment (007-chatkit-frontend)
**Updated**: 2026-01-17

This guide helps developers set up and run the ChatKit frontend locally for development.

---

## Prerequisites

- **Node.js**: 18+ (with npm or yarn)
- **TypeScript**: 5.0+
- **Git**: Clone the repository
- **Backend Running**: AI Agent Chat API (006-ai-agent-chat-api) must be running on `http://localhost:8000`
- **Database**: PostgreSQL with chat API tables created (run `alembic upgrade head` in backend)

---

## Quick Setup

### 1. Clone & Install

```bash
cd /mnt/c/Users/a/Desktop/phase-3/frontend

# Install dependencies
npm install
# or
yarn install
```

### 2. Configure Environment

Create `.env.local` for development:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development

# No domain key needed for local development
# (domain allowlist validation disabled in dev mode)
```

### 3. Verify Backend Connection

Before starting the frontend, ensure the backend is running:

```bash
# In a separate terminal, from backend directory
cd /mnt/c/Users/a/Desktop/phase-3/backend
python -m uvicorn src.main:app --reload
```

Test backend connectivity:

```bash
curl -X GET http://localhost:8000/api/health
# Expected: {"status": "ok"}
```

### 4. Start Frontend Development Server

```bash
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

### 5. Login & Test Chat

1. Navigate to `http://localhost:3000`
2. Log in with test credentials (see Backend README for credentials)
3. Navigate to `/chat` (chat feature page)
4. Type a message: "Add a task to buy groceries"
5. Verify message appears in UI
6. Wait for agent response (should appear within 5 seconds)
7. Confirm task was created

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router pages
│   │   ├── (auth)/               # Authentication pages
│   │   │   ├── layout.tsx        # Auth layout
│   │   │   ├── login/page.tsx    # Login page
│   │   │   └── signup/page.tsx   # Signup page
│   │   ├── tasks/                # Existing task management
│   │   │   └── page.tsx
│   │   ├── chat/                 # NEW: Chat feature
│   │   │   └── page.tsx          # Chat page
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Home page
│   ├── components/               # Reusable React components
│   │   ├── Chat/                 # NEW: Chat-specific components
│   │   │   ├── ChatWindow.tsx    # Main chat container
│   │   │   ├── MessageList.tsx   # Message display
│   │   │   ├── MessageInput.tsx  # Input field
│   │   │   └── ConversationList.tsx # Sidebar
│   │   ├── Common/               # Shared components
│   │   ├── Layout/               # Layout components
│   │   └── Forms/                # Form components
│   ├── services/                 # API client services
│   │   ├── api.ts                # Base HTTP client
│   │   ├── auth.ts               # Authentication service
│   │   ├── tasks.ts              # Existing task API
│   │   └── chat.ts               # NEW: Chat API client
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.ts            # Authentication hook
│   │   ├── useTasks.ts           # Task management hook
│   │   └── useChat.ts            # NEW: Chat state management
│   ├── types/                    # TypeScript type definitions
│   │   ├── index.ts              # Global types
│   │   ├── auth.ts               # Auth types
│   │   ├── task.ts               # Task types
│   │   └── chat.ts               # NEW: Chat types
│   ├── utils/                    # Utility functions
│   │   ├── jwt.ts                # JWT token handling
│   │   ├── domain.ts             # NEW: Domain validation
│   │   ├── errors.ts             # Error handling
│   │   └── format.ts             # Formatting utilities
│   ├── middleware.ts             # Next.js middleware
│   └── constants/                # Configuration constants
├── tests/                        # Test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests (Playwright)
│   └── fixtures/                 # Test data
├── public/                       # Static assets
├── .env.local                    # Local environment (not committed)
├── .env.example                  # Environment template
├── next.config.ts                # Next.js config
├── tsconfig.json                 # TypeScript config
├── tailwind.config.ts            # Tailwind CSS config
├── package.json                  # Dependencies
└── README.md                     # Project documentation
```

---

## Key Files to Edit

When implementing the ChatKit feature, focus on these files:

### 1. Chat Service (`src/services/chat.ts`)

Implements API client for chat endpoints:

```typescript
import { Message, Conversation, ChatResponse } from '@/types/chat'

export class ChatService {
  private apiUrl: string

  constructor() {
    this.apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }

  async sendMessage(
    conversationId: string | null,
    message: string
  ): Promise<ChatResponse> {
    const response = await fetch(`${this.apiUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // JWT token automatically included via cookies
      },
      credentials: 'include', // Include httpOnly cookies
      body: JSON.stringify({
        conversation_id: conversationId,
        message,
      }),
    })

    if (!response.ok) {
      throw this.handleError(response)
    }

    return response.json()
  }

  // ... other methods
}

export const chatService = new ChatService()
```

### 2. Chat Hook (`src/hooks/useChat.ts`)

Manages chat state:

```typescript
import { useState, useCallback } from 'react'
import { chatService } from '@/services/chat'
import { Message, Conversation } from '@/types/chat'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (content: string, conversationId?: string) => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await chatService.sendMessage(conversationId || null, content)
        setMessages((prev) => [...prev, response.user_message, response.agent_response])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return { messages, conversations, isLoading, error, sendMessage }
}
```

### 3. Chat Page (`src/app/chat/page.tsx`)

Main chat interface:

```typescript
'use client'

import { useEffect } from 'react'
import { ChatWindow } from '@/components/Chat/ChatWindow'
import { useAuth } from '@/hooks/useAuth'
import { useChat } from '@/hooks/useChat'
import { validateDomain } from '@/utils/domain'

export default function ChatPage() {
  const { user } = useAuth()
  const chat = useChat()

  useEffect(() => {
    // Validate domain allowlist
    if (!validateDomain()) {
      return <div>This application is not available on this domain</div>
    }
  }, [])

  if (!user) {
    return <div>Please log in to use the chat</div>
  }

  return (
    <div className="flex h-screen">
      <ChatWindow {...chat} />
    </div>
  )
}
```

### 4. Chat Types (`src/types/chat.ts`)

TypeScript interfaces:

```typescript
export type UUID = string
export type MessageRole = 'user' | 'assistant'
export type MessageStatus = 'sending' | 'sent' | 'failed'

export interface Message {
  id: UUID
  conversationId: UUID
  role: MessageRole
  content: string
  status?: MessageStatus
  toolCalls?: ToolCall[]
  createdAt: string
}

export interface Conversation {
  id: UUID
  title: string
  createdAt: string
  updatedAt: string
  messageCount: number
  lastMessage?: string
}

export interface ChatResponse {
  conversationId: UUID
  userMessage: Message
  agentResponse: Message
}

export interface ToolCall {
  tool: string
  parameters: Record<string, unknown>
  result: Record<string, unknown>
}
```

### 5. Chat Components

**`src/components/Chat/ChatWindow.tsx`** — Main container:
```typescript
export function ChatWindow({ messages, isLoading, error, sendMessage }) {
  return (
    <div className="flex h-full">
      <ConversationList />
      <div className="flex-1 flex flex-col">
        <ChatHeader />
        <MessageList messages={messages} isLoading={isLoading} />
        <MessageInput onSend={sendMessage} disabled={isLoading} />
        {error && <ErrorBanner error={error} />}
      </div>
    </div>
  )
}
```

**`src/components/Chat/MessageList.tsx`** — Message display:
```typescript
export function MessageList({ messages, isLoading }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4" role="log">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  )
}
```

**`src/components/Chat/MessageInput.tsx`** — Input field:
```typescript
export function MessageInput({ onSend, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input)
      setInput('')
    }
  }

  return (
    <div className="border-t p-4">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message..."
        maxLength={5000}
        disabled={disabled}
        className="w-full p-2 border rounded"
      />
      <button onClick={handleSubmit} disabled={disabled || !input.trim()}>
        Send
      </button>
      <span className="text-xs text-gray-500">
        {input.length}/5000
      </span>
    </div>
  )
}
```

---

## Development Workflow

### 1. Build Chat Components

```bash
# Start with Chat UI components
npm run dev

# Components to build (in order):
# 1. MessageList
# 2. MessageInput
# 3. ConversationList
# 4. ChatWindow (combines above)
# 5. ChatPage (integrates with auth)
```

### 2. Run Tests

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

### 3. Build for Production

```bash
# Type check
npm run type-check

# Build
npm run build

# Start production server
npm start
```

---

## Testing Chat Locally

### Manual Testing

1. **Send Message**:
   - Type: "Add a task to buy milk"
   - Verify message appears immediately (optimistic UI)
   - Wait for agent response
   - Verify agent response appears

2. **Resume Conversation**:
   - Send a message
   - Refresh page (⌘R or Ctrl+R)
   - Verify conversation history loads
   - Verify old message still visible

3. **Error Handling**:
   - Stop backend API
   - Try to send message
   - Verify error message appears
   - Verify retry button works when backend restarts

4. **Authentication**:
   - Log out (if implemented)
   - Verify chat disabled
   - Log back in
   - Verify chat works again

### Automated Testing

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run specific test file
npm run test -- src/components/Chat/__tests__/ChatWindow.test.tsx

# Run tests with coverage
npm run test -- --coverage
```

### E2E Testing (Playwright)

```bash
# Run E2E tests
npm run test:e2e

# Run specific E2E test
npm run test:e2e -- tests/e2e/chat.spec.ts

# Run in headed mode (see browser)
npm run test:e2e -- --headed
```

---

## API Endpoints Reference

All endpoints require JWT authentication (included in httpOnly cookies).

### Send Chat Message

```
POST /api/chat
Authorization: <JWT in cookie>
Content-Type: application/json

{
  "conversation_id": "uuid" or null,
  "message": "Add a task to buy groceries"
}

Response (200):
{
  "conversation_id": "uuid",
  "user_message": {...},
  "agent_response": {...}
}

Errors:
401: Token expired or invalid
400: Invalid message (empty or too long)
429: Rate limit exceeded
500: Server error
```

### List Conversations

```
GET /api/chat/conversations?limit=20&offset=0
Authorization: <JWT in cookie>

Response (200):
{
  "conversations": [...],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Get Conversation Messages

```
GET /api/chat/{conversation_id}?limit=50&offset=0
Authorization: <JWT in cookie>

Response (200):
{
  "conversation_id": "uuid",
  "messages": [...],
  "total": 24
}
```

---

## Common Issues

### Backend Connection Failed

**Problem**: "Connection refused" when frontend tries to reach backend

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL
3. Verify CORS is enabled in backend (should be by default)

### JWT Token Not Found

**Problem**: Chat page shows "Please log in" even after logging in

**Solution**:
1. Check browser cookies (DevTools > Application > Cookies)
2. Verify httpOnly cookie is set by backend
3. Clear cookies and log in again
4. Check backend returns `Set-Cookie` header

### Messages Not Sending

**Problem**: Message input doesn't respond to send button

**Solution**:
1. Check browser console for errors
2. Verify backend is running and accepting requests
3. Check network tab in DevTools for failed requests
4. Verify `NEXT_PUBLIC_API_URL` is correct

### Domain Allowlist Blocking Access

**Problem**: "This application is not available on this domain"

**Solution**:
1. For development: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` can be unset
2. For staging/production: Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set correctly
3. Check middleware logic in `src/middleware.ts`

---

## Environment Variables

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_ENVIRONMENT` | Yes | `development` | Environment name |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | No (dev), Yes (prod) | `domain-key-123` | OpenAI domain allowlist key |

---

## Helpful Commands

```bash
# Start development server
npm run dev

# Type check without building
npm run type-check

# Lint code
npm run lint

# Format code
npm run format

# Run tests
npm run test

# Build for production
npm run build

# Start production server
npm start

# Clean build artifacts
npm run clean
```

---

## Debugging Tips

### Enable Debug Logging

Add to `.env.local`:
```
DEBUG=chatkit:*
```

Then in code:
```typescript
import debug from 'debug'
const log = debug('chatkit:chat')

log('Sending message:', message)
```

### Inspect Network Requests

In browser DevTools:
1. Open Network tab
2. Send a chat message
3. Look for POST to `/api/chat`
4. Check Request/Response headers and body
5. Verify `Authorization` header is present

### Inspect Redux/State (if using Redux)

Install Redux DevTools browser extension:
- Chrome: https://chrome.google.com/webstore/detail/redux-devtools
- Firefox: https://addons.mozilla.org/firefox/addon/reduxdevtools/

---

## Documentation Links

- [Feature Specification](./spec.md) — Complete requirements
- [Implementation Plan](./plan.md) — Architecture and design decisions
- [Research & Decisions](./research.md) — Technical deep-dive
- [Backend API Spec](../../006-ai-agent-chat-api/spec.md) — Backend endpoints
- [Constitution](../../../../.specify/memory/constitution.md) — Project principles

---

## Next Steps

1. **Review** the files in `specs/007-chatkit-frontend/` directory
2. **Setup** local development environment following Quick Setup section
3. **Create** chat components starting with `MessageList` → `MessageInput` → `ChatWindow`
4. **Integrate** with backend API using `ChatService`
5. **Test** manually and with automated tests
6. **Deploy** to staging/production following production deployment section in [plan.md](./plan.md)

---

**Last Updated**: 2026-01-17
**Status**: ✅ Ready for Development
