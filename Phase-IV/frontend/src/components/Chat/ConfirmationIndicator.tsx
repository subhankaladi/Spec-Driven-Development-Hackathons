/**
 * ConfirmationIndicator Component
 *
 * Displays visual feedback for successful operations.
 * Shows checkmark icon and success styling.
 */

'use client';

interface ConfirmationIndicatorProps {
  message: string;
  show?: boolean;
}

export function ConfirmationIndicator({ message, show = true }: ConfirmationIndicatorProps) {
  if (!show) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg text-green-800">
      {/* Checkmark icon */}
      <svg
        className="w-5 h-5 text-green-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 13l4 4L19 7"
        />
      </svg>

      {/* Message */}
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}
