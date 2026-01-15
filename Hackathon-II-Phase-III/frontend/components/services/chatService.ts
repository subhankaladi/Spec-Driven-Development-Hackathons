/**
 * API client service for chat interface
 * Handles communication with the backend API with JWT authentication
 */

import { JWTHandler } from '../components/Auth/JWTHandler';
import { SendMessageRequest, APIResponse } from '../types/chatTypes';

const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:8000';

/**
 * Send a message to the backend API
 */
export async function sendMessage(userId: string, request: SendMessageRequest): Promise<APIResponse> {
  // Log the outgoing request
  console.log('[ChatService] Sending message:', {
    userId,
    message: request.message,
    timestamp: new Date().toISOString()
  });

  try {
    const url = `${BACKEND_URL}/api/v1/${userId}/chat`;

    const startTime = Date.now();
    const response = await fetch(url, {
      method: 'POST',
      ...JWTHandler.attachTokenToRequest(),
      body: JSON.stringify(request),
    });
    const endTime = Date.now();
    const duration = endTime - startTime;

    // Log response details
    console.log('[ChatService] Response received:', {
      status: response.status,
      duration_ms: duration,
      url: url,
      timestamp: new Date().toISOString()
    });

    // Handle different response statuses
    if (response.status === 401) {
      console.warn('[ChatService] Unauthorized access attempt:', { userId, url });
      throw new Error('Unauthorized: Invalid or missing JWT token');
    }

    if (response.status === 403) {
      console.warn('[ChatService] Forbidden access attempt:', { userId, url });
      throw new Error('Forbidden: User ID in token does not match request');
    }

    if (response.status === 500) {
      console.error('[ChatService] Internal server error:', { userId, url });
      throw new Error('Internal server error');
    }

    const data: APIResponse = await response.json();

    // Log successful response
    console.log('[ChatService] Message sent successfully:', {
      userId,
      conversationId: data.conversationId,
      responseLength: data.assistantMessage.length,
      timestamp: new Date().toISOString()
    });

    return {
      conversationId: data.conversationId,
      assistantMessage: data.assistantMessage,
      success: response.ok,
    };
  } catch (error) {
    console.error('[ChatService] Error sending message:', {
      userId,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    });

    return {
      conversationId: '',
      assistantMessage: '',
      success: false,
      error: {
        code: 'NETWORK_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
      },
    };
  }
}

/**
 * Get user's conversation history (if available in backend API)
 */
export async function getConversationHistory(userId: string, conversationId: string): Promise<any> {
  console.log('[ChatService] Fetching conversation history:', {
    userId,
    conversationId,
    timestamp: new Date().toISOString()
  });

  try {
    const url = `${BACKEND_URL}/api/v1/${userId}/conversations/${conversationId}`;

    const startTime = Date.now();
    const response = await fetch(url, {
      method: 'GET',
      ...JWTHandler.attachTokenToRequest(),
    });
    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log('[ChatService] Conversation history response:', {
      status: response.status,
      duration_ms: duration,
      url: url,
      timestamp: new Date().toISOString()
    });

    if (response.status === 401) {
      console.warn('[ChatService] Unauthorized access attempt to conversation history:', { userId, conversationId, url });
      throw new Error('Unauthorized: Invalid or missing JWT token');
    }

    if (response.status === 403) {
      console.warn('[ChatService] Forbidden access attempt to conversation history:', { userId, conversationId, url });
      throw new Error('Forbidden: User ID in token does not match request');
    }

    if (!response.ok) {
      console.error('[ChatService] Failed to fetch conversation history:', { status: response.status, url });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    console.log('[ChatService] Conversation history fetched successfully:', {
      userId,
      conversationId,
      messageCount: Array.isArray(data.messages) ? data.messages.length : 'unknown',
      timestamp: new Date().toISOString()
    });

    return data;
  } catch (error) {
    console.error('[ChatService] Error getting conversation history:', {
      userId,
      conversationId,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    });
    throw error;
  }
}

/**
 * Validate the API endpoint is accessible
 */
export async function validateAPIConnection(): Promise<boolean> {
  console.log('[ChatService] Validating API connection:', {
    url: `${BACKEND_URL}/health`,
    timestamp: new Date().toISOString()
  });

  try {
    const url = `${BACKEND_URL}/health`;
    const startTime = Date.now();
    const response = await fetch(url);
    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log('[ChatService] API connection validation result:', {
      url: url,
      status: response.status,
      duration_ms: duration,
      success: response.ok,
      timestamp: new Date().toISOString()
    });

    return response.ok;
  } catch (error) {
    console.error('[ChatService] API connection validation failed:', {
      url: `${BACKEND_URL}/health`,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    });
    return false;
  }
}

/**
 * Type guard to check if response matches APIResponse interface
 */
export function isAPIResponse(data: any): data is APIResponse {
  return (
    typeof data === 'object' &&
    typeof data.conversationId === 'string' &&
    typeof data.assistantMessage === 'string' &&
    typeof data.success === 'boolean'
  );
}