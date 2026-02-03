/**
 * MessageInput Component
 *
 * Text input for composing and sending chat messages.
 * Includes character counter, Enter key support, and send button.
 */

'use client';

import { useState, useRef, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  maxLength?: number;
}

export function MessageInput({
  onSend,
  disabled = false,
  maxLength = 5000,
}: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;

    onSend(input.trim());
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const isOverLimit = input.length > maxLength;
  const canSend = input.trim().length > 0 && !isOverLimit && !disabled;

  return (
    <div className="flex gap-3">
      {/* Text input */}
      <div className="flex-1">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Type a message... (Enter to send)"
          className="w-full p-3 bg-gray-900/50 backdrop-blur-sm border border-gray-700/50 text-gray-100 placeholder-gray-500 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:bg-gray-900/30 disabled:cursor-not-allowed transition-all"
          rows={1}
          maxLength={maxLength + 100}
          aria-label="Message input"
        />

        {/* Character counter */}
        {input.length > 0 && (
          <div className="flex justify-between items-center mt-2 text-xs px-1">
            <span className={isOverLimit ? 'text-red-400 font-medium' : 'text-gray-500'}>
              {input.length} / {maxLength}
              {isOverLimit && ' (too long)'}
            </span>
            <span className="text-gray-600">
              Shift+Enter for new line
            </span>
          </div>
        )}
      </div>

      {/* Send button */}
      <button
        onClick={handleSubmit}
        disabled={!canSend}
        className="px-5 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-medium hover:from-blue-700 hover:to-blue-800 disabled:from-gray-700 disabled:to-gray-800 disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 self-start"
        aria-label="Send message"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
    </div>
  );
}
