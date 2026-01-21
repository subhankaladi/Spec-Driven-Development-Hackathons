/**
 * MessageBubble Component
 *
 * Displays a single message in the chat interface.
 * Shows user/agent distinction, message status, and confirmation indicators.
 */

'use client';

import type { Message } from '@/types/chat';
import { InlineLoadingSpinner } from './LoadingIndicator';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isAgent = message.role === 'assistant';
  const isSending = message.status === 'sending';
  const isSent = message.status === 'sent';
  const isFailed = message.status === 'failed';

  // Check if message contains confirmation indicator (✓ or checkmark)
  const hasConfirmation = /^✓|completed|created|updated|deleted|done/i.test(message.content);

  // Base styles - Dark theme
  const bubbleClasses = [
    'px-4 py-3 rounded-2xl max-w-[80%] break-words transition-all duration-300',
    isUser && !isFailed && 'bg-gradient-to-br from-blue-600 to-blue-700 text-white ml-auto shadow-lg shadow-blue-500/20',
    isUser && isSent && 'shadow-xl shadow-blue-500/30',
    isAgent && 'bg-gray-800/80 backdrop-blur-sm text-gray-100 border border-gray-700/50',
    hasConfirmation && isAgent && 'bg-green-900/30 border border-green-600/50 shadow-lg shadow-green-500/10',
    isSending && 'opacity-70 animate-pulse',
    isFailed && 'opacity-70 border-2 border-red-500/50 bg-red-900/20 text-red-200',
  ]
    .filter(Boolean)
    .join(' ');

  const containerClasses = ['flex', isUser ? 'justify-end' : 'justify-start'].join(' ');

  return (
    <div className={containerClasses}>
      <div className={bubbleClasses}>
        {/* Message content */}
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Status indicators */}
        <div className="flex items-center gap-2 mt-1.5 text-xs opacity-80">
          {/* Sending status with spinner */}
          {isSending && (
            <span className="flex items-center gap-1.5">
              <InlineLoadingSpinner className="text-current" />
              <span>Sending...</span>
            </span>
          )}

          {/* Sent status with checkmark */}
          {isSent && isUser && (
            <span className="flex items-center gap-1" title="Delivered">
              <svg
                className="h-3 w-3 text-current"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                  clipRule="evenodd"
                />
              </svg>
            </span>
          )}

          {/* Failed status with error icon */}
          {isFailed && (
            <span className="flex items-center gap-1.5 text-red-600 font-medium">
              <svg
                className="h-3 w-3"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Failed to send</span>
            </span>
          )}

          {/* Timestamp */}
          {!isSending && (
            <span className="text-xs">
              {new Date(message.createdAt).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}
        </div>

        {/* Tool calls indicator (for debugging) */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 text-xs opacity-50">
            {message.toolCalls.map((tool, idx) => (
              <div key={idx}>🔧 {tool.tool}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
