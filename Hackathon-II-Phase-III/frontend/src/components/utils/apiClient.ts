/**
 * API client utility for managing conversation state
 * Handles temporary storage and retrieval of conversation data during session
 */

import { ChatMessage, Conversation } from '../../types/chatTypes';

const CONVERSATION_STORAGE_KEY = 'temp_conversation_state';

/**
 * Store conversation state temporarily during session
 */
export function storeTemporaryConversation(conversation: Conversation): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(conversation));
  }
}

/**
 * Retrieve conversation state from temporary storage
 */
export function getTemporaryConversation(): Conversation | null {
  if (typeof window !== 'undefined') {
    const stored = sessionStorage.getItem(CONVERSATION_STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored, (key, value) => {
          // Convert date strings back to Date objects
          if (key === 'timestamp' || key === 'createdAt' || key === 'updatedAt') {
            return new Date(value);
          }
          return value;
        });
      } catch (error) {
        console.error('Failed to parse conversation from storage:', error);
        return null;
      }
    }
  }
  return null;
}

/**
 * Clear temporary conversation storage
 */
export function clearTemporaryConversation(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(CONVERSATION_STORAGE_KEY);
  }
}

/**
 * Store conversation history in local storage for persistence across page refreshes
 */
export function storeConversationHistory(userId: string, conversation: Conversation): void {
  if (typeof window !== 'undefined') {
    const key = `conversation_history_${userId}`;
    localStorage.setItem(key, JSON.stringify(conversation));
  }
}

/**
 * Retrieve conversation history from local storage
 */
export function getConversationHistory(userId: string): Conversation | null {
  if (typeof window !== 'undefined') {
    const key = `conversation_history_${userId}`;
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        return JSON.parse(stored, (key, value) => {
          // Convert date strings back to Date objects
          if (key === 'timestamp' || key === 'createdAt' || key === 'updatedAt') {
            return new Date(value);
          }
          return value;
        });
      } catch (error) {
        console.error('Failed to parse conversation history from storage:', error);
        return null;
      }
    }
  }
  return null;
}

/**
 * Add a message to the conversation in storage
 */
export function addMessageToConversation(userId: string, message: ChatMessage): void {
  if (typeof window !== 'undefined') {
    const existingConversation = getConversationHistory(userId);
    if (existingConversation) {
      const updatedMessages = [...existingConversation.messages, message];
      const updatedConversation: Conversation = {
        ...existingConversation,
        messages: updatedMessages,
        updatedAt: new Date(),
      };
      storeConversationHistory(userId, updatedConversation);
    } else {
      // Create a new conversation if none exists
      const newConversation: Conversation = {
        id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        userId,
        messages: [message],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      storeConversationHistory(userId, newConversation);
    }
  }
}

/**
 * Clear conversation history for a user
 */
export function clearConversationHistory(userId: string): void {
  if (typeof window !== 'undefined') {
    const key = `conversation_history_${userId}`;
    localStorage.removeItem(key);
  }
}

/**
 * Get recent messages for a user
 */
export function getRecentMessages(userId: string, limit: number = 10): ChatMessage[] {
  const conversation = getConversationHistory(userId);
  if (conversation && conversation.messages) {
    return conversation.messages.slice(-limit);
  }
  return [];
}