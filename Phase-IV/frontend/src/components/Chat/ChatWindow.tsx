/**
 * ChatWindow Component
 *
 * Main chat interface container that combines MessageList and MessageInput.
 * Manages chat state via useChat hook and displays error banners.
 */

'use client';

import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ReAuthenticationModal } from '../auth/ReAuthenticationModal';
import { ErrorBanner } from './ErrorBanner';
import { ConversationList } from './ConversationList';
import { useState } from 'react';

interface ChatWindowProps {
  conversationId?: string | null;
}

export function ChatWindow({ conversationId = null }: ChatWindowProps) {
  const {
    messages,
    conversations,
    currentConversationId,
    isLoading,
    error,
    needsReAuth,
    sendMessage,
    loadConversations,
    loadConversation,
    setCurrentConversation,
    clearError,
    retryMessage,
    handleReAuthenticated,
  } = useChat();

  // Mobile sidebar toggle
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Handle conversation selection
  const handleSelectConversation = (convId: string) => {
    loadConversation(convId);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };

  // Handle new conversation
  const handleNewConversation = () => {
    setCurrentConversation(null);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };

  return (
    <div className="flex h-full bg-white">
      {/* Sidebar - Conversation List */}
      <div
        className={`
          ${isSidebarOpen ? 'block' : 'hidden'}
          md:block md:w-80 lg:w-96 flex-shrink-0
          absolute md:relative inset-y-0 left-0 z-30
          bg-gray-50 md:bg-transparent
        `}
      >
        <ConversationList
          conversations={conversations}
          currentConversationId={currentConversationId}
          isLoading={false}
          error={null}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onLoadConversations={loadConversations}
        />
      </div>

      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Chat header */}
        <div className="border-b bg-gray-50 px-6 py-4 flex items-center gap-4">
          {/* Mobile menu toggle */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle conversation list"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="flex-1">
            <h1 className="text-xl font-semibold text-gray-900">Chat</h1>
            <p className="text-sm text-gray-600 mt-1">
              Ask me to manage your tasks using natural language
            </p>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <ErrorBanner
            error={error}
            onRetry={error.retry}
            onClose={clearError}
            position="inline"
            className="border-b border-transparent"
          />
        )}

        {/* Message list */}
        <MessageList messages={messages} isLoading={isLoading} />

        {/* Message input */}
        <MessageInput onSend={sendMessage} disabled={isLoading} />

        {/* Re-authentication modal */}
        <ReAuthenticationModal show={needsReAuth} onClose={handleReAuthenticated} />
      </div>
    </div>
  );
}
