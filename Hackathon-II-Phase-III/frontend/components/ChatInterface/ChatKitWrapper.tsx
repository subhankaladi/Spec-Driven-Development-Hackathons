/**
 * ChatKit wrapper component
 * Integrates OpenAI ChatKit with our authentication and API service
 */

import React, { useState, useEffect } from 'react';
import { Chat, type ChatProps } from '@openai/chatkit-react';
import { JWTHandler } from '../Auth/JWTHandler';
import { sendMessage } from '../../services/chatService';
import { addMessageToConversation } from '../utils/apiClient';
import { ChatMessage } from '../../types/chatTypes';

interface ChatKitWrapperProps {
  userId: string;
  domainAllowlist?: string[];
}

const ChatKitWrapper: React.FC<ChatKitWrapperProps> = ({ userId, domainAllowlist = [] }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Validate required environment variables on component mount
  useEffect(() => {
    // Check for required environment variables
    const backendUrl = process.env.VITE_BACKEND_URL;
    const chatKitDomain = process.env.VITE_CHATKIT_DOMAIN;

    if (!backendUrl) {
      console.error('[ChatKitWrapper] Missing required environment variable: VITE_BACKEND_URL');
      setError('Configuration error: Missing backend URL. Please set VITE_BACKEND_URL in environment variables.');
      return;
    }

    if (!chatKitDomain) {
      console.error('[ChatKitWrapper] Missing required environment variable: VITE_CHATKIT_DOMAIN');
      setError('Configuration error: Missing ChatKit domain. Please set VITE_CHATKIT_DOMAIN in environment variables.');
      return;
    }

    // Validate domain allowlist
    const currentDomain = window.location.hostname;
    if (domainAllowlist.length > 0 && !domainAllowlist.includes(currentDomain)) {
      setError(`Domain ${currentDomain} is not allowlisted for this application`);
      return;
    }

    // Check if JWT token is valid
    if (!JWTHandler.isValidToken()) {
      setError('No valid JWT token found. Please authenticate.');
      return;
    }
  }, [domainAllowlist]);

  const handleSendMessage = async (input: string) => {
    if (!JWTHandler.isValidToken()) {
      setError('No valid JWT token found. Please authenticate.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        content: input,
        role: 'user',
        timestamp: new Date(),
        status: 'sending',
      };

      setMessages(prev => [...prev, userMessage]);

      // Send message to backend
      const token = JWTHandler.getToken();
      if (!token) {
        throw new Error('No JWT token available');
      }

      const userIdFromToken = JWTHandler.getUserIdFromToken(token);
      if (!userIdFromToken || userIdFromToken !== userId) {
        throw new Error('User ID mismatch between token and request');
      }

      const response = await sendMessage(userId, { message: input });

      if (response.success) {
        // Add assistant response to messages
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
          content: response.assistantMessage,
          role: 'assistant',
          timestamp: new Date(),
          status: 'confirmed',
        };

        setMessages(prev => {
          // Update the user message status to confirmed and add assistant response
          const updatedPrev = prev.map(msg =>
            msg.id === userMessage.id ? { ...msg, status: 'confirmed' } : msg
          );
          return [...updatedPrev, assistantMessage];
        });

        // Store both messages in history
        addMessageToConversation(userId, userMessage);
        addMessageToConversation(userId, assistantMessage);
      } else {
        // Update user message status to error
        setMessages(prev =>
          prev.map(msg =>
            msg.id === userMessage.id ? { ...msg, status: 'error' } : msg
          )
        );

        throw new Error(response.error?.message || 'Failed to get response from backend');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Configuration for ChatKit
  const chatConfig: Partial<ChatProps> = {
    // We won't use OpenAI's backend for AI processing as per requirements
    // All AI processing happens via our backend API
    onSend: (input: string) => {
      handleSendMessage(input);
    },
    // Customize the appearance and behavior as needed
    className: 'chat-kit-wrapper',
    placeholder: 'Type your task or question here...',
    disabled: isLoading || !!error,
  };

  // Filter out any AI/business logic from frontend as required
  // The frontend only handles UI and routes requests to backend

  return (
    <div className="chat-container">
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      <Chat
        {...chatConfig}
        messages={messages.map(msg => ({
          id: msg.id,
          content: msg.content,
          role: msg.role,
          createdAt: msg.timestamp,
        }))}
      />

      {isLoading && (
        <div className="loading-indicator">
          Assistant is thinking...
        </div>
      )}
    </div>
  );
};

export default ChatKitWrapper;