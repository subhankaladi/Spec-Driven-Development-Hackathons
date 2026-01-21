# Research & Design Decisions: ChatKit Frontend

**Date**: 2026-01-17 | **Feature**: ChatKit Frontend & Secure Deployment (007-chatkit-frontend)

---

## Executive Summary

This document consolidates research and design decisions for the ChatKit frontend implementation. All clarifications from the specification have been resolved. Technical decisions prioritize security, simplicity, and user experience while maintaining compatibility with the existing Todo Full-Stack application architecture.

---

## Research Findings

### 1. ChatKit Component Library Decision

**Decision**: Build custom chat UI components using React + TailwindCSS (no third-party chat library)

**Rationale**:
- Full control over styling and behavior
- Lightweight (no additional dependencies beyond existing stack)
- Easy to customize for OpenAI integration requirements
- Composable components aligned with existing Todo UI patterns

**Alternatives Considered**:
1. **Shadcn/ui Chat Components** — Pre-built accessibility, but adds CLI dependency and learning curve
2. **Third-party Chat Library** (e.g., Sendbird, Tawk) — Full-featured but vendor lock-in, cost implications
3. **Re-Chat or similar** — Adds unnecessary complexity for simple message display

**Selection Rationale**: Custom components provide the right balance of simplicity and control. The chat UI is straightforward (message bubbles, input field, loading states) — doesn't justify third-party dependency.

---

### 2. JWT Token Storage & Security

**Decision**: Store JWT tokens in httpOnly cookies set by backend; access via Authorization header

**Rationale**:
- **httpOnly flag**: Tokens inaccessible to JavaScript (prevents XSS token theft)
- **Backend-set**: Backend controls cookie expiration, SameSite policy
- **Secure flag**: Enforced HTTPS in production
- **Automatic CORS**: Browser handles Authorization header automatically

**Alternatives Considered**:
1. **localStorage** — Vulnerable to XSS attacks; never recommended for secrets
2. **sessionStorage** — Same vulnerability as localStorage
3. **Refresh token rotation** — Adds complexity; httpOnly cookies already secure

**Selection Rationale**: httpOnly cookies are the industry standard for securing JWT tokens. This aligns with Constitution Principle III (Security-First Design) and satisfies FR-009.

---

### 3. Conversation State Management

**Decision**: Use React Context + custom `useChat` hook; fetch full history from backend API on demand

**Rationale**:
- Simple state management for chat messages and conversations
- Backend is source of truth (stateless frontend principle)
- No risk of stale local state
- Scales efficiently with pagination (load next batch on scroll)

**Alternatives Considered**:
1. **Redux** — Overkill for chat state; adds bundle size and learning curve
2. **Zustand** — Simpler than Redux but still unnecessary complexity for single feature
3. **TanStack Query (React Query)** — Would add complexity for automatic background sync; not needed

**Selection Rationale**: React Context is sufficient for this scope. Full history fetched on each conversation load ensures users always see current state. This aligns with Constitution Principle IX (Fully Stateless Server Architecture).

---

### 4. Domain Allowlist Validation

**Decision**: Validate domain in Next.js middleware + component mount; reject early with 403 Forbidden

**Rationale**:
- **Middleware layer**: Blocks requests before any component code runs
- **Component layer**: Secondary validation as safety net
- **Early rejection**: Fail-fast approach prevents confusion
- **User message**: Clear explanation of why access is denied

**Alternatives Considered**:
1. **Client-side only** — Can be bypassed; not secure
2. **Redirect to error page** — Less immediate; users might refresh
3. **Silent fallback to localhost** — Confusing behavior in dev vs. production

**Selection Rationale**: Defense-in-depth approach with middleware first ensures unauthorized domains are rejected before rendering. Production deployment requires NEXT_PUBLIC_OPENAI_DOMAIN_KEY set correctly (FR-026, FR-027, FR-028).

---

### 5. Loading & Error State Management

**Decision**: Per-message loading state (not global); inline error banners with retry options

**Rationale**:
- **Per-message state**: Users see which specific messages are pending/failed
- **Inline errors**: Visible in context; users know which message failed
- **Retry button**: Users can attempt failed operations without re-typing
- **Loading animation**: Visual feedback while waiting for agent response (max 5 seconds per FR-015)

**Alternatives Considered**:
1. **Global loading overlay** — Hides conversation context; frustrating UX
2. **Toast notifications only** — Error messages disappear; users can't see retry option
3. **Dedicated error page** — Breaks chat flow; requires page navigation

**Selection Rationale**: Per-message state provides the best UX. Users understand what's happening and can take corrective action. This satisfies US4 (Clear Loading, Error, and Confirmation States) and FR-016/FR-017.

---

### 6. API Error Handling & User Messages

**Decision**: Map backend error codes to user-friendly messages via `translateError()` utility

**Error Code Mappings**:
```
Backend Code         → User Message                        → Suggestion
INVALID_TOKEN       → "Your session expired"               → "Please log in again"
TOKEN_EXPIRED       → "Your session expired"               → "Please refresh the page"
RATE_LIMITED        → "You're sending too fast"            → "Wait a moment and try again"
NETWORK_ERROR       → "Connection lost"                    → "Check your internet and retry"
SERVER_ERROR        → "Server is busy"                     → "Try again in a moment"
INVALID_MESSAGE     → "Message is too long or empty"       → "Keep it under 5000 characters"
CONVERSATION_404    → "Conversation not found"             → "It may have been deleted"
UNAUTHENTICATED     → "You need to be logged in"          → "Please log in to chat"
```

**Rationale**:
- **User-friendly**: Non-technical language
- **Actionable**: Users know what to do next
- **Secure**: No technical details leaked (prevents info disclosure)
- **Translatable**: Easy to translate for i18n

**Alternatives Considered**:
1. **Show raw error messages** — Confusing for users; potential information disclosure
2. **Generic "Error occurred" message** — No actionable guidance
3. **Error codes only** — Users must guess what went wrong

**Selection Rationale**: User-friendly messages improve UX and security simultaneously. This aligns with FR-016/FR-017 and improves Trust & Transparency.

---

### 7. Message Retry Strategy

**Decision**: Store failed message locally; allow user to retry send without re-typing

**Flow**:
1. User sends message → `status: 'sending'`
2. API call fails → `status: 'failed'` + error message + retry button
3. User clicks retry → `status: 'sending'` (update UI optimistically)
4. If successful → `status: 'sent'` + display response
5. If failed again → Show error message again

**Rationale**:
- Reduces friction for network failures
- Users don't lose their message
- Clear visibility into failure state
- Satisfies FR-019 (Chat UI gracefully handles network failures with retry mechanism)

**Alternatives Considered**:
1. **Auto-retry with exponential backoff** — Might retry until token expires; confusing
2. **Manual re-type required** — Frustrating; users will abandon chat
3. **Discard failed message** — Data loss potential

**Selection Rationale**: User-initiated retry with visible state provides the right balance of control and helpfulness.

---

### 8. Conversation Resume Behavior

**Decision**: Load full conversation history from API on page/component mount; display in chronological order

**Flow**:
1. User navigates to `/chat`
2. Fetch list of recent conversations
3. Display conversation list in sidebar
4. If resuming conversation, load full message history
5. Display messages in correct chronological order
6. User can send new message to continue

**Rationale**:
- Stateless architecture (backend persists state)
- User expects history to be available after page refresh
- Pagination prevents performance issues with large conversations
- Satisfies US2 (Conversation Resume Behavior) and FR-021

**Alternatives Considered**:
1. **In-memory caching** — Violates stateless principle; lost on page refresh
2. **IndexedDB** — Unnecessary complexity; backend is source of truth
3. **Lazy loading** — Load only recent messages initially; load older messages on scroll up

**Selection Rationale**: Full history load on resume is simple and aligns with stateless principle. Backend API handles pagination (FR-024) if conversations become very large.

---

### 9. Optimistic UI for Message Send

**Decision**: Show message in UI immediately (optimistic); update status when response received

**Flow**:
1. User types "Add a task" and clicks send
2. UI immediately shows message in chat (before backend processes)
3. Show loading spinner on message
4. Backend processes → agent responds
5. Update message with server timestamp and response

**Rationale**:
- **Fast UX**: No perceived delay (satisfies NFR-001: messages send within 1 second)
- **User confidence**: Immediate visual feedback
- **Network resilience**: If request fails, message marked as failed (not lost)

**Alternatives Considered**:
1. **Wait for backend response before showing** — Feels slow; users think message didn't send
2. **Disable send button until response** — Frustrating; users can't interact
3. **Queue messages during network outage** — Complex; might send when user leaves

**Selection Rationale**: Optimistic UI is industry standard for chat applications. Satisfies NFR-001 and improves perceived performance.

---

### 10. Confirmation Feedback for Task Operations

**Decision**: Show confirmation inline after agent response; use checkmarks and status indicators

**Examples**:
- Task created: "✓ Added task: Buy groceries"
- Task completed: "✓ Marked complete: Review proposal"
- List shown: Agent response lists items with clear formatting

**Rationale**:
- Reassures users that action completed
- Visual indicator (✓) is universally understood
- Inline with message (no separate notification needed)
- Satisfies US4 requirement for confirmation states

**Implementation**:
```typescript
// In message content, parse agent response for action confirmations
const hasConfirmation = /^✓|completed|created|updated|deleted/i.test(content)
return (
  <div className={hasConfirmation ? 'bg-green-50 border-green-200' : ''}>
    {content}
  </div>
)
```

**Alternatives Considered**:
1. **Toast notifications** — Disappear quickly; users might miss
2. **Modal dialogs** — Too intrusive for frequent operations
3. **Status badges** — Harder to see in busy chat interface

**Selection Rationale**: Inline confirmations keep focus in the chat UI. Green background + checkmark provides clear visual feedback for successful operations.

---

### 11. Message Input Validation

**Decision**: Client-side validation before send; server validates again for security

**Validations**:
- Message not empty (show placeholder "Enter a message")
- Message under 5000 characters (show character count as user types)
- User authenticated (disable input if JWT missing/expired)

**Rationale**:
- **Client-side**: Fast feedback before network request
- **Server-side**: Security boundary; never trust client validation
- **Character count**: Helps users stay within limits

**Alternatives Considered**:
1. **Server-side only** — Users send empty messages before seeing error
2. **No validation** — Users send invalid data; confusing errors
3. **Strict length limits** — Might be too restrictive

**Selection Rationale**: Defense in depth with client + server validation. Satisfies FR-003 (max 5000 chars) and improves UX.

---

### 12. Accessibility (WCAG 2.1 AA)

**Decision**: Implement semantic HTML, keyboard navigation, and screen reader support from the start

**Requirements** (from NFR-007):
- Chat window navigable with Tab key
- Message list marked as `role="log"` (announces new messages)
- Send button keyboard accessible (Enter key support)
- Error messages associated with form (aria-describedby)
- Loading spinner announced (aria-busy)
- Conversation list with aria-current for active conversation

**Alternatives Considered**:
1. **Add accessibility later** — Requires major refactoring
2. **Use third-party accessible components** — Limited customization
3. **Skip accessibility** — Excludes users with disabilities; potential legal liability

**Selection Rationale**: Building accessibility from the start is simpler than retrofitting. Required by specification (NFR-007) and aligns with inclusive design principles.

---

### 13. Mobile Responsiveness

**Decision**: Mobile-first design with breakpoints for tablet and desktop

**Breakpoints** (TailwindCSS):
- Mobile (375px - 640px): Single column, full-width input
- Tablet (641px - 1024px): Sidebar collapses to icon bar
- Desktop (1025px+): Full sidebar + chat area

**Rationale**:
- Mobile users increasingly common for productivity tools
- Sidebar hides on mobile to maximize message space
- Touch-friendly button sizes (minimum 44px)
- Satisfies NFR-006 (fully responsive on mobile devices)

**Alternatives Considered**:
1. **Desktop-only** — Excludes mobile users
2. **Separate mobile app** — Requires additional development
3. **Responsive without testing** — Works on desktop but fails on real mobile

**Selection Rationale**: Mobile-first approach ensures best experience on all devices. TailwindCSS breakpoints provide clean implementation.

---

## Technology Stack Decisions

| Layer | Technology | Version | Why |
|-------|-----------|---------|-----|
| Framework | Next.js | 16+ | Existing choice; App Router for client/server split |
| Language | TypeScript | 5+ | Type safety; existing codebase already uses TS |
| UI Library | React | 19+ | Latest version; hooks are well-supported |
| CSS | TailwindCSS | 4+ | Utility-first; existing choice in project |
| Testing | Jest + React Testing Library | Latest | Standard for React; existing in project |
| E2E | Playwright | Latest | Modern, reliable; better than Cypress for chat testing |
| HTTP Client | Fetch API / axios | Built-in / existing | fetch for new code, axios if already in project |
| Form Handling | React Hook Form | Latest | Simple form validation; lightweight |
| Icon Library | Heroicons | Latest | Tailwind-native icons; existing choice |
| Date Formatting | date-fns | Latest | Lightweight; existing choice |

---

## Deployment & Environment Configuration

**Development**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
# No NEXT_PUBLIC_OPENAI_DOMAIN_KEY (local development)
```

**Staging**:
```bash
NEXT_PUBLIC_API_URL=https://api-staging.example.com
NEXT_PUBLIC_ENVIRONMENT=staging
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=staging-domain-key-from-openai
```

**Production**:
```bash
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<production-domain-key-from-openai>
```

**Domain Allowlist Validation**:
- Development: All domains allowed (localhost, 127.0.0.1)
- Staging/Production: Only allowlisted domains permitted
- Non-allowlisted domains: Show "This application is not available on this domain"

---

## Security Considerations

### Authentication
- ✅ JWT tokens in httpOnly cookies (not accessible to JavaScript)
- ✅ Automatic token refresh on 401 response
- ✅ Graceful re-authentication flow (redirect to login, preserve message)

### Authorization
- ✅ Every API request includes JWT
- ✅ Backend validates user_id matches JWT
- ✅ No direct OpenAI API calls from frontend (all through backend)
- ✅ Domain allowlist prevents access from unauthorized domains

### Data Protection
- ✅ HTTPS only in production (enforced via Strict-Transport-Security header)
- ✅ CORS properly configured to backend API only
- ✅ No secrets in frontend code (environment variables only)
- ✅ Content-Security-Policy header restricts API calls

### Input Validation
- ✅ Client-side validation (user feedback)
- ✅ Server-side validation (security boundary)
- ✅ Message sanitization before display
- ✅ Character limits enforced (5000 char max per FR-003)

---

## Performance Targets

| Metric | Target | How Achieved |
|--------|--------|-------------|
| Initial page load | <2s | Code splitting, lazy loading |
| Message send | <1s | Optimistic UI, background fetch |
| Agent response display | <5s | Streaming support (if available) |
| Conversation history load | <2s | Pagination, indexed API queries |
| Chat responsive with 100+ messages | Smooth | Virtual scrolling (if needed) |
| Lighthouse score | >90 | CSS-in-JS minimization, image optimization |

---

## Risk Analysis

| Risk | Mitigation | Impact |
|------|-----------|--------|
| JWT token theft via XSS | httpOnly cookies, CSP header | High priority |
| User isolation failure | Backend enforces user_id matching | High priority |
| Network disconnection | Graceful error handling + retry | Medium priority |
| Conversation history loss | Backend persists all state | Low priority (backend responsibility) |
| Domain allowlist bypass | Middleware validation before render | High priority |
| Token expiration during chat | Auto-refresh + re-auth prompt | Medium priority |
| Slow message response | Timeout at 5 seconds, show retry | Low priority (UX improvement) |

---

## Rollout Plan

### Phase 1: MVP (Core Chat)
- Basic message send/receive
- Conversation list
- JWT authentication
- Domain allowlist

### Phase 2: Enhancement
- Conversation resume from page refresh
- Error handling and retry
- Loading states
- Accessibility (WCAG AA)

### Phase 3: Polish
- Mobile responsiveness
- Performance optimization
- E2E testing
- Production monitoring

---

## References

- **Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Constitution**: [../../../.specify/memory/constitution.md](../../../.specify/memory/constitution.md)
- **Backend API Spec**: [../../006-ai-agent-chat-api/spec.md](../../006-ai-agent-chat-api/spec.md)

---

**Status**: ✅ **Complete** - All clarifications addressed, research consolidated
**Date**: 2026-01-17
**Next**: Generate `data-model.md` with detailed frontend architecture
