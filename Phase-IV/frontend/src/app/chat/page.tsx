/**
 * Chat Page
 *
 * Main chat interface page for managing tasks via natural language.
 * Protected route - requires authentication via AuthGuard.
 */

'use client';

import { useEffect, useState } from 'react';
import { ChatWindow } from '@/components/Chat/ChatWindow';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { validateDomainAllowlist } from '@/utils/domain';

export default function ChatPage() {
  const [domainError, setDomainError] = useState<string | null>(null);

  useEffect(() => {
    // Validate domain allowlist on component mount
    const error = validateDomainAllowlist();
    if (error) {
      setDomainError(error);
    }
  }, []);

  // Show domain error if not allowed
  if (domainError) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="max-w-md p-8 bg-white rounded-lg shadow-lg text-center">
          <div className="text-red-600 mb-4">
            <svg
              className="w-16 h-16 mx-auto"
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
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">{domainError}</p>
        </div>
      </div>
    );
  }

  return (
    <AuthGuard>
      <div className="h-screen flex flex-col">
        <ChatWindow />
      </div>
    </AuthGuard>
  );
}
