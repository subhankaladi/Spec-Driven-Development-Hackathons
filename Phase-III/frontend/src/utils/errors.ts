/**
 * Error Translation Utility
 *
 * Maps backend error codes to user-friendly messages with actionable suggestions.
 * Ensures users understand errors without exposing technical details.
 */

import type { ErrorCode, ErrorMessage } from '@/types/chat';
import type { HttpError } from './http';

/**
 * Error code to user message mapping
 */
const ERROR_MESSAGES: Record<ErrorCode, { message: string; suggestion: string }> = {
  NETWORK_ERROR: {
    message: 'Connection lost',
    suggestion: 'Check your internet connection and try again',
  },
  AUTH_EXPIRED: {
    message: 'Your session expired',
    suggestion: 'Please refresh the page or log in again',
  },
  UNAUTHORIZED: {
    message: 'You need to be logged in',
    suggestion: 'Please log in to continue using the chat',
  },
  SERVER_ERROR: {
    message: 'Server is busy',
    suggestion: 'Please try again in a moment',
  },
  VALIDATION_ERROR: {
    message: 'Message is invalid',
    suggestion: 'Please check your message and try again',
  },
  RATE_LIMITED: {
    message: "You're sending messages too fast",
    suggestion: 'Please wait a moment before sending another message',
  },
  NOT_FOUND: {
    message: 'Conversation not found',
    suggestion: 'The conversation may have been deleted',
  },
};

/**
 * Map HTTP status code to error code
 */
function mapStatusToErrorCode(status: number, backendCode?: string): ErrorCode {
  // If backend provides a specific error code, use it
  if (backendCode) {
    const upperCode = backendCode.toUpperCase();
    if (upperCode in ERROR_MESSAGES) {
      return upperCode as ErrorCode;
    }
  }

  // Otherwise, map by HTTP status
  switch (status) {
    case 401:
      return 'UNAUTHORIZED';
    case 404:
      return 'NOT_FOUND';
    case 429:
      return 'RATE_LIMITED';
    case 400:
      return 'VALIDATION_ERROR';
    case 500:
    case 502:
    case 503:
    case 504:
      return 'SERVER_ERROR';
    case 0:
      return 'NETWORK_ERROR';
    default:
      return 'SERVER_ERROR';
  }
}

/**
 * Map backend error to user-friendly error message
 */
export function mapErrorToUserMessage(
  error: HttpError | Error | unknown,
  retry?: () => void
): ErrorMessage {
  // HTTP error from backend
  if (error instanceof Error && 'status' in error) {
    const httpError = error as HttpError;
    const code = mapStatusToErrorCode(httpError.status, httpError.code);
    const mapping = ERROR_MESSAGES[code];

    return {
      code,
      message: mapping.message,
      suggestion: mapping.suggestion,
      retry,
    };
  }

  // Generic error
  if (error instanceof Error) {
    return {
      code: 'SERVER_ERROR',
      message: 'Something went wrong',
      suggestion: 'Please try again',
      retry,
    };
  }

  // Unknown error
  return {
    code: 'SERVER_ERROR',
    message: 'An unexpected error occurred',
    suggestion: 'Please refresh the page and try again',
    retry,
  };
}

/**
 * Check if error indicates authentication failure
 */
export function isAuthError(error: HttpError | Error | unknown): boolean {
  if (!(error instanceof Error && 'status' in error)) {
    return false;
  }

  const httpError = error as HttpError;
  return httpError.status === 401 || httpError.code === 'UNAUTHORIZED';
}

/**
 * Check if error indicates rate limiting
 */
export function isRateLimitError(error: HttpError | Error | unknown): boolean {
  if (!(error instanceof Error && 'status' in error)) {
    return false;
  }

  const httpError = error as HttpError;
  return httpError.status === 429 || httpError.code === 'RATE_LIMITED';
}

/**
 * Get retry-after duration from rate limit error (in seconds)
 */
export function getRetryAfter(error: HttpError | Error | unknown): number | null {
  if (!isRateLimitError(error)) return null;

  const httpError = error as HttpError;

  // Check details for reset_after_seconds
  if (httpError.details && 'reset_after_seconds' in httpError.details) {
    return httpError.details.reset_after_seconds as number;
  }

  // Default to 60 seconds if not specified
  return 60;
}

/**
 * Format error for display in UI
 */
export function formatError(errorMessage: ErrorMessage): string {
  return `${errorMessage.message}. ${errorMessage.suggestion}`;
}
