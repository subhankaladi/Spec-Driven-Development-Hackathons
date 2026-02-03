/**
 * LoadingIndicator Component
 *
 * Displays a spinner animation to indicate loading state
 * Used in chat interface for message sending and data fetching
 */

import React from 'react';

export interface LoadingIndicatorProps {
  /** Size of the spinner: 'sm' | 'md' | 'lg' */
  size?: 'sm' | 'md' | 'lg';
  /** Optional label text to display next to spinner */
  label?: string;
  /** Color variant: 'primary' | 'secondary' | 'white' */
  variant?: 'primary' | 'secondary' | 'white';
  /** Additional CSS classes */
  className?: string;
}

/**
 * LoadingIndicator displays an animated spinner with optional label
 *
 * @example
 * <LoadingIndicator size="md" label="Sending..." variant="primary" />
 */
export function LoadingIndicator({
  size = 'md',
  label,
  variant = 'primary',
  className = '',
}: LoadingIndicatorProps) {
  // Size mappings
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
  };

  // Color variant mappings
  const variantClasses = {
    primary: 'border-blue-600 border-t-transparent',
    secondary: 'border-gray-600 border-t-transparent',
    white: 'border-white border-t-transparent',
  };

  // Text size mappings
  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  return (
    <div
      className={`flex items-center gap-2 ${className}`}
      role="status"
      aria-live="polite"
      aria-label={label || 'Loading'}
    >
      {/* Spinner */}
      <div
        className={`
          ${sizeClasses[size]}
          ${variantClasses[variant]}
          rounded-full
          animate-spin
        `}
        aria-hidden="true"
      />

      {/* Optional label */}
      {label && (
        <span className={`${textSizeClasses[size]} text-gray-300`}>
          {label}
        </span>
      )}

      {/* Screen reader text */}
      <span className="sr-only">{label || 'Loading, please wait...'}</span>
    </div>
  );
}

/**
 * LoadingDots - Alternative loading indicator with animated dots
 * Useful for inline loading states
 */
export function LoadingDots({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center gap-1 ${className}`} role="status" aria-label="Loading">
      <span
        className="h-2 w-2 bg-blue-400 rounded-full animate-bounce"
        style={{ animationDelay: '0ms' }}
      />
      <span
        className="h-2 w-2 bg-blue-400 rounded-full animate-bounce"
        style={{ animationDelay: '150ms' }}
      />
      <span
        className="h-2 w-2 bg-blue-400 rounded-full animate-bounce"
        style={{ animationDelay: '300ms' }}
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
}

/**
 * InlineLoadingSpinner - Small inline spinner for tight spaces
 * Used within buttons or small UI elements
 */
export function InlineLoadingSpinner({ className = '' }: { className?: string }) {
  return (
    <div
      className={`h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin ${className}`}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}
