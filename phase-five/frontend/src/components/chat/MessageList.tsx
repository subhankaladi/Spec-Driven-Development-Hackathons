// T023: MessageList component for displaying chat message history

import React from 'react';
import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: Message[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

/**
 * MessageList component displays a scrollable list of chat messages
 * - Maps over messages and renders MessageBubble for each
 * - Scrollable container with max height for proper layout
 * - Empty state when no messages exist
 * - Auto-scroll support via messagesEndRef
 */
export function MessageList({ messages, messagesEndRef }: MessageListProps) {
  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-6 space-y-2"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      {messages.length === 0 ? (
        // Empty state
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg
                className="w-16 h-16 mx-auto mb-4 opacity-50"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <p className="text-lg font-medium text-gray-300 mb-1">
              No messages yet
            </p>
            <p className="text-sm text-gray-500">
              Start a conversation with the AI assistant
            </p>
          </div>
        </div>
      ) : (
        // Message list
        <>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {/* Invisible div for auto-scroll targeting */}
          <div ref={messagesEndRef} aria-hidden="true" />
        </>
      )}
    </div>
  );
}
