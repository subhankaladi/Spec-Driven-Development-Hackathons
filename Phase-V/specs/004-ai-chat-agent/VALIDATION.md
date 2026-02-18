# AI Chat Agent - End-to-End Validation Guide

**Feature**: 004-ai-chat-agent
**Created**: 2026-01-19
**Purpose**: Manual validation checklist for verifying complete implementation

## Overview

This document provides a comprehensive validation checklist for the AI Chat Agent feature. Use this guide to verify that all components work correctly in an end-to-end flow.

**Validation Time**: 30-40 minutes
**Required Environment**: Local development (backend + frontend)

---

## Pre-Validation Checklist

Before starting validation, verify these prerequisites are met:

### Environment Setup
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL database accessible (Neon Serverless)
- [ ] OpenAI API account with valid API key

### Phase-II Components Running
- [ ] Backend server running at `http://localhost:8000`
- [ ] Frontend server running at `http://localhost:3000`
- [ ] Database migrations applied (Phase-II tables exist)
- [ ] User authentication working (can sign up/sign in)

### Phase-III Dependencies Installed
- [ ] Backend: `openai>=1.0.0` installed
- [ ] Backend: `mcp-sdk>=0.1.0` installed (if available)
- [ ] Frontend: No new dependencies required (uses existing React/Next.js)

### Environment Configuration
- [ ] `backend/.env` contains `OPENAI_API_KEY`
- [ ] `backend/.env` contains `OPENAI_MODEL` (e.g., `gpt-4o-mini`)
- [ ] `backend/.env` contains `AGENT_MAX_TOKENS` (e.g., `1000`)
- [ ] All Phase-II environment variables present

### Database Migrations Applied
- [ ] Migration for `conversation` table created and applied
- [ ] Migration for `message` table created and applied
- [ ] Migration for `toolinvocation` (or `tool_invocation`) table created and applied

**Verification Command**:
```bash
python -c "
from src.models.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
assert 'conversation' in tables
assert 'message' in tables
assert 'toolinvocation' in tables or 'tool_invocation' in tables
print('✅ All required tables exist')
"
```

---

## Section 1: Backend API Validation

### 1.1 Server Health Check
- [ ] Backend server starts without errors
- [ ] Health endpoint responds correctly

**Test**:
```bash
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy"}` or similar success response

### 1.2 OpenAPI Documentation
- [ ] OpenAPI docs accessible at `http://localhost:8000/docs`
- [ ] `/chat` endpoint visible in docs
- [ ] Chat endpoint shows correct request/response schema

**Expected Schema**:
- **Request**: `{ conversation_id?: string | null, message: string }`
- **Response**: `{ conversation_id: string, message_id: string, agent_response: string, tool_invocations: array }`

### 1.3 Authentication with Chat Endpoint
- [ ] Chat endpoint requires authentication (401 without token)
- [ ] Chat endpoint accepts valid JWT token

**Test**:
```bash
# Should return 401 Unauthorized
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Get valid token
TOKEN=$(curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Should return 200 OK with agent response
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": null, "message": "Hello"}' \
  | jq
```

**Expected**:
- First request: HTTP 401
- Third request: HTTP 200 with conversation_id and agent_response

### 1.4 MCP Tools Registration
- [ ] Backend logs show MCP tools registered on startup
- [ ] All 4 tools available: `create_task`, `list_tasks`, `update_task`, `delete_task`

**Check Backend Logs**: Look for messages like:
```
INFO: Registered MCP tool: create_task
INFO: Registered MCP tool: list_tasks
INFO: Registered MCP tool: update_task
INFO: Registered MCP tool: delete_task
```

---

## Section 2: Frontend UI Validation

### 2.1 Chat Page Access
- [ ] Navigate to `http://localhost:3000/chat`
- [ ] Page loads without errors
- [ ] Chat interface displays properly
- [ ] Empty state shows when no messages exist

**Expected UI Elements**:
- Chat container with rounded corners and border
- Empty state message: "No messages yet" with icon
- Message input textarea at bottom
- Send button with icon (text hidden on mobile)

### 2.2 Authentication Flow
- [ ] Accessing `/chat` without login redirects to `/signin`
- [ ] After sign in, can access `/chat` successfully
- [ ] JWT token stored in localStorage or cookies

**Test**:
1. Sign out (if signed in)
2. Navigate to `http://localhost:3000/chat`
3. Verify redirect to `/signin`
4. Sign in with valid credentials
5. Verify redirect back to `/chat` (or `/tasks` then manually navigate to `/chat`)

### 2.3 Responsive Design
- [ ] Chat interface responsive on mobile (320px width)
- [ ] Chat interface responsive on tablet (768px width)
- [ ] Chat interface responsive on desktop (1440px width)
- [ ] Message bubbles have proper max-width on all breakpoints
- [ ] Send button shows icon-only on mobile, icon+text on desktop

**Test**: Use browser DevTools responsive mode to test breakpoints:
- 375px (mobile)
- 768px (tablet)
- 1024px (desktop)
- 1440px (large desktop)

**Expected**:
- Message bubbles: `max-w-[85%]` (mobile) → `max-w-[60%]` (desktop)
- Send button: Icon only (mobile) → Icon + "Send" text (≥640px)

### 2.4 Accessibility
- [ ] All interactive elements keyboard-navigable
- [ ] ARIA labels present on input and buttons
- [ ] Focus states visible on interactive elements
- [ ] Screen reader announcements for new messages (aria-live)

**Test**:
1. Navigate using Tab key through all interactive elements
2. Verify focus ring visible on each element
3. Check for ARIA labels in DevTools Elements inspector

---

## Section 3: Chat Functionality Validation

### 3.1 Send First Message
- [ ] Type message in input field
- [ ] Click Send button (or press Enter)
- [ ] Loading state appears while processing
- [ ] Agent response appears in chat
- [ ] User message and agent message both display correctly

**Test**:
1. Type: "Hello"
2. Press Enter
3. Verify loading indicator (3 bouncing dots + "AI is thinking...")
4. Verify agent response appears (e.g., "Hello! How can I help you today?")
5. Verify 2 message bubbles total (1 user, 1 agent)

**Expected**:
- User message: Blue background, right-aligned
- Agent message: Gray background, left-aligned
- Timestamp shown on each message

### 3.2 Create Task via Chat
- [ ] Send message to create a task
- [ ] Agent confirms task creation
- [ ] Task appears in task list at `/tasks`
- [ ] Tool invocation recorded in database

**Test**:
1. Send: "Create a task to buy milk"
2. Verify agent response confirms creation (e.g., "I've created a task: Buy milk")
3. Navigate to `http://localhost:3000/tasks`
4. Verify "Buy milk" task appears in list
5. Return to `/chat`

**Expected**:
- Agent response mentions task creation
- Task visible at `/tasks` with correct title

### 3.3 List Tasks via Chat
- [ ] Send message to list tasks
- [ ] Agent lists all user's tasks
- [ ] Task count and details match actual task list

**Test**:
1. Send: "Show me my tasks"
2. Verify agent response lists tasks
3. Compare with task list at `/tasks`

**Expected**:
- Agent lists all tasks with titles
- Task count matches actual count
- Completed/incomplete status mentioned (if applicable)

### 3.4 Update Task via Chat
- [ ] Send message to mark task as complete
- [ ] Agent confirms update
- [ ] Task status updated at `/tasks`

**Test**:
1. Send: "Mark 'Buy milk' as complete"
2. Verify agent response confirms completion
3. Navigate to `/tasks`
4. Verify "Buy milk" task shows as completed (checked)

**Expected**:
- Agent confirms task marked complete
- Task shows checked/strikethrough at `/tasks`

### 3.5 Delete Task via Chat
- [ ] Send message to delete a task
- [ ] Agent confirms deletion
- [ ] Task removed from task list

**Test**:
1. Send: "Delete the 'Buy milk' task"
2. Verify agent response confirms deletion
3. Navigate to `/tasks`
4. Verify "Buy milk" task no longer appears

**Expected**:
- Agent confirms task deleted
- Task removed from `/tasks` page

---

## Section 4: Conversation Persistence Validation

### 4.1 In-Page Persistence
- [ ] Send multiple messages (5+)
- [ ] All messages remain visible in chat
- [ ] Messages display in chronological order
- [ ] Auto-scroll keeps latest message visible

**Test**:
1. Send 5 messages in sequence
2. Verify all 10 messages (5 user + 5 agent) visible
3. Verify order: oldest at top, newest at bottom
4. Verify page auto-scrolls to newest message

### 4.2 Page Refresh Persistence
- [ ] Send several messages
- [ ] Refresh page (F5)
- [ ] All messages reload correctly
- [ ] Conversation continues from same point

**Test**:
1. Send 3 messages
2. Press F5 to refresh page
3. Verify loading spinner appears briefly
4. Verify all 6 messages (3 user + 3 agent) reappear
5. Send new message
6. Verify new message appends to existing conversation

**Expected**:
- All messages persist across refresh
- Conversation ID remains the same (check localStorage: `chat_conversation_id`)

### 4.3 Backend Restart Persistence
- [ ] Create conversation with multiple messages
- [ ] Stop backend server (Ctrl+C)
- [ ] Restart backend server
- [ ] Refresh frontend
- [ ] All messages reload correctly
- [ ] Can continue conversation

**Test** (See QUICKSTART.md Step 10 for detailed procedure):
1. Create conversation with 5+ message pairs
2. Stop backend: `Ctrl+C` in backend terminal
3. Restart backend: `uvicorn src.main:app --reload --port 8000`
4. Refresh frontend page
5. Verify all messages reload
6. Send new message
7. Verify conversation continues

**Expected**:
- All messages persist across backend restart
- No data loss
- Conversation resumes seamlessly

### 4.4 Database Record Verification
- [ ] Conversation records exist in database
- [ ] Message records linked to conversation
- [ ] Tool invocation records linked to messages
- [ ] User ID matches authenticated user

**Test**:
```bash
python -c "
from src.models.database import get_session
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.tool_invocation import ToolInvocation
from sqlmodel import select

with next(get_session()) as session:
    # Check conversation
    conv = session.exec(select(Conversation)).first()
    print(f'✓ Conversation ID: {conv.id}')
    print(f'✓ User ID: {conv.user_id}')

    # Check messages
    messages = session.exec(
        select(Message).where(Message.conversation_id == conv.id)
    ).all()
    print(f'✓ Total messages: {len(messages)}')

    # Check tool invocations
    tools = session.exec(select(ToolInvocation)).all()
    print(f'✓ Tool invocations: {len(tools)}')

    # Sample messages
    print('\\nFirst 3 messages:')
    for msg in messages[:3]:
        print(f'  [{msg.role}] {msg.content[:50]}')
"
```

**Expected**:
- Conversation record with correct user_id
- Message count matches UI message count
- Tool invocations recorded for create/update/delete/list actions

---

## Section 5: Error Handling Validation

### 5.1 Network Error Handling
- [ ] Stop backend server
- [ ] Send message from frontend
- [ ] Error message displays in UI
- [ ] Input remains enabled after error

**Test**:
1. Stop backend server (Ctrl+C)
2. Send message: "test"
3. Verify error banner appears at top of chat
4. Verify error message (e.g., "Network error" or "Failed to send message")
5. Restart backend
6. Send message again
7. Verify message sends successfully

### 5.2 Invalid Message Handling
- [ ] Send empty message (whitespace only)
- [ ] Send button disabled when input empty
- [ ] No API request made for empty message

**Test**:
1. Clear input field
2. Verify Send button is disabled
3. Type only spaces
4. Verify Send button remains disabled
5. Type "test"
6. Verify Send button enabled

### 5.3 OpenAI API Error Handling
- [ ] Invalid API key in `.env`
- [ ] Send message
- [ ] Error message displays
- [ ] Backend logs show OpenAI error

**Test**:
1. Edit `backend/.env`: set `OPENAI_API_KEY=invalid-key`
2. Restart backend
3. Send message: "test"
4. Verify error banner in frontend
5. Check backend logs for OpenAI authentication error
6. Restore valid API key and restart

### 5.4 Tool Execution Error Handling
- [ ] Agent attempts to use tool with invalid parameters
- [ ] Error captured in tool invocation record
- [ ] Agent provides graceful error response to user

**Test** (simulated):
1. Send message with ambiguous task title: "Create a task"
2. Verify agent either:
   - Asks for clarification, OR
   - Creates task with default/inferred title
3. Check database tool_invocation record has `success=true` or error details

---

## Section 6: Advanced Scenarios

### 6.1 Ambiguous Commands
- [ ] Send ambiguous message (e.g., "update my task")
- [ ] Agent asks for clarification or provides helpful response

**Test**:
1. Send: "update my task"
2. Verify agent response asks which task or what to update

### 6.2 Multi-Turn Conversation
- [ ] Have conversation with context from previous messages
- [ ] Agent references earlier messages correctly

**Test**:
1. Send: "Create a task to buy milk"
2. Send: "Mark it as complete" (without specifying task name)
3. Verify agent understands "it" refers to "buy milk" task
4. Verify task marked complete

### 6.3 Concurrent Operations
- [ ] Send message to create multiple tasks in one request
- [ ] Agent creates all tasks
- [ ] All tool invocations recorded

**Test**:
1. Send: "Create tasks to buy milk, read a book, and exercise"
2. Verify agent response mentions all 3 tasks
3. Navigate to `/tasks`
4. Verify 3 tasks created

### 6.4 Edge Case: Very Long Message
- [ ] Send message with 500+ characters
- [ ] Agent handles long message correctly
- [ ] Message displays properly in UI

**Test**:
1. Type or paste a message with 500+ characters
2. Send message
3. Verify agent responds
4. Verify message displays correctly in bubble (word-wrap, not overflow)

### 6.5 Edge Case: Special Characters
- [ ] Send message with special characters (emojis, symbols)
- [ ] Message persists correctly
- [ ] Displays correctly in UI and database

**Test**:
1. Send: "Create a task: Buy milk 🥛 @ store #groceries"
2. Verify agent creates task
3. Verify task title includes emoji and special characters
4. Refresh page
5. Verify message still displays correctly

---

## Section 7: Performance Validation

### 7.1 Response Time
- [ ] Agent responds within 5 seconds for simple requests
- [ ] Loading indicator shows during processing
- [ ] No UI freezing or blocking

**Test**:
1. Send: "Hello"
2. Start timer when Send button clicked
3. Stop timer when agent response appears
4. Verify response time < 5 seconds

**Expected**: Response time 1-3 seconds for simple messages

### 7.2 Large Conversation Handling
- [ ] Create conversation with 50+ messages
- [ ] Page loads without performance issues
- [ ] Scroll performance remains smooth

**Test**:
1. Send 25+ messages (can use script or manual)
2. Refresh page
3. Verify all messages load
4. Verify smooth scrolling in message list
5. Verify no browser lag

### 7.3 Database Query Performance
- [ ] Conversation history loads quickly (<2 seconds)
- [ ] No N+1 query issues (check backend logs)

**Check Backend Logs**: Look for SQL queries when loading chat page. Should see:
- 1 query for conversation
- 1 query for messages (with JOIN or eager loading)
- Not: 1 query per message (N+1 problem)

---

## Section 8: Security Validation

### 8.1 Authorization
- [ ] User can only access their own conversations
- [ ] Cannot access other user's conversations by changing conversation_id

**Test** (requires 2 user accounts):
1. Sign in as User A
2. Create conversation, note conversation_id
3. Sign out, sign in as User B
4. Try to send message with User A's conversation_id
5. Verify error or new conversation created

**Expected**: User B cannot access User A's conversation

### 8.2 Input Sanitization
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized in message display

**Test**:
1. Send: `<script>alert('xss')</script>`
2. Verify script does not execute
3. Verify message displays as plain text (script tags visible or escaped)

### 8.3 API Key Security
- [ ] OpenAI API key not exposed in frontend
- [ ] API key not logged in backend logs (except first/last few chars)

**Test**:
1. Check browser DevTools Network tab
2. Verify no API key in request headers or response bodies
3. Check backend logs
4. Verify API key not printed in full

---

## Section 9: Constitution Compliance

Reference: See `CONSTITUTION_COMPLIANCE.md` for detailed checklist

Quick verification:
- [ ] Spec-driven development: Implementation matches spec.md
- [ ] Agentic workflow: Uses agent service with MCP tools
- [ ] Security-first: Authentication required, input validated
- [ ] Deterministic: Responses consistent for same input (within reason)
- [ ] Full-stack coherence: Frontend/backend types match contracts
- [ ] Traceability: All changes documented in tasks.md
- [ ] AI agent statelessness: Agent doesn't store state, uses database
- [ ] MCP tool-first: Uses MCP tools for task operations, not direct DB access

---

## Validation Summary

### Quick Status Check

After completing all sections, verify:

**Backend (5 checks)**:
- [ ] Health endpoint responding
- [ ] Chat endpoint authenticated and functional
- [ ] MCP tools registered and working
- [ ] Database tables created and populated
- [ ] Error handling working

**Frontend (5 checks)**:
- [ ] Chat page accessible
- [ ] Responsive design working on all breakpoints
- [ ] Messages sending and receiving
- [ ] Conversation persistence across refreshes
- [ ] Error states displaying

**Integration (5 checks)**:
- [ ] Create task via chat works end-to-end
- [ ] List tasks via chat works
- [ ] Update task via chat works
- [ ] Delete task via chat works
- [ ] Conversation history persists across backend restart

### Final Acceptance Criteria

**ALL must pass for feature to be considered complete:**

1. ✅ User can create, list, update, and delete tasks via natural language chat
2. ✅ Agent responds with helpful, contextual messages
3. ✅ Conversation persists across page refreshes and backend restarts
4. ✅ All MCP tools (create, list, update, delete) function correctly
5. ✅ UI is responsive on mobile, tablet, and desktop
6. ✅ Authentication enforced on all chat endpoints
7. ✅ Error handling graceful for network, API, and tool errors
8. ✅ Database records all conversations, messages, and tool invocations
9. ✅ Performance acceptable (<5s response time, smooth UI)
10. ✅ Security measures in place (auth, input sanitization, API key protection)

---

## Next Steps After Validation

If validation passes:
- [ ] Mark T053 as complete in tasks.md
- [ ] Proceed to constitution compliance verification (T054)
- [ ] Prepare for demo or user acceptance testing

If validation fails:
- [ ] Document failures with screenshots/logs
- [ ] Create bug tickets for each issue
- [ ] Fix issues and re-run validation
- [ ] Update implementation documentation as needed

---

## Support Resources

- **Spec**: `specs/004-ai-chat-agent/spec.md`
- **Plan**: `specs/004-ai-chat-agent/plan.md`
- **Tasks**: `specs/004-ai-chat-agent/tasks.md`
- **Quickstart**: `specs/004-ai-chat-agent/QUICKSTART.md`
- **API Contract**: `specs/004-ai-chat-agent/contracts/chat-api.yaml`
- **MCP Tools**: `specs/004-ai-chat-agent/contracts/mcp-tools.json`

For issues:
1. Check backend logs: `uvicorn src.main:app --reload --log-level debug`
2. Check browser console for frontend errors
3. Review OpenAPI docs: `http://localhost:8000/docs`
4. Verify database state with SQL queries or Python scripts
