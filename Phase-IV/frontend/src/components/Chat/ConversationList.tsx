/**
 * ConversationList Component
 *
 * Displays a sidebar list of all conversations.
 * Supports conversation selection, loading states, and empty states.
 */

'use client';

import React, { useEffect } from 'react';
import type { Conversation, UUID } from '@/types/chat';
import { ConversationItem, ConversationItemSkeleton } from './ConversationItem';
import { LoadingIndicator } from './LoadingIndicator';

export interface ConversationListProps {
  /** Array of conversations to display */
  conversations: Conversation[];
  /** Currently selected conversation ID */
  currentConversationId: UUID | null;
  /** Whether conversations are loading */
  isLoading?: boolean;
  /** Error message if loading failed */
  error?: string | null;
  /** Callback when conversation is selected */
  onSelectConversation: (conversationId: UUID) => void;
  /** Callback to create new conversation */
  onNewConversation: () => void;
  /** Callback to load conversations (called on mount) */
  onLoadConversations?: () => void;
}

/**
 * ConversationList displays a sidebar of conversation history
 *
 * @example
 * <ConversationList
 *   conversations={conversations}
 *   currentConversationId={currentId}
 *   onSelectConversation={handleSelect}
 *   onNewConversation={handleNew}
 * />
 */
export function ConversationList({
  conversations,
  currentConversationId,
  isLoading = false,
  error = null,
  onSelectConversation,
  onNewConversation,
  onLoadConversations,
}: ConversationListProps) {
  // Load conversations on mount
  useEffect(() => {
    if (onLoadConversations) {
      onLoadConversations();
    }
  }, [onLoadConversations]);

  return (
    <div className="flex flex-col h-full bg-gray-50 border-r border-gray-200">
      {/* Header with New Conversation button */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="
            w-full px-4 py-2 bg-blue-600 text-white rounded-lg
            hover:bg-blue-700 transition-colors
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            font-medium text-sm
          "
          aria-label="Start new conversation"
        >
          <span className="flex items-center justify-center gap-2">
            <svg
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            New Chat
          </span>
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-2">
        {/* Loading state */}
        {isLoading && conversations.length === 0 && (
          <div className="space-y-2">
            <ConversationItemSkeleton />
            <ConversationItemSkeleton />
            <ConversationItemSkeleton />
          </div>
        )}

        {/* Error state */}
        {error && !isLoading && (
          <div className="px-4 py-8 text-center">
            <svg
              className="h-12 w-12 text-gray-400 mx-auto mb-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-gray-600 mb-3">{error}</p>
            {onLoadConversations && (
              <button
                onClick={onLoadConversations}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Try again
              </button>
            )}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !error && conversations.length === 0 && (
          <div className="px-4 py-8 text-center">
            <svg
              className="h-12 w-12 text-gray-400 mx-auto mb-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 2c-2.236 0-4.43.18-6.57.524C1.993 2.755 1 4.014 1 5.426v5.148c0 1.413.993 2.67 2.43 2.902.848.137 1.705.248 2.57.331v3.443a.75.75 0 001.28.53l3.58-3.579a.78.78 0 01.527-.224 41.202 41.202 0 005.183-.5c1.437-.232 2.43-1.49 2.43-2.903V5.426c0-1.413-.993-2.67-2.43-2.902A41.289 41.289 0 0010 2zm0 7a1 1 0 100-2 1 1 0 000 2zM8 8a1 1 0 11-2 0 1 1 0 012 0zm5 1a1 1 0 100-2 1 1 0 000 2z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-gray-600 mb-2">No conversations yet</p>
            <p className="text-xs text-gray-500">
              Start a new chat to begin
            </p>
          </div>
        )}

        {/* Conversation items */}
        {!isLoading && !error && conversations.length > 0 && (
          <div className="space-y-1" role="list" aria-label="Conversations">
            {conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onClick={() => onSelectConversation(conversation.id)}
              />
            ))}
          </div>
        )}

        {/* Loading more indicator (for pagination) */}
        {isLoading && conversations.length > 0 && (
          <div className="py-4 flex justify-center">
            <LoadingIndicator size="sm" variant="secondary" />
          </div>
        )}
      </div>

      {/* Footer with conversation count */}
      {!isLoading && conversations.length > 0 && (
        <div className="flex-shrink-0 px-4 py-2 border-t border-gray-200 bg-gray-100">
          <p className="text-xs text-gray-600 text-center">
            {conversations.length} {conversations.length === 1 ? 'conversation' : 'conversations'}
          </p>
        </div>
      )}
    </div>
  );
}
