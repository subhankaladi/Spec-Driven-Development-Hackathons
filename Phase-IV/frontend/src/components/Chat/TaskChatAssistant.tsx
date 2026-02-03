/**
 * TaskChatAssistant Component
 *
 * Simplified chat interface for task management dashboard.
 * Dark theme with smooth, modern UI.
 */

'use client';

import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ReAuthenticationModal } from '../auth/ReAuthenticationModal';
import { ErrorBanner } from './ErrorBanner';

export function TaskChatAssistant() {
  const {
    messages,
    isLoading,
    error,
    needsReAuth,
    sendMessage,
    clearError,
    handleReAuthenticated,
  } = useChat();

  // Show welcome message if no messages yet
  const showWelcome = messages.length === 0 && !isLoading;

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-gray-700/50 overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 bg-gradient-to-r from-blue-600 via-blue-500 to-purple-600 px-6 py-4 border-b border-blue-500/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">
              AI Task Assistant
            </h2>
            <p className="text-blue-100 text-xs">
              Powered by GPT-4
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex-shrink-0 p-4 border-b border-gray-700/50">
          <ErrorBanner error={error} onRetry={error.retry} onClose={clearError} position="inline" />
        </div>
      )}

      {/* Messages or Welcome Screen */}
      <div className="flex-1 overflow-hidden">
        {showWelcome ? (
          <div className="h-full flex items-center justify-center p-6">
            <div className="max-w-md text-center space-y-6">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                <svg
                  className="w-10 h-10 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">
                  Hey! I'm your AI Assistant
                </h3>
                <p className="text-sm text-gray-400">
                  I can help you manage tasks with natural language
                </p>
              </div>
              <div className="space-y-2 text-left bg-gray-800/50 backdrop-blur-sm rounded-xl p-5 border border-gray-700/50">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Try these commands:</p>
                <div className="flex items-start gap-3 text-sm text-gray-300 hover:text-white transition-colors group">
                  <span className="text-blue-400 group-hover:text-blue-300">→</span>
                  <span>"Create a task to buy groceries"</span>
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-300 hover:text-white transition-colors group">
                  <span className="text-blue-400 group-hover:text-blue-300">→</span>
                  <span>"Show me all my tasks"</span>
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-300 hover:text-white transition-colors group">
                  <span className="text-blue-400 group-hover:text-blue-300">→</span>
                  <span>"Mark the grocery task as complete"</span>
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-300 hover:text-white transition-colors group">
                  <span className="text-blue-400 group-hover:text-blue-300">→</span>
                  <span>"Delete all completed tasks"</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}
      </div>

      {/* Input */}
      <div className="flex-shrink-0 bg-gray-800/50 backdrop-blur-sm border-t border-gray-700/50 p-4">
        <MessageInput onSend={sendMessage} disabled={isLoading} />
      </div>

      {/* Re-authentication Modal */}
      <ReAuthenticationModal show={needsReAuth} onClose={handleReAuthenticated} />
    </div>
  );
}
