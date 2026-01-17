/**
 * Test Fixtures for Chat Feature
 *
 * Mock data for chat messages, conversations, and API responses
 * used in unit and integration tests.
 */

import type {
  Message,
  Conversation,
  ChatResponse,
  ConversationList,
  ConversationMessages,
  ToolCall,
} from '@/types/chat';

export const mockToolCall: ToolCall = {
  tool: 'add_task',
  parameters: { title: 'Buy groceries' },
  result: { task_id: 'task-123', status: 'created' },
};

export const mockUserMessage: Message = {
  id: 'msg-001',
  conversationId: 'conv-001',
  role: 'user',
  content: 'Add a task to buy groceries',
  status: 'sent',
  createdAt: '2026-01-17T10:30:00Z',
};

export const mockAgentMessage: Message = {
  id: 'msg-002',
  conversationId: 'conv-001',
  role: 'assistant',
  content: '✓ I\'ve added a new task: Buy groceries',
  toolCalls: [mockToolCall],
  status: 'sent',
  createdAt: '2026-01-17T10:30:02Z',
};

export const mockConversation: Conversation = {
  id: 'conv-001',
  title: 'Shopping list planning',
  createdAt: '2026-01-16T15:00:00Z',
  updatedAt: '2026-01-17T09:45:00Z',
  messageCount: 12,
  lastMessage: 'Done! I\'ve updated your shopping list.',
};

export const mockChatResponse: ChatResponse = {
  conversationId: 'conv-001',
  userMessage: mockUserMessage,
  agentResponse: mockAgentMessage,
};

export const mockConversationList: ConversationList = {
  conversations: [
    mockConversation,
    {
      id: 'conv-002',
      title: 'Work tasks review',
      createdAt: '2026-01-15T09:00:00Z',
      updatedAt: '2026-01-16T14:30:00Z',
      messageCount: 8,
      lastMessage: 'All set! Your work tasks are updated.',
    },
    {
      id: 'conv-003',
      title: 'Planning weekend',
      createdAt: '2026-01-14T18:00:00Z',
      updatedAt: '2026-01-15T10:00:00Z',
      messageCount: 5,
      lastMessage: 'Great! I\'ve added those to your weekend plans.',
    },
  ],
  total: 3,
  limit: 20,
  offset: 0,
};

export const mockConversationMessages: ConversationMessages = {
  conversationId: 'conv-001',
  messages: [
    {
      id: 'msg-001',
      conversationId: 'conv-001',
      role: 'user',
      content: 'Show me my tasks',
      status: 'sent',
      createdAt: '2026-01-17T09:00:00Z',
    },
    {
      id: 'msg-002',
      conversationId: 'conv-001',
      role: 'assistant',
      content: 'Here are your tasks: 1. Buy milk, 2. Review proposal',
      toolCalls: [
        {
          tool: 'list_tasks',
          parameters: {},
          result: {
            tasks: [
              { id: 'task-1', title: 'Buy milk' },
              { id: 'task-2', title: 'Review proposal' },
            ],
          },
        },
      ],
      status: 'sent',
      createdAt: '2026-01-17T09:00:02Z',
    },
    mockUserMessage,
    mockAgentMessage,
  ],
  total: 4,
  limit: 50,
  offset: 0,
};

export const mockErrorResponse = {
  error: 'RATE_LIMITED',
  message: 'Rate limit exceeded: 10 requests per minute',
  details: {
    reset_after_seconds: 45,
  },
};

export const mockAuthExpiredError = {
  error: 'UNAUTHORIZED',
  message: 'JWT token expired. Please re-authenticate.',
  details: {},
};

export const mockNetworkError = new Error('Network request failed');

export const mockHTTPError = {
  message: 'Server error',
  status: 500,
  code: 'SERVER_ERROR',
} as any;
