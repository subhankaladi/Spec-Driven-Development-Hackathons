/**
 * ReAuthenticationModal Component
 *
 * Modal dialog that prompts user to re-authenticate when their JWT token expires.
 * Provides clear messaging and redirect to login page.
 */

'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ReAuthenticationModalProps {
  show: boolean;
  onClose?: () => void;
}

export function ReAuthenticationModal({ show, onClose }: ReAuthenticationModalProps) {
  const router = useRouter();

  if (!show) return null;

  const handleReAuthenticate = () => {
    // Redirect to login page
    router.push('/signin');
  };

  const handleStay = () => {
    if (onClose) {
      onClose();
    }
  };

  // Add Escape key handler for keyboard accessibility
  useEffect(() => {
    if (!show) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleStay();
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [show]);

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={handleStay}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reauth-modal-title"
      >
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          {/* Icon */}
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-yellow-100 rounded-full mb-4">
            <svg
              className="w-6 h-6 text-yellow-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          {/* Title */}
          <h2
            id="reauth-modal-title"
            className="text-xl font-semibold text-gray-900 text-center mb-2"
          >
            Session Expired
          </h2>

          {/* Message */}
          <p className="text-gray-600 text-center mb-6">
            Your session has expired for security reasons. Please log in again to continue using the chat.
          </p>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleStay}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Stay Here
            </button>
            <button
              onClick={handleReAuthenticate}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              autoFocus
            >
              Log In
            </button>
          </div>

          {/* Additional info */}
          <p className="text-xs text-gray-500 text-center mt-4">
            Your unsent messages will be saved and can be retried after logging in.
          </p>
        </div>
      </div>
    </>
  );
}
