/**
 * ConversationItem Component
 *
 * Displays a single conversation item in the conversation list sidebar.
 * Shows conversation title, last message preview, and timestamp.
 */

'use client';

import React from 'react';
import type { Conversation } from '@/types/chat';

export interface ConversationItemProps {
  /** Conversation data to display */
  conversation: Conversation;
  /** Whether this conversation is currently active/selected */
  isActive?: boolean;
  /** Click handler when conversation is selected */
  onClick?: () => void;
}

/**
 * ConversationItem displays a single conversation in the sidebar
 *
 * @example
 * <ConversationItem
 *   conversation={conversation}
 *   isActive={currentId === conversation.id}
 *   onClick={() => selectConversation(conversation.id)}
 * />
 */
export function ConversationItem({
  conversation,
  isActive = false,
  onClick,
}: ConversationItemProps) {
  // Format timestamp
  const formatTimestamp = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
    });
  };

  // Truncate text to max length
  const truncate = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left px-4 py-3 rounded-lg transition-colors
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${
          isActive
            ? 'bg-blue-50 border-l-4 border-blue-600'
            : 'hover:bg-gray-50 border-l-4 border-transparent'
        }
      `}
      aria-label={`Conversation: ${conversation.title}`}
      aria-current={isActive ? 'page' : undefined}
    >
      {/* Conversation title */}
      <div className="flex items-start justify-between gap-2 mb-1">
        <h3
          className={`
            font-medium text-sm truncate flex-1
            ${isActive ? 'text-blue-900' : 'text-gray-900'}
          `}
        >
          {truncate(conversation.title, 40)}
        </h3>

        {/* Timestamp */}
        <span
          className={`
            text-xs flex-shrink-0
            ${isActive ? 'text-blue-700' : 'text-gray-500'}
          `}
        >
          {formatTimestamp(conversation.updatedAt)}
        </span>
      </div>

      {/* Last message preview */}
      {conversation.lastMessage && (
        <p
          className={`
            text-xs truncate
            ${isActive ? 'text-blue-700' : 'text-gray-600'}
          `}
        >
          {truncate(conversation.lastMessage, 60)}
        </p>
      )}

      {/* Message count indicator */}
      <div className="flex items-center gap-2 mt-1.5">
        <span
          className={`
            text-xs
            ${isActive ? 'text-blue-600' : 'text-gray-500'}
          `}
        >
          {conversation.messageCount} {conversation.messageCount === 1 ? 'message' : 'messages'}
        </span>
      </div>
    </button>
  );
}

/**
 * ConversationItemSkeleton - Loading placeholder for conversation items
 */
export function ConversationItemSkeleton() {
  return (
    <div className="w-full px-4 py-3 rounded-lg border-l-4 border-transparent">
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
        <div className="h-3 bg-gray-200 rounded w-12 animate-pulse" />
      </div>
      <div className="h-3 bg-gray-200 rounded w-full animate-pulse mb-1.5" />
      <div className="h-3 bg-gray-200 rounded w-20 animate-pulse" />
    </div>
  );
}
