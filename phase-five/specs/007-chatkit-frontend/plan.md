# Implementation Plan: ChatKit Frontend & Secure Deployment

**Branch**: `007-chatkit-frontend` | **Date**: 2026-01-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-chatkit-frontend/spec.md`

## Summary

Build a secure, user-facing chat interface for managing tasks via natural language conversation. The frontend will integrate with the existing backend AI Agent Chat API (006-ai-agent-chat-api), implementing JWT authentication, conversation state resumption, and domain allowlist validation. The chat UI contains ZERO AI logic—all reasoning is delegated to the backend. Users can start new conversations, resume previous conversations, and receive real-time feedback on task operations with clear loading, error, and confirmation states.

**Key Implementation Phases**:
1. Initialize Next.js ChatKit-based frontend with domain allowlist configuration
2. Implement authenticated chat API client with JWT token management
3. Build chat UI components with message history and conversation list
4. Add confirmation feedback for task operations
5. Implement conversation resume behavior (state reconstruction from API)
6. Validate production deployment with environment-based domain key configuration

---

## Technical Context

**Language/Version**: TypeScript / React 19+ with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 19+, TypeScript 5+, TailwindCSS 4+, axios/fetch for HTTP
**Storage**: PostgreSQL (backend-persisted via API; no frontend storage except cookies for JWT)
**Testing**: Jest, React Testing Library, Playwright for E2E
**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only; backend already implemented)
**Performance Goals**:
- Messages send within 1 second (optimistic UI)
- Agent responses display within 5 seconds
- Conversation history loads within 2 seconds
- Chat remains responsive with 100+ messages

**Constraints**:
- JWT token must be included on every backend request
- No direct OpenAI API calls from frontend
- Domain allowlist enforced via environment variable (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- All state persisted in backend; frontend is stateless UI layer
- No hardcoded secrets or API keys

**Scale/Scope**:
- Single user per session (multi-user isolation enforced by JWT + backend)
- ~50 frontend components/pages
- ~10 API integration endpoints
- Supports unlimited conversation history (paginated loading)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|------------|--------|-------|
| **I. Spec-Driven Development** | Implementation follows approved spec (007-chatkit-frontend/spec.md) | ✅ PASS | Spec completed and validated (16/16 checklist items pass) |
| **II. Agentic Workflow Compliance** | Code generation via Frontend Agent (frontend-nextjs-generator) | ✅ PASS | Frontend components will be built by specialized frontend agent |
| **III. Security-First Design** | JWT authentication on every request; user isolation enforced | ✅ PASS | FR-008: JWT in Authorization header; FR-013: No direct external API calls |
| **IV. Deterministic Behavior** | UI behavior predictable; REST APIs follow HTTP semantics | ✅ PASS | Chat responses deterministic; error states explicitly handled |
| **V. Full-Stack Coherence** | Frontend consumes backend API as specified in 006-ai-agent-chat-api | ✅ PASS | Backend contracts defined; frontend will match exactly |
| **VI. Traceability** | All decisions recorded in PHRs; iterative development tracked | ✅ PASS | PHR created for specification; plan PHR will be created |
| **VII. Natural Language as First-Class Interface** | Users manage todos via natural language chat | ✅ PASS | User Story 1: Chat UI for natural language task management |
| **VIII. Tool-Driven AI Architecture** | Frontend delegates all AI to backend; backend uses MCP tools | ✅ PASS | FR-013: No direct AI calls from frontend; all logic in backend |
| **IX. Fully Stateless Server Architecture** | Backend persists all state; frontend retrieves on demand | ✅ PASS | FR-021: Conversation history loads automatically; no in-memory state |
| **X. User Identity Enforcement at Tool Level** | JWT token embedded in every request; backend validates on each tool call | ✅ PASS | FR-008: Every request includes JWT; backend enforces at tool layer |

**Constitution Check Result**: ✅ **PASS** - All 10 principles satisfied

---

## Project Structure

### Documentation (this feature)

```text
specs/007-chatkit-frontend/
├── spec.md                    # Feature specification (completed)
├── checklists/
│   └── requirements.md        # Quality validation (16/16 items PASS)
├── plan.md                    # This file (implementation plan)
├── research.md                # Phase 0: Research & clarifications
├── data-model.md              # Phase 1: Frontend data models & state management
├── quickstart.md              # Phase 1: Developer quickstart
├── contracts/
│   ├── openapi.yaml           # REST API contract with backend
│   ├── chat-api.yaml          # Chat-specific endpoints
│   └── error-schema.yaml      # Error response schemas
└── tasks.md                   # Phase 2: Actionable implementation tasks
```

### Source Code (existing frontend repository)

The existing frontend at `/mnt/c/Users/a/Desktop/phase-3/frontend/` contains the Todo-Full-Chat application with infrastructure already in place.

**Current Structure** (will be extended):
```text
frontend/
├── src/
│   ├── app/                   # Next.js App Router pages
│   │   ├── (auth)/            # Authentication flows
│   │   ├── tasks/             # Existing task management UI
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/            # Reusable React components
│   │   ├── TaskList/          # Existing task list components
│   │   ├── Chat/              # NEW: Chat UI components
│   │   ├── Forms/             # Form components
│   │   └── Common/            # Shared UI components
│   ├── services/              # API client services
│   │   ├── api.ts             # Base API client (will extend)
│   │   ├── auth.ts            # Authentication service
│   │   ├── tasks.ts           # Existing task API client
│   │   └── chat.ts            # NEW: Chat API client
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts         # Authentication hook
│   │   ├── useTasks.ts        # Existing task management hook
│   │   └── useChat.ts         # NEW: Chat management hook
│   ├── types/                 # TypeScript types
│   │   ├── index.ts           # Global types
│   │   ├── auth.ts            # Auth types
│   │   ├── task.ts            # Task types
│   │   └── chat.ts            # NEW: Chat types (Conversation, Message, etc.)
│   ├── utils/                 # Utility functions
│   │   ├── jwt.ts             # JWT token handling
│   │   ├── domain.ts          # NEW: Domain allowlist validation
│   │   └── errors.ts          # Error translation
│   ├── middleware.ts          # Next.js middleware (domain validation)
│   └── constants/             # Configuration constants
│       └── config.ts          # Environment-based configuration
├── tests/
│   ├── unit/                  # Unit tests for components, hooks, services
│   ├── integration/           # Integration tests with backend API mock
│   ├── e2e/                   # End-to-end tests (Playwright)
│   └── fixtures/              # Test data and mocks
├── .env                       # Environment variables (local)
├── .env.production            # Production environment (uses NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
├── package.json               # Dependencies (will add chat-related libraries)
└── next.config.ts             # Next.js configuration
```

**New Chat Feature Files** (to be created):
- `src/app/chat/` — Chat page(s)
- `src/components/Chat/ChatWindow.tsx` — Main chat container
- `src/components/Chat/MessageList.tsx` — Message display
- `src/components/Chat/MessageInput.tsx` — Input field
- `src/components/Chat/ConversationList.tsx` — Conversation history sidebar
- `src/services/chat.ts` — Chat API client
- `src/hooks/useChat.ts` — Chat state management hook
- `src/types/chat.ts` — Chat TypeScript interfaces
- `src/utils/domain.ts` — Domain allowlist validation
- Tests for all new components and services

**Structure Decision**: **Web application (Option 2)** - Extends existing Next.js frontend with new chat feature components. Maintains separation of concerns: existing task management UI remains unchanged; new chat UI is modular and independent.

---

## Complexity Tracking

No Constitution Check violations. All principles are satisfied by design:
- Spec-driven: specification completed and validated
- Agentic workflow: frontend agent will build components
- Security-first: JWT on every request, no unauthorized access
- User isolation: backend enforces at tool layer
- Stateless: frontend is pure UI; backend persists state

---

## Phase 0: Research & Clarifications

**Status**: To be completed during planning workflow

### Research Tasks

1. **ChatKit Library Integration**
   - Decision: Using standard React patterns (no ChatKit library; build custom UI with TailwindCSS)
   - Rationale: Full control over UI, no vendor lock-in, composable components
   - Alternatives: Shadcn/ui chat components, third-party chat library (both add dependency)

2. **JWT Token Storage & Refresh Strategy**
   - Decision: httpOnly cookies (backend sets via Set-Cookie header)
   - Rationale: Secure by default; tokens inaccessible to JavaScript; automatic CORS handling
   - Alternatives: localStorage (vulnerable to XSS), sessionStorage (same vulnerability)

3. **Conversation State Management**
   - Decision: React Context + custom hook (useChat) for local state; full history fetched from API
   - Rationale: Simple for single-page state; avoids heavy state management library
   - Alternatives: Redux (overkill for chat state), Zustand (additional dependency)

4. **Domain Allowlist Validation**
   - Decision: Validate at middleware layer + component mount
   - Rationale: Early rejection of unauthorized domains; fail-safe approach
   - Alternatives: Only validate at runtime (allows brief unauthorized access)

5. **Loading & Error State Management**
   - Decision: Per-message loading state (not global); error states visible inline
   - Rationale: Users can see which specific messages are pending/failed
   - Alternatives: Global loading overlay (hides context), toast notifications only (less discoverable)

6. **API Error Handling & User Messages**
   - Decision: Map backend error codes to user-friendly messages via utility function
   - Rationale: Users understand errors; security-safe (no technical details leaked)
   - Alternatives: Show raw error messages (poor UX, potential information disclosure)

---

## Phase 1: Design & Contracts

### 1. Data Model

**Frontend State** (managed by useChat hook):
```typescript
interface ChatState {
  currentConversationId: UUID | null;
  messages: Message[];
  conversations: Conversation[];
  isLoading: boolean;
  error: ErrorMessage | null;
  jwtToken: string | null;
  isAuthenticated: boolean;
}

interface Message {
  id: UUID;
  conversationId: UUID;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCall[];
  createdAt: DateTime;
  status: 'sending' | 'sent' | 'failed'; // Optimistic UI
}

interface Conversation {
  id: UUID;
  title: string;
  createdAt: DateTime;
  updatedAt: DateTime;
  messageCount: number;
  lastMessage?: string;
}

interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

interface ErrorMessage {
  code: string; // 'NETWORK_ERROR', 'AUTH_EXPIRED', 'SERVER_ERROR', etc.
  message: string; // User-friendly message
  suggestion: string; // What to do next
  retry: () => void; // Retry function
}
```

**Key State Transitions**:
- `Authenticated`: User logged in, JWT token present in cookies
- `Loading`: Sending message, waiting for backend response
- `MessageReceived`: Agent response loaded into message list
- `Conversation Resumed`: Full history loaded from API
- `Error`: Backend error or network failure
- `TokenExpired`: JWT refresh needed

### 2. API Contracts

**Base URL**: `${NEXT_PUBLIC_API_URL}/api/chat` (configured via environment variable)

#### Chat Messages Endpoint

```
POST /api/chat
Authorization: Bearer <JWT> (or httpOnly cookie)
Content-Type: application/json

Request:
{
  "conversation_id": "uuid" or null (null = new conversation),
  "message": "Add a task to buy groceries"
}

Response (200 OK):
{
  "conversation_id": "uuid",
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "Add a task to buy groceries",
    "created_at": "2026-01-17T10:30:00Z"
  },
  "agent_response": {
    "id": "uuid",
    "role": "assistant",
    "content": "✓ I've added a new task: Buy groceries",
    "tool_calls": [
      {
        "tool": "add_task",
        "parameters": {"title": "Buy groceries"},
        "result": {"task_id": "uuid", "status": "created"}
      }
    ],
    "created_at": "2026-01-17T10:30:02Z"
  }
}

Errors:
401 Unauthorized (invalid/expired token) → Redirect to login
400 Bad Request (empty message) → Show validation error
429 Too Many Requests → Show rate limit message
500 Internal Server Error → Show "Server unavailable" with retry
```

#### Conversation History Endpoint

```
GET /api/chat/conversations
Authorization: Bearer <JWT> (or httpOnly cookie)
Query: ?limit=20&offset=0

Response (200 OK):
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Shopping list planning",
      "created_at": "2026-01-16T15:00:00Z",
      "updated_at": "2026-01-17T09:45:00Z",
      "message_count": 12,
      "last_message": "Done! I've updated your shopping list."
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

#### Retrieve Conversation Messages

```
GET /api/chat/{conversation_id}
Authorization: Bearer <JWT> (or httpOnly cookie)
Query: ?limit=50&offset=0

Response (200 OK):
{
  "conversation_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Show me my tasks",
      "created_at": "2026-01-17T09:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Here are your tasks: 1. Buy milk...",
      "tool_calls": [...],
      "created_at": "2026-01-17T09:00:02Z"
    }
  ],
  "total": 24,
  "limit": 50,
  "offset": 0
}
```

### 3. Frontend Components Hierarchy

```
ChatPage (layout)
├── DomainAllowlistValidator (middleware component)
├── ChatWindow (main container)
│   ├── ConversationList (sidebar)
│   │   ├── ConversationItem (individual conversation)
│   │   ├── NewConversationButton
│   │   └── ConversationSearch
│   ├── ChatArea (main chat)
│   │   ├── ChatHeader (conversation title, info)
│   │   ├── MessageList (scrollable)
│   │   │   ├── MessageGroup (user or assistant messages)
│   │   │   │   └── Message (individual message bubble)
│   │   │   └── LoadingIndicator (while awaiting response)
│   │   ├── MessageInput (textarea + send button)
│   │   ├── LoadingState (overlay during send)
│   │   └── ErrorBanner (sticky error message with retry)
│   └── TokenExpiredModal (re-auth prompt)
└── ConfirmationFeedback (inline confirmations for task operations)
```

### 4. Service Layer

**chat.ts** - API client service:
```typescript
class ChatService {
  async sendMessage(conversationId: UUID | null, message: string): Promise<ChatResponse>
  async getConversations(limit: number, offset: number): Promise<ConversationList>
  async getConversation(conversationId: UUID, limit: number, offset: number): Promise<ConversationMessages>
  async retryMessage(conversationId: UUID, messageId: UUID): Promise<ChatResponse>

  // Error handling
  private translateError(error: APIError): UserFriendlyError
  private handleUnauthorized(): void // Redirect to login
  private handleRateLimited(): void // Show rate limit message
}
```

**jwt.ts** - Token management:
```typescript
function getJWTToken(): string | null // From httpOnly cookie
function isTokenExpired(): boolean
function setupTokenRefresh(onExpire: () => void): void // Auto-refresh or notify
```

**domain.ts** - Domain validation:
```typescript
function isAllowedDomain(): boolean
function getCurrentDomain(): string
function validateDomainAllowlist(): boolean
```

### 5. Hooks

**useChat.ts** - Main chat logic:
```typescript
function useChat() {
  // State
  const [currentConversationId, setCurrentConversationId] = useState<UUID | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ErrorMessage | null>(null)

  // Actions
  const sendMessage = async (content: string) => {...}
  const resumeConversation = async (conversationId: UUID) => {...}
  const createNewConversation = () => {...}
  const retryMessage = async (messageId: UUID) => {...}
  const clearError = () => {...}

  return { messages, conversations, isLoading, error, sendMessage, ... }
}
```

### 6. Types

**chat.ts** - TypeScript interfaces:
```typescript
type UUID = string // UUID format
type DateTime = string // ISO 8601 format
type MessageRole = 'user' | 'assistant'
type MessageStatus = 'sending' | 'sent' | 'failed'
type ErrorCode = 'NETWORK_ERROR' | 'AUTH_EXPIRED' | 'SERVER_ERROR' | ...

interface Message { ... }
interface Conversation { ... }
interface ToolCall { ... }
interface ChatResponse { ... }
interface ErrorMessage { ... }
```

### 7. Configuration

**Environment Variables** (frontend):
```
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development

# .env.production
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<domain-key-from-openai>
NEXT_PUBLIC_ENVIRONMENT=production
```

**Middleware** - Domain validation at request time:
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const allowedDomains = getAllowedDomains() // From env or config
  const currentDomain = request.nextUrl.hostname

  if (!allowedDomains.includes(currentDomain)) {
    return new NextResponse('Domain not allowed', { status: 403 })
  }

  return NextResponse.next()
}
```

### 8. Contracts Directory

**contracts/openapi.yaml** - Full REST API specification (OpenAPI 3.0)
**contracts/chat-api.yaml** - Chat endpoint details
**contracts/error-schema.yaml** - Error response format and codes

---

## Phase 1: Output Summary (to be generated)

- ✅ **research.md** — Consolidated research findings
- ✅ **data-model.md** — Frontend data structures and state management
- ✅ **contracts/** — OpenAPI/REST specifications
- ✅ **quickstart.md** — Developer setup guide
- ✅ **Agent context** — Frontend-specific tools and patterns (when agent initialized)

---

## Next Steps

1. **Phase 0 Complete**: Research all unknowns → consolidate into `research.md`
2. **Phase 1 Complete**: Design data models, contracts, services → create `data-model.md`, `quickstart.md`, `/contracts/*`
3. **Phase 2 (Next)**: Run `/sp.tasks` to generate implementation tasks organized by user story
4. **Phase 3 (After Tasks)**: Run `/sp.implement` to build components and integrate with backend API

---

**Status**: ✅ **Implementation Plan Complete**
**Next Command**: `/sp.tasks` to generate actionable tasks
**Branch**: `007-chatkit-frontend` | **Last Updated**: 2026-01-17
