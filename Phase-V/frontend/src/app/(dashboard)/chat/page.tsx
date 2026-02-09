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
    <div className="min-h-screen bg-[#0B0B0B] p-3 sm:p-4 md:p-6">
      <div className="max-w-full mx-auto h-full">
        {/* Page header */}
        <div className="mb-3 sm:mb-4 md:mb-6 py-3 sm:py-4 border-b border-[#E25555]/30">
          <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-[#E25555] mb-1">
            Chat with AI Assistant
          </h1>
          <p className="text-gray-400 text-xs sm:text-sm">
            Ask me to create, list, update, or delete your tasks using natural language
          </p>
        </div>

        {/* Chat interface - takes remaining height */}
        <div className="bg-[#111111] rounded-lg sm:rounded-xl border border-[#E25555]/30 p-3 sm:p-4 md:p-6 h-[calc(100vh-180px)] sm:h-[calc(100vh-200px)] md:h-[calc(100vh-220px)] min-h-[50vh]">
          <ChatInterface />
        </div>
      </div>
    </div>
  );
}
