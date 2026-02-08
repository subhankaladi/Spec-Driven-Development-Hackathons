// T025: ChatInterface component - Main chat interface container

'use client';

import React from 'react';
import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

/**
 * ChatInterface component integrates all chat functionality
 * - Uses useChat hook for state management
 * - Renders MessageList with current messages
 * - Renders MessageInput with send callback
 * - Shows loading spinner while processing
 * - Shows error alert if error occurs
 * - Auto-scroll to latest message via messagesEndRef
 * - Full height container with proper layout
 */
export function ChatInterface() {
  const { messages, loading, error, sendMessage, messagesEndRef } = useChat();

  return (
    <div className="flex flex-col h-full bg-background-dark rounded-xl border border-gray-800 shadow-xl overflow-hidden">
      {/* Error banner */}
      {error && (
        <div
          className="bg-danger-500 text-white px-4 py-3 flex items-start gap-3"
          role="alert"
          aria-live="assertive"
        >
          <svg
            className="w-5 h-5 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="flex-1">
            <p className="font-medium">Error</p>
            <p className="text-sm text-red-100 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Message list with scrollable content */}
      <MessageList messages={messages} messagesEndRef={messagesEndRef} />

      {/* Loading indicator */}
      {loading && (
        <div className="px-4 pb-2 flex items-center gap-2 text-gray-400">
          <div className="flex gap-1">
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: '0ms' }}
            />
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: '150ms' }}
            />
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: '300ms' }}
            />
          </div>
          <span className="text-sm">AI is thinking...</span>
        </div>
      )}

      {/* Message input */}
      <MessageInput onSendMessage={sendMessage} disabled={loading} />
    </div>
  );
}
