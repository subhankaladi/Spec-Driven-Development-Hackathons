# Quickstart: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Created**: 2026-01-19
**Prerequisites**: Phase-II backend and frontend running successfully

## Overview

This guide walks through setting up the AI Chat Agent feature for natural language todo management. You'll install dependencies, configure environment variables, run database migrations, and test the end-to-end chat flow.

**Expected Time**: 15-20 minutes

## Prerequisites

Before starting, ensure you have:

1. ✅ Phase-II backend running at http://localhost:8000
2. ✅ Phase-II frontend running at http://localhost:3000
3. ✅ Neon PostgreSQL database connected and accessible
4. ✅ User authentication working (can sign up/sign in)
5. ✅ Python 3.11+ and Node.js 18+ installed
6. ✅ OpenAI API account with API key

## Step 1: Install Backend Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend
pip install openai>=1.0.0  # OpenAI Agents SDK
pip install mcp-sdk>=0.1.0  # Official MCP SDK
```

**Verification**:
```bash
python -c "import openai; print(openai.__version__)"
python -c "import mcp; print('MCP SDK installed')"
```

Expected output: OpenAI version ≥1.0.0, MCP confirmation message

## Step 2: Configure Environment Variables

Add OpenAI API key to `backend/.env`:

```bash
# Existing Phase-II variables
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=your-secret-key
API_PORT=8000
DEBUG=true

# NEW: OpenAI configuration
OPENAI_API_KEY=sk-proj-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini    # Model for agent (or gpt-4o for better quality)
AGENT_MAX_TOKENS=1000       # Max tokens for agent response
```

**Get OpenAI API Key**:
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy and paste into `.env` file

**Verification**:
```bash
python -c "from src.config import settings; print(settings.openai_api_key[:10])"
```

Expected output: First 10 characters of your API key (e.g., `sk-proj-ab`)

## Step 3: Run Database Migrations

Create and apply migrations for new tables (Conversation, Message, ToolInvocation):

```bash
# Generate migration
alembic revision --autogenerate -m "Add conversation message toolinvocation tables"

# Review generated migration file (optional but recommended)
cat alembic/versions/[latest_version]_add_conversation_message_toolinvocation_tables.py

# Apply migration
alembic upgrade head
```

**Verification**:
```bash
# Check tables exist in database
python -c "
from src.models.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
assert 'conversation' in tables, 'Conversation table missing'
assert 'message' in tables, 'Message table missing'
assert 'toolinvocation' in tables or 'tool_invocation' in tables, 'ToolInvocation table missing'
print('✅ All tables created successfully')
"
```

Expected output: `✅ All tables created successfully`

## Step 4: Start Backend Server

Start or restart the FastAPI backend:

```bash
# From backend/ directory
uvicorn src.main:app --reload --port 8000
```

**Verification**:
```bash
# Health check
curl http://localhost:8000/health

# Check OpenAPI docs
open http://localhost:8000/docs
```

Expected output:
- Health check: `{"status":"healthy"}`
- Docs page should show new `/chat` endpoint

## Step 5: Install Frontend Dependencies (if needed)

Frontend chat components use existing dependencies (React, Next.js, Axios). No new packages required.

```bash
cd frontend
# Verify dependencies
npm list axios react react-dom
```

Expected output: Package versions for axios, react, react-dom

## Step 6: Start Frontend

Start or restart the Next.js frontend:

```bash
# From frontend/ directory
npm run dev
```

**Verification**:
```bash
open http://localhost:3000
```

Expected output: Landing page loads successfully

## Step 7: Test Chat Flow (Manual)

### 7.1 Sign In

1. Navigate to http://localhost:3000/signin
2. Sign in with existing account or create new account at /signup
3. Verify redirect to /tasks page

### 7.2 Access Chat Page

1. Navigate to http://localhost:3000/chat
2. Verify chat interface loads with empty conversation
3. Verify input field and send button are present

### 7.3 Send First Message

1. Type: "Create a task to buy milk"
2. Click Send button
3. Verify:
   - Loading state appears while processing
   - Agent response appears: "Task created: Buy milk" (or similar)
   - Message bubbles display correctly (user message + agent response)

### 7.4 Verify Task Created

1. Navigate to http://localhost:3000/tasks
2. Verify "Buy milk" task appears in task list
3. Return to http://localhost:3000/chat

### 7.5 Test List Tasks

1. Send message: "Show me my tasks"
2. Verify agent response lists tasks including "Buy milk"

### 7.6 Test Conversation Persistence

1. Close browser tab
2. Reopen http://localhost:3000/chat
3. Verify conversation history shows previous messages
4. Send new message: "Mark 'Buy milk' as complete"
5. Verify agent response confirms completion
6. Navigate to /tasks and verify task is marked complete

## Step 8: Test with cURL (Optional)

Test chat endpoint directly via API:

```bash
# First, get JWT token by signing in
TOKEN=$(curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "Create a task to buy groceries"
  }' | jq

# Expected response:
# {
#   "conversation_id": "uuid-here",
#   "message_id": "uuid-here",
#   "agent_response": "Task created: Buy groceries",
#   "tool_invocations": [
#     {
#       "tool_name": "create_task",
#       "success": true,
#       "result": "{\"id\":\"...\",\"title\":\"Buy groceries\"}"
#     }
#   ]
# }
```

## Step 9: Verify Database Records

Check that conversation data is persisted:

```bash
python -c "
from src.models.database import get_session
from src.models.conversation import Conversation
from src.models.message import Message

with next(get_session()) as session:
    conversations = session.query(Conversation).all()
    print(f'Conversations: {len(conversations)}')

    if conversations:
        conv = conversations[0]
        messages = session.query(Message).filter(Message.conversation_id == conv.id).all()
        print(f'Messages in first conversation: {len(messages)}')
        for msg in messages[:3]:
            print(f'  {msg.role}: {msg.content[:50]}...')
"
```

Expected output:
```
Conversations: 1
Messages in first conversation: 4
  user: Create a task to buy milk...
  agent: Task created: Buy milk...
  user: Show me my tasks...
  agent: You have 1 task:...
```

## Step 10: Test Stateless Operation (Backend Restart)

This test verifies that conversations resume correctly after backend restarts, demonstrating stateless operation with database persistence.

### Prerequisites
- Completed Steps 1-7 with at least one conversation containing 5+ messages
- Backend and frontend servers running

### Test Procedure

#### 10.1 Create a Conversation with Multiple Messages

1. Navigate to http://localhost:3000/chat
2. Send the following messages (wait for each response before sending the next):
   ```
   Message 1: "Create a task to buy milk"
   Message 2: "Create a task to read a book"
   Message 3: "List all my tasks"
   Message 4: "Mark 'buy milk' as complete"
   Message 5: "Show me incomplete tasks"
   ```
3. Verify all 5 messages and agent responses appear in the chat interface (total 10 messages)
4. Note the conversation ID (visible in browser DevTools localStorage: `chat_conversation_id`)

#### 10.2 Stop Backend Server

1. Open terminal where backend is running
2. Press `Ctrl+C` to stop the uvicorn server
3. Wait for graceful shutdown message

Expected output:
```
INFO:     Shutting down
INFO:     Finished server process
```

#### 10.3 Restart Backend Server

1. In the same terminal, restart the server:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```
2. Wait for startup complete message

Expected output:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 10.4 Verify Conversation Loads Correctly

1. Return to browser with chat page open (DO NOT refresh yet)
2. Refresh the page (F5 or Cmd+R)
3. Verify the following:
   - ✅ Loading spinner appears briefly while fetching history
   - ✅ All 10 messages (5 user + 5 agent) load in correct chronological order
   - ✅ Message content matches original conversation
   - ✅ No error messages appear
   - ✅ Auto-scroll positions view at the latest message

#### 10.5 Continue Conversation After Restart

1. Send a new message: "Delete the 'read a book' task"
2. Verify:
   - ✅ Message sends successfully
   - ✅ Agent response appears
   - ✅ New messages append to existing conversation history
   - ✅ Total message count is now 12 (6 user + 6 agent)

#### 10.6 Verify Database Persistence

1. In terminal, check database records match:
   ```bash
   python -c "
   from src.models.database import get_session
   from src.models.conversation import Conversation
   from src.models.message import Message
   from sqlmodel import select

   with next(get_session()) as session:
       # Get the conversation
       conv = session.exec(select(Conversation)).first()
       print(f'Conversation ID: {conv.id}')

       # Count messages
       messages = session.exec(
           select(Message)
           .where(Message.conversation_id == conv.id)
           .order_by(Message.created_at)
       ).all()

       print(f'Total messages in DB: {len(messages)}')
       print('\\nFirst 3 messages:')
       for msg in messages[:3]:
           print(f'  [{msg.role}] {msg.content[:50]}...')
   "
   ```

Expected output:
```
Conversation ID: <uuid>
Total messages in DB: 12
First 3 messages:
  [user] Create a task to buy milk...
  [agent] I've created a task to buy milk...
  [user] Create a task to read a book...
```

### Test Success Criteria

✅ **All criteria must pass:**

1. **History Loads**: All messages from before restart appear correctly
2. **Order Preserved**: Messages display in chronological order
3. **No Data Loss**: All message content matches original conversation
4. **Continuation Works**: New messages can be sent after restart
5. **Database Synced**: Database record count matches UI message count
6. **Auto-scroll**: View scrolls to latest message on load
7. **No Errors**: No console errors or API errors during entire flow

### What This Proves

This test demonstrates:

- **Stateless Backend**: Backend server doesn't store conversation state in memory; all state is in database
- **Frontend Persistence**: Frontend stores conversationId in localStorage for seamless user experience
- **Automatic Recovery**: Conversation resumes automatically without user intervention
- **Data Integrity**: All messages and conversation metadata persist correctly across restarts
- **Production Readiness**: Application can handle server restarts, deployments, and scaling without losing user data

## Troubleshooting

### Chat endpoint returns 500 error

**Cause**: OpenAI API key invalid or missing

**Solution**:
1. Check `.env` file has correct `OPENAI_API_KEY`
2. Verify key is active at https://platform.openai.com/api-keys
3. Restart backend server

### Agent doesn't create tasks

**Cause**: MCP tools not registered with agent

**Solution**:
1. Check logs for tool invocation errors
2. Verify `src/services/mcp_tools.py` implements all 4 tools
3. Verify agent service passes tools to OpenAI SDK

### Conversation history not loading

**Cause**: Database migration not applied or conversation query failing

**Solution**:
1. Run `alembic upgrade head` to ensure tables exist
2. Check backend logs for SQL errors
3. Verify user_id in JWT matches conversation user_id

### Frontend shows authentication error

**Cause**: JWT token expired or missing

**Solution**:
1. Sign out and sign in again to get fresh token
2. Check localStorage has `auth_token` key
3. Verify token is passed in Authorization header

## Next Steps

After successful setup:

1. ✅ Test all 4 MCP tools (create, list, update, delete)
2. ✅ Verify conversation persistence across page refreshes
3. ✅ Test edge cases (ambiguous commands, errors, timeouts)
4. ✅ Review agent responses for quality and accuracy
5. ⏭️ Proceed with additional user stories (P2-P4) implementation

## Reference

- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/chat-api.yaml](./contracts/chat-api.yaml)
- **MCP Tools**: [contracts/mcp-tools.json](./contracts/mcp-tools.json)

## Support

If you encounter issues not covered here:
1. Check backend logs: `uvicorn src.main:app --reload --log-level debug`
2. Check browser console for frontend errors
3. Review OpenAPI docs: http://localhost:8000/docs
4. Verify database connection and migrations
