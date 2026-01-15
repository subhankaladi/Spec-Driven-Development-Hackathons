/**
 * Type definitions for chat interface based on the data model
 */

// Represents a single message in the chat interface
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  status: 'sending' | 'sent' | 'error' | 'confirmed';
}

// Represents a logical grouping of messages for a user session
export interface Conversation {
  id: string;
  userId: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

// Configuration object for the ChatKit component
export interface ChatConfig {
  domain: string;
  backendUrl: string;
  jwtToken: string;
}

// Structure for responses from the backend API
export interface APIResponse {
  conversationId: string;
  assistantMessage: string;
  success: boolean;
  error?: {
    code: string;
    message: string;
  };
}

// Request payload for sending a message
export interface SendMessageRequest {
  message: string;
}

// Validation functions
export const isValidChatMessage = (message: any): message is ChatMessage => {
  return (
    typeof message.id === 'string' &&
    typeof message.content === 'string' &&
    (message.role === 'user' || message.role === 'assistant') &&
    message.timestamp instanceof Date &&
    ['sending', 'sent', 'error', 'confirmed'].includes(message.status)
  );
};

export const isValidConversation = (conversation: any): conversation is Conversation => {
  return (
    typeof conversation.id === 'string' &&
    typeof conversation.userId === 'string' &&
    Array.isArray(conversation.messages) &&
    conversation.createdAt instanceof Date &&
    conversation.updatedAt instanceof Date
  );
};