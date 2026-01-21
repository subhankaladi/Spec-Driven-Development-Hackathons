/**
 * ErrorBanner Component
 *
 * Displays error messages with retry functionality
 * Shows user-friendly error messages and suggested actions
 */

import React from 'react';
import type { ErrorMessage } from '@/types/chat';

export interface ErrorBannerProps {
  /** Error object containing code, message, and suggestion */
  error: ErrorMessage;
  /** Callback when retry button is clicked */
  onRetry?: () => void;
  /** Callback when close/dismiss button is clicked */
  onClose?: () => void;
  /** Whether to show the banner (for animations) */
  show?: boolean;
  /** Position: 'top' | 'bottom' | 'inline' */
  position?: 'top' | 'bottom' | 'inline';
  /** Additional CSS classes */
  className?: string;
}

/**
 * ErrorBanner displays user-friendly error messages with retry functionality
 *
 * @example
 * <ErrorBanner
 *   error={{ code: 'NETWORK_ERROR', message: 'Connection failed', suggestion: 'Check your internet connection' }}
 *   onRetry={handleRetry}
 *   onClose={handleClose}
 * />
 */
export function ErrorBanner({
  error,
  onRetry,
  onClose,
  show = true,
  position = 'inline',
  className = '',
}: ErrorBannerProps) {
  if (!show) return null;

  // Position-specific styling
  const positionClasses = {
    top: 'fixed top-0 left-0 right-0 z-30',
    bottom: 'fixed bottom-0 left-0 right-0 z-30',
    inline: 'relative',
  };

  // Error severity based on code
  const getSeverity = (code: string): 'error' | 'warning' | 'info' => {
    if (code === 'NETWORK_ERROR' || code === 'SERVER_ERROR') return 'error';
    if (code === 'AUTH_EXPIRED' || code === 'RATE_LIMITED') return 'warning';
    return 'info';
  };

  const severity = getSeverity(error.code);

  // Severity color mappings - Dark theme
  const severityStyles = {
    error: {
      bg: 'bg-red-900/30 backdrop-blur-sm',
      border: 'border-red-600/50',
      text: 'text-red-200',
      icon: 'text-red-400',
      button: 'bg-red-600 hover:bg-red-700 text-white',
    },
    warning: {
      bg: 'bg-yellow-900/30 backdrop-blur-sm',
      border: 'border-yellow-600/50',
      text: 'text-yellow-200',
      icon: 'text-yellow-400',
      button: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    },
    info: {
      bg: 'bg-blue-900/30 backdrop-blur-sm',
      border: 'border-blue-600/50',
      text: 'text-blue-200',
      icon: 'text-blue-400',
      button: 'bg-blue-600 hover:bg-blue-700 text-white',
    },
  };

  const styles = severityStyles[severity];

  // Icon based on severity
  const getIcon = () => {
    if (severity === 'error') {
      return (
        <svg
          className="h-5 w-5"
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
      );
    }
    if (severity === 'warning') {
      return (
        <svg
          className="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
            clipRule="evenodd"
          />
        </svg>
      );
    }
    return (
      <svg
        className="h-5 w-5"
        viewBox="0 0 20 20"
        fill="currentColor"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"
          clipRule="evenodd"
        />
      </svg>
    );
  };

  return (
    <div
      className={`
        ${positionClasses[position]}
        ${styles.bg}
        ${styles.border}
        border
        rounded-md
        p-4
        ${className}
      `}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${styles.icon}`}>
          {getIcon()}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Error message */}
          <p className={`font-medium ${styles.text}`}>
            {error.message}
          </p>

          {/* Suggestion (if provided) */}
          {error.suggestion && (
            <p className={`mt-1 text-sm ${styles.text} opacity-90`}>
              {error.suggestion}
            </p>
          )}

          {/* Error code (for debugging) */}
          {process.env.NODE_ENV === 'development' && (
            <p className="mt-1 text-xs text-gray-400">
              Error code: {error.code}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex-shrink-0 flex items-center gap-2">
          {/* Retry button (if retry handler provided) */}
          {onRetry && (
            <button
              onClick={onRetry}
              className={`
                ${styles.button}
                px-3 py-1.5
                text-sm font-medium
                rounded-md
                transition-colors
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900
              `}
              aria-label="Retry action"
            >
              Retry
            </button>
          )}

          {/* Close button */}
          {onClose && (
            <button
              onClick={onClose}
              className={`
                ${styles.text}
                hover:opacity-75
                transition-opacity
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900
                rounded-md
                p-2 min-w-[44px] min-h-[44px] flex items-center justify-center
              `}
              aria-label="Dismiss error"
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * CompactErrorBanner - Smaller error banner for inline use (Dark theme)
 */
export function CompactErrorBanner({
  error,
  onRetry,
  onClose,
}: {
  error: ErrorMessage;
  onRetry?: () => void;
  onClose?: () => void;
}) {
  return (
    <div
      className="flex items-center gap-2 bg-red-900/30 backdrop-blur-sm border border-red-600/50 rounded-md px-3 py-2"
      role="alert"
    >
      <svg
        className="h-4 w-4 text-red-400 flex-shrink-0"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
          clipRule="evenodd"
        />
      </svg>
      <p className="text-sm text-red-200 flex-1 min-w-0">{error.message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs text-red-300 hover:text-red-100 font-medium"
        >
          Retry
        </button>
      )}
      {onClose && (
        <button onClick={onClose} className="text-red-400 hover:text-red-200">
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </button>
      )}
    </div>
  );
}
