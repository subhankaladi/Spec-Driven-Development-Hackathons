// T105: Landing page with branding and auth CTAs

import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background-dark relative overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-accent-purple/10 to-accent-cyan/10" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(14,165,233,0.1),transparent_50%)]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="py-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-accent-purple bg-clip-text text-transparent">
            ✨ Todo App
          </h1>
          <div className="flex items-center gap-3">
            <Link href="/signin">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link href="/signup">
              <Button variant="primary" size="sm">
                Sign Up
              </Button>
            </Link>
          </div>
        </header>

        {/* Hero section */}
        <div className="py-20 md:py-32 text-center">
          <div className="inline-block mb-6 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full">
            <span className="text-sm font-medium text-primary-400">🚀 Modern Task Management</span>
          </div>

          <h2 className="text-5xl md:text-7xl font-bold text-gray-100 mb-6 leading-tight">
            Manage Your Tasks
            <br />
            <span className="bg-clip-text text-white">
              Simply & Efficiently
            </span>
          </h2>

          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Stay organized and productive with our intuitive task management app.
            Create, edit, and track your tasks effortlessly in a beautiful dark interface.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link href="/signup">
              <Button variant="primary" size="lg">
                🎯 Get Started Free
              </Button>
            </Link>
            <Link href="/signin">
              <Button variant="secondary" size="lg">
                Sign In →
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Easy Task Creation
            </h3>
            <p className="text-gray-600">
              Quickly add new tasks with titles and descriptions. Stay organized effortlessly.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Responsive Design
            </h3>
            <p className="text-gray-600">
              Access your tasks on any device - desktop, tablet, or mobile.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Secure & Private
            </h3>
            <p className="text-gray-600">
              Your tasks are secure with JWT authentication. Only you can access your data.
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="py-8 text-center text-sm text-gray-600 border-t border-gray-200">
          <p>&copy; 2026 Todo App. Built with Next.js, FastAPI, and PostgreSQL.</p>
        </footer>
      </div>
    </div>
  );
}
