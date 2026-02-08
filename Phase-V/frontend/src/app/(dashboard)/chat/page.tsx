// T026: Chat page - AI Assistant chat interface

'use client';

import React from 'react';
import { ChatInterface } from '@/components/chat/ChatInterface';

/**
 * Chat Page Component
 * - Next.js App Router page with "use client" directive for interactivity
 * - Protected route (authentication enforced via middleware)
 * - Renders ChatInterface component
 * - Full height page layout for optimal chat experience
 */
export default function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-accent-purple bg-clip-text text-transparent mb-2">
          Chat with AI Assistant
        </h1>
        <p className="text-gray-400">
          Ask me to create, list, update, or delete your tasks using natural language
        </p>
      </div>

      {/* Chat interface - takes remaining height */}
      <div className="flex-1 min-h-0">
        <ChatInterface />
      </div>
    </div>
  );
}
