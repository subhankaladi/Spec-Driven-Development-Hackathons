// T020: Chat API client for communication with backend chat endpoint

import apiClient from './client';
import { ChatRequest, ChatResponse, ConversationHistory } from '@/types/chat';

/**
 * Send a chat message to the AI agent
 * @param conversationId - Existing conversation ID or null to create a new conversation
 * @param message - User's message text (1-5000 characters)
 * @returns ChatResponse with agent's response and conversation ID
 * @throws Error if API call fails or returns an error
 */
export async function sendMessage(
  conversationId: string | null,
  message: string
): Promise<ChatResponse> {
  try {
    const requestBody: ChatRequest = {
      conversationId,
      message,
    };

    const response = await apiClient.post<ChatResponse>('/chat', requestBody);
    return response.data;
  } catch (error: any) {
    // Error handling is already done by apiClient interceptor
    // Re-throw with a more specific message if needed
    const errorMessage = error.message || 'Failed to send message';
    throw new Error(errorMessage);
  }
}

/**
 * Get conversation history with all messages
 * @param conversationId - UUID of the conversation to retrieve
 * @returns ConversationHistory with conversation metadata and all messages
 * @throws Error if API call fails or conversation doesn't exist
 */
export async function getConversationHistory(
  conversationId: string
): Promise<ConversationHistory> {
  try {
    const response = await apiClient.get<ConversationHistory>(
      `/chat/${conversationId}`
    );
    return response.data;
  } catch (error: any) {
    // Error handling is already done by apiClient interceptor
    const errorMessage = error.message || 'Failed to load conversation history';
    throw new Error(errorMessage);
  }
}
