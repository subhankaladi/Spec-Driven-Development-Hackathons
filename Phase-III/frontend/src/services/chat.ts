/**
 * Chat Service
 *
 * API client for chat endpoints. Handles sending messages,
 * retrieving conversations, and managing chat history.
 */

import { http } from '@/utils/http';
import type {
  ChatRequest,
  ChatResponse,
  ConversationList,
  ConversationMessages,
  Message,
} from '@/types/chat';

/**
 * Transform backend snake_case response to frontend camelCase format
 */
function transformChatResponse(backendResponse: any): ChatResponse {
  const conversationId = backendResponse.conversationId || backendResponse.conversation_id;
  return {
    conversationId,
    userMessage: transformMessage(backendResponse.userMessage || backendResponse.user_message, conversationId),
    agentResponse: transformMessage(backendResponse.agentResponse || backendResponse.agent_response, conversationId),
  };
}

/**
 * Transform backend message format to frontend format
 */
function transformMessage(backendMessage: any, conversationId: string): Message {
  return {
    id: backendMessage.id,
    conversationId,
    role: backendMessage.role,
    content: backendMessage.content,
    toolCalls: backendMessage.toolCalls || backendMessage.tool_calls || undefined,
    createdAt: backendMessage.createdAt || backendMessage.created_at,
  };
}

/**
 * Send a message to the chat API
 * POST /api/chat
 */
export async function sendMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatResponse> {
  const request: ChatRequest = {
    message,
    conversationId: conversationId || null,
  };

  try {
    const response = await http.post<any>('/api/chat', request);
    console.log('Backend response:', response.data);
    const transformed = transformChatResponse(response.data);
    console.log('Transformed response:', transformed);
    return transformed;
  } catch (error) {
    console.error('Chat service error:', error);
    throw error;
  }
}

/**
 * Get list of user's conversations
 * GET /api/chat/conversations
 */
export async function getConversations(
  limit: number = 20,
  offset: number = 0
): Promise<ConversationList> {
  const response = await http.get<ConversationList>(
    `/api/chat/conversations?limit=${limit}&offset=${offset}`
  );
  return response.data;
}

/**
 * Get messages from a specific conversation
 * GET /api/chat/{conversation_id}
 */
export async function getConversation(
  conversationId: string,
  limit: number = 50,
  offset: number = 0
): Promise<ConversationMessages> {
  const response = await http.get<ConversationMessages>(
    `/api/chat/${conversationId}?limit=${limit}&offset=${offset}`
  );
  return response.data;
}

/**
 * ChatService object with all methods
 */
export const ChatService = {
  sendMessage,
  getConversations,
  getConversation,
};

export default ChatService;
