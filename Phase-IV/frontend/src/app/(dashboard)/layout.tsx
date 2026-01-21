// T040: Dashboard layout with navigation bar and user menu

'use client';

import React from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, signOut } = useAuth();

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background-dark">
      {/* Navigation bar */}
      <nav className="bg-background-card border-b border-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-purple bg-clip-text text-transparent">
                ✨ Todo App
              </h1>
            </div>

            <div className="flex items-center gap-4">
              {user && (
                <>
                  <span className="text-sm text-gray-300">{user.email}</span>
                  <Button variant="ghost" size="sm" onClick={signOut}>
                    Sign Out
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
    </AuthGuard>
  );
}
