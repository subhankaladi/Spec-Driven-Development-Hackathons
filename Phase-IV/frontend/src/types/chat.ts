/**
 * Chat Types for ChatKit Frontend
 *
 * Defines TypeScript interfaces for chat messages, conversations,
 * and API responses used throughout the chat application.
 */

export type UUID = string;
export type DateTime = string; // ISO 8601 format

export type MessageRole = 'user' | 'assistant';
export type MessageStatus = 'sending' | 'sent' | 'failed';

export type ErrorCode =
  | 'NETWORK_ERROR'
  | 'AUTH_EXPIRED'
  | 'SERVER_ERROR'
  | 'VALIDATION_ERROR'
  | 'RATE_LIMITED'
  | 'UNAUTHORIZED'
  | 'NOT_FOUND';

/**
 * Tool call made by AI agent (e.g., add_task, list_tasks)
 */
export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result: Record<string, unknown>;
}

/**
 * Individual message in a conversation
 */
export interface Message {
  id: UUID;
  conversationId: UUID;
  role: MessageRole;
  content: string;
  status?: MessageStatus; // For optimistic UI
  toolCalls?: ToolCall[];
  createdAt: DateTime;
}

/**
 * Conversation entity with metadata
 */
export interface Conversation {
  id: UUID;
  title: string;
  createdAt: DateTime;
  updatedAt: DateTime;
  messageCount: number;
  lastMessage?: string;
}

/**
 * Response from POST /api/chat endpoint
 */
export interface ChatResponse {
  conversationId: UUID;
  userMessage: Message;
  agentResponse: Message;
}

/**
 * Request body for POST /api/chat endpoint
 */
export interface ChatRequest {
  conversationId?: UUID | null;
  message: string;
}

/**
 * Response from GET /api/chat/conversations endpoint
 */
export interface ConversationList {
  conversations: Conversation[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Response from GET /api/chat/{conversation_id} endpoint
 */
export interface ConversationMessages {
  conversationId: UUID;
  messages: Message[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * User-friendly error message with retry capability
 */
export interface ErrorMessage {
  code: ErrorCode;
  message: string;
  suggestion: string;
  retry?: () => void;
}

/**
 * State managed by useChat hook
 */
export interface ChatState {
  currentConversationId: UUID | null;
  messages: Message[];
  conversations: Conversation[];
  isLoading: boolean;
  error: ErrorMessage | null;
  isAuthenticated: boolean;
}
