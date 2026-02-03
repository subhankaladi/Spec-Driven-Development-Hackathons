/**
 * useChat Hook
 *
 * Custom React hook for managing chat state, messages, and conversations.
 * Handles sending messages, optimistic UI, error handling, and retry logic.
 */

'use client';

import { useState, useCallback } from 'react';
import type { Message, Conversation, ErrorMessage, UUID } from '@/types/chat';
import { ChatService } from '@/services/chat';
import { mapErrorToUserMessage, isAuthError } from '@/utils/errors';

export interface UseChatReturn {
  // State
  messages: Message[];
  conversations: Conversation[];
  currentConversationId: UUID | null;
  isLoading: boolean;
  error: ErrorMessage | null;
  needsReAuth: boolean;
  conversationsHasMore: boolean;
  messagesHasMore: boolean;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  loadConversations: (loadMore?: boolean) => Promise<void>;
  loadConversation: (conversationId: UUID, loadMore?: boolean) => Promise<void>;
  retryMessage: (messageId: UUID) => Promise<void>;
  clearError: () => void;
  setCurrentConversation: (conversationId: UUID | null) => void;
  handleReAuthenticated: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<UUID | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ErrorMessage | null>(null);
  const [needsReAuth, setNeedsReAuth] = useState(false);

  // Pagination state
  const [conversationsHasMore, setConversationsHasMore] = useState(true);
  const [messagesHasMore, setMessagesHasMore] = useState(true);

  /**
   * Send a message to the chat API
   * Implements optimistic UI: shows message immediately before backend response
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      setIsLoading(true);
      setError(null);

      // Create optimistic user message
      const optimisticMessage: Message = {
        id: `temp-${Date.now()}`,
        conversationId: currentConversationId || 'temp',
        role: 'user',
        content,
        status: 'sending',
        createdAt: new Date().toISOString(),
      };

      // Add optimistic message to UI immediately
      setMessages((prev) => [...prev, optimisticMessage]);

      try {
        // Send to backend
        const response = await ChatService.sendMessage(content, currentConversationId);

        // Update conversation ID if this was a new conversation
        if (!currentConversationId) {
          setCurrentConversationId(response.conversationId);
        }

        // Replace optimistic message with real messages from backend
        setMessages((prev) => {
          const withoutOptimistic = prev.filter((m) => m.id !== optimisticMessage.id);
          return [
            ...withoutOptimistic,
            { ...response.userMessage, status: 'sent' },
            { ...response.agentResponse, status: 'sent' },
          ];
        });
      } catch (err) {
        // Check if this is an authentication error
        if (isAuthError(err)) {
          setNeedsReAuth(true);
          // Don't mark message as failed - it will be retried after re-auth
        } else {
          // Mark message as failed for non-auth errors
          setMessages((prev) =>
            prev.map((m) =>
              m.id === optimisticMessage.id ? { ...m, status: 'failed' as const } : m
            )
          );
        }

        // Create retry function
        const retry = () => retryMessage(optimisticMessage.id);

        // Set user-friendly error
        setError(mapErrorToUserMessage(err, retry));
      } finally {
        setIsLoading(false);
      }
    },
    [currentConversationId]
  );

  /**
   * Load list of conversations
   */
  const loadConversations = useCallback(async (loadMore = false) => {
    try {
      const offset = loadMore ? conversations.length : 0;
      const response = await ChatService.getConversations(20, offset);

      if (loadMore) {
        setConversations((prev) => [...prev, ...response.conversations]);
      } else {
        setConversations(response.conversations);
      }

      // Check if there are more conversations to load
      setConversationsHasMore(response.conversations.length === 20);
    } catch (err) {
      if (isAuthError(err)) {
        setNeedsReAuth(true);
      }
      setError(mapErrorToUserMessage(err));
    }
  }, [conversations.length]);

  /**
   * Load messages from a specific conversation
   */
  const loadConversation = useCallback(async (conversationId: UUID, loadMore = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const offset = loadMore ? messages.length : 0;
      const response = await ChatService.getConversation(conversationId, 50, offset);

      const newMessages = response.messages.map((m) => ({ ...m, status: 'sent' as const }));

      if (loadMore) {
        // Prepend older messages to the beginning of the array
        setMessages((prev) => [...newMessages, ...prev]);
      } else {
        setMessages(newMessages);
      }

      setCurrentConversationId(conversationId);

      // Check if there are more messages to load
      setMessagesHasMore(response.messages.length === 50);
    } catch (err) {
      if (isAuthError(err)) {
        setNeedsReAuth(true);
      }
      setError(mapErrorToUserMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [messages.length]);

  /**
   * Retry a failed message
   */
  const retryMessage = useCallback(
    async (messageId: UUID) => {
      const failedMessage = messages.find((m) => m.id === messageId);
      if (!failedMessage) return;

      // Remove failed message
      setMessages((prev) => prev.filter((m) => m.id !== messageId));

      // Resend with original content
      await sendMessage(failedMessage.content);
    },
    [messages, sendMessage]
  );

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Set current conversation
   */
  const setCurrentConversation = useCallback((conversationId: UUID | null) => {
    setCurrentConversationId(conversationId);
    if (!conversationId) {
      setMessages([]); // Clear messages when starting new conversation
    }
  }, []);

  /**
   * Handle successful re-authentication
   * Clears the needsReAuth flag and error state
   */
  const handleReAuthenticated = useCallback(() => {
    setNeedsReAuth(false);
    setError(null);
  }, []);

  return {
    messages,
    conversations,
    currentConversationId,
    isLoading,
    error,
    needsReAuth,
    conversationsHasMore,
    messagesHasMore,
    sendMessage,
    loadConversations,
    loadConversation,
    retryMessage,
    clearError,
    setCurrentConversation,
    handleReAuthenticated,
  };
}
