'use client';

import { useState, useEffect } from 'react';
import ChatKitWrapper from '@/components/ChatInterface/ChatKitWrapper';
import LoadingStates from '@/components/ChatInterface/LoadingStates';
import { JWTHandler } from '@/components/Auth/JWTHandler';
import { getConversationHistory } from '@/components/utils/apiClient';
import { Conversation } from '@/components/types/chatTypes';

export default function ChatPage() {
  const [userId, setUserId] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);

  useEffect(() => {
    // Initialize the page
    initializePage();
  }, []);

  const initializePage = async () => {
    try {
      // Validate JWT token
      if (!JWTHandler.isValidToken()) {
        setError('No valid authentication token found. Please log in.');
        return;
      }

      // Get user ID from token
      const token = JWTHandler.getToken();
      if (token) {
        const decodedToken = JWTHandler.decodeToken(token);
        if (decodedToken?.user_id) {
          setUserId(decodedToken.user_id);

          // Load conversation history if available
          const history = getConversationHistory(decodedToken.user_id);
          if (history) {
            setConversation(history);
          }
        } else {
          setError('User ID not found in token');
          return;
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during initialization');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingStates isLoading={true} error={null} />;
  }

  if (error) {
    return <LoadingStates isLoading={false} error={error} />;
  }

  if (!userId) {
    return (
      <div className="chat-page">
        <div className="authentication-required">
          <h2>Authentication Required</h2>
          <p>Please log in to access the chat interface.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-50 to-zinc-100 dark:from-zinc-950 dark:to-zinc-900 p-4">
      <header className="chat-header max-w-4xl mx-auto mb-6">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 text-center">
          Todo Management Chat
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 text-center">
          Manage your tasks through natural language
        </p>
      </header>

      <main className="chat-main max-w-4xl mx-auto bg-white dark:bg-zinc-800 rounded-xl shadow-lg p-4">
        <ChatKitWrapper userId={userId} domainAllowlist={['localhost', '127.0.0.1']} />
      </main>

      <footer className="chat-footer max-w-4xl mx-auto mt-6 text-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Your conversations are securely processed through our backend.
        </p>
      </footer>
    </div>
  );
}