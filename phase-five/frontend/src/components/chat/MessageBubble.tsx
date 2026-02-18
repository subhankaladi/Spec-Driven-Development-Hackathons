// T022: MessageBubble component for displaying individual chat messages

import React from 'react';
import { Message } from '@/types/chat';

interface MessageBubbleProps {
  message: Message;
}

/**
 * MessageBubble component displays a single chat message with role-based styling
 * - User messages: right-aligned with blue background
 * - Agent messages: left-aligned with gray background
 * - Includes timestamp in small text
 * - Fully responsive design
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  // Format timestamp to readable format
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();

    if (isToday) {
      // Show time only for today's messages
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } else {
      // Show date and time for older messages
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    }
  };

  return (
    <div
      className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Agent'} message`}
    >
      <div
        className={`
          max-w-[85%] sm:max-w-[75%] md:max-w-[65%] lg:max-w-[60%]
          px-4 py-3 rounded-2xl shadow-md
          ${
            isUser
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-gray-200 text-gray-900 rounded-bl-md'
          }
        `}
      >
        {/* Message content */}
        <p className="text-sm sm:text-base whitespace-pre-wrap break-words">
          {message.content}
        </p>

        {/* Timestamp */}
        <time
          className={`
            block mt-1.5 text-xs
            ${isUser ? 'text-blue-100' : 'text-gray-500'}
          `}
          dateTime={message.createdAt}
        >
          {formatTimestamp(message.createdAt)}
        </time>
      </div>
    </div>
  );
}
