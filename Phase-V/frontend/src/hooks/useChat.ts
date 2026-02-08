// T021: Custom React hook for chat functionality

import { useState, useEffect, useRef } from 'react';
import { Message } from '@/types/chat';
import {
  sendMessage as sendMessageAPI,
  getConversationHistory,
} from '@/lib/api/chat';

interface UseChatReturn {
  messages: Message[];
  loading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (content: string) => Promise<void>;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

const CONVERSATION_ID_KEY = 'chat_conversation_id';

/**
 * Custom hook for managing chat state and interactions
 * - Loads conversationId from localStorage on mount
 * - Loads conversation history if conversationId exists
 * - Persists conversationId to localStorage when created
 * @returns Chat state and functions for sending messages
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [historyLoaded, setHistoryLoaded] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Load conversationId from localStorage on mount and fetch history
   * T033: Conversation history loading on chat page mount
   * T035: Conversation ID persistence with localStorage
   */
  useEffect(() => {
    const loadConversationHistory = async () => {
      try {
        // Load conversationId from localStorage
        const storedConversationId = localStorage.getItem(CONVERSATION_ID_KEY);

        if (storedConversationId) {
          setConversationId(storedConversationId);
          setLoading(true);

          // Fetch conversation history from backend
          const history = await getConversationHistory(storedConversationId);

          // Set messages from history
          setMessages(history.messages);
          setHistoryLoaded(true);
        } else {
          // No stored conversation, mark as loaded
          setHistoryLoaded(true);
        }
      } catch (err: any) {
        console.error('Failed to load conversation history:', err);
        // Clear invalid conversationId from localStorage
        localStorage.removeItem(CONVERSATION_ID_KEY);
        setConversationId(null);
        setError('Failed to load conversation history. Starting a new conversation.');
        setHistoryLoaded(true);
      } finally {
        setLoading(false);
      }
    };

    loadConversationHistory();
  }, []); // Run once on mount

  /**
   * Auto-scroll to the latest message when messages update
   * T036: Auto-scroll to latest message
   */
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Send a message to the AI agent
   * @param content - Message text to send
   */
  const sendMessage = async (content: string): Promise<void> => {
    if (!content.trim()) {
      setError('Message cannot be empty');
      return;
    }

    // Clear any previous errors
    setError(null);
    setLoading(true);

    // Generate a unique temporary ID using timestamp and random number
    const tempId = `temp-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    // Add user message to UI immediately for better UX
    const userMessage: Message = {
      id: tempId, // Temporary unique ID
      conversationId: conversationId || 'temp',
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send message to API
      const response = await sendMessageAPI(conversationId, content.trim());

      // Update conversation ID if this is the first message
      // T035: Persist conversationId to localStorage
      if (!conversationId) {
        setConversationId(response.conversationId);
        localStorage.setItem(CONVERSATION_ID_KEY, response.conversationId);
      }

      // Add agent response to messages
      const agentMessage: Message = {
        id: response.messageId,
        conversationId: response.conversationId,
        role: 'agent',
        content: response.agentResponse,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');

      // Remove the optimistically added user message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    error,
    conversationId,
    sendMessage,
    messagesEndRef,
  };
}
