// T012: Chat type definitions matching backend schemas

/**
 * Request schema for sending a chat message to the agent.
 * conversation_id is null to create a new conversation.
 */
export interface ChatRequest {
  conversationId: string | null;  // Optional conversation ID (null creates new conversation)
  message: string;                // User's message text (required, 1-5000 characters)
}

/**
 * Summary of a tool invocation during chat processing.
 */
export interface ToolInvocationSummary {
  toolName: string;               // Name of the invoked MCP tool
  success: boolean;               // Boolean indicating if tool invocation succeeded
  result: string | null;          // Optional string representation of the tool result
  error: string | null;           // Optional error message if invocation failed
}

/**
 * Response schema from agent after processing a chat message.
 */
export interface ChatResponse {
  conversationId: string;         // UUID of the conversation
  messageId: string;              // UUID of the agent's message
  agentResponse: string;          // Agent's text response to the user
  toolInvocations: ToolInvocationSummary[];  // List of tool invocations that occurred
}

/**
 * Individual message in a conversation.
 */
export interface Message {
  id: string;                     // Unique message identifier (UUID)
  conversationId: string;         // Parent conversation identifier (UUID)
  role: 'user' | 'agent';         // Message sender role
  content: string;                // Message text content
  createdAt: string;              // Creation timestamp (ISO 8601)
}

/**
 * Conversation metadata.
 */
export interface Conversation {
  id: string;                     // Unique conversation identifier (UUID)
  userId: string;                 // Owner user identifier (UUID)
  title: string | null;           // Optional conversation title
  createdAt: string;              // Creation timestamp (ISO 8601)
  updatedAt: string;              // Last update timestamp (ISO 8601)
}

/**
 * Response containing conversation history with messages.
 */
export interface ConversationHistoryResponse {
  conversation: Conversation;     // Conversation metadata
  messages: Message[];            // List of messages in chronological order
}

/**
 * Type alias for conversation history (used in API client)
 */
export type ConversationHistory = ConversationHistoryResponse;

/**
 * Response containing list of conversations.
 */
export interface ConversationListResponse {
  conversations: Conversation[];  // List of conversation metadata
  total: number;                  // Total number of conversations for the user
}
