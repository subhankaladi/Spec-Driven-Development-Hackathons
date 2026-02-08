// T024: MessageInput component for composing and sending chat messages

import React, { useState, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/Button';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled: boolean;
}

/**
 * MessageInput component provides a text input interface for chat messages
 * - Textarea with Tailwind styling
 * - Send button
 * - Enter key to send (Shift+Enter for new line)
 * - Auto-clear input after sending
 * - Disable textarea and button when processing
 */
export function MessageInput({ onSendMessage, disabled }: MessageInputProps) {
  const [message, setMessage] = useState<string>('');

  /**
   * Handle sending the message
   */
  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage(''); // Clear input after sending
    }
  };

  /**
   * Handle keyboard events in the textarea
   * - Enter: Send message
   * - Shift+Enter: New line
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent new line on Enter
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-800 bg-background-card p-4">
      <div className="flex items-end gap-3">
        {/* Message textarea */}
        <div className="flex-1">
          <label htmlFor="message-input" className="sr-only">
            Type your message
          </label>
          <textarea
            id="message-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            disabled={disabled}
            rows={3}
            className={`
              w-full px-4 py-3 bg-background-dark border rounded-xl resize-none
              text-gray-100 placeholder-gray-500
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              transition-all duration-200
              disabled:bg-background-hover disabled:cursor-not-allowed disabled:opacity-50
              border-gray-800 hover:border-gray-700
            `}
            aria-label="Chat message input"
          />
        </div>

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          variant="primary"
          size="md"
          className="flex-shrink-0"
          aria-label="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
          <span className="ml-2 hidden sm:inline">Send</span>
        </Button>
      </div>

      {/* Helper text */}
      <p className="mt-2 text-xs text-gray-500">
        Press <kbd className="px-1.5 py-0.5 bg-background-hover rounded text-gray-400 border border-gray-700">Enter</kbd> to send,{' '}
        <kbd className="px-1.5 py-0.5 bg-background-hover rounded text-gray-400 border border-gray-700">Shift</kbd> +{' '}
        <kbd className="px-1.5 py-0.5 bg-background-hover rounded text-gray-400 border border-gray-700">Enter</kbd> for new line
      </p>
    </div>
  );
}
