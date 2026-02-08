// T105: Landing page with dark red outline theme

import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0B0A0A] text-[#E5E7EB] relative overflow-hidden">
      {/* Subtle red grid background */}
      <div className="absolute inset-0 bg-[radial-gradient(#8B1E1E_1px,transparent_1px)] [background-size:24px_24px]" />
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="py-6 flex items-center justify-between border-b border-[#8B1E1E]">
          <h1 className="text-2xl font-bold text-[#8B1E1E]">
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
          <div className="inline-block mb-6 px-4 py-2 border border-[#8B1E1E] rounded-full">
            <span className="text-sm font-medium text-[#8B1E1E]">🚀 Modern Task Management</span>
          </div>

          <h2 className="text-5xl md:text-7xl font-bold text-[#E5E7EB] mb-6 leading-tight">
            AI Powered Todo App.
            <br />
            <span className="text-[#E5E7EB]">
              Get Tasks Done.
            </span>
          </h2>

          <p className="text-lg md:text-xl text-[#D1D5DB] mb-10 max-w-2xl mx-auto leading-relaxed">
            A bold and powerful todo app designed for deep focus.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link href="/signup">
              <Button variant="outline" size="lg">
                🎯 Start Using Todo App
              </Button>
            </Link>
            <Link href="/signin">
              <Button variant="ghost" size="lg">
                Learn More →
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          <div className="border border-[#8B1E1E] rounded-lg p-6 bg-transparent hover:border-[#B11226] hover-glow transition-all duration-300">
            <div className="w-12 h-12 border border-[#8B1E1E] rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-[#8B1E1E]"
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
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">
              Smart Task Management
            </h3>
            <p className="text-[#D1D5DB]">
              Intelligently organize and prioritize your tasks for maximum productivity.
            </p>
          </div>

          <div className="border border-[#8B1E1E] rounded-lg p-6 bg-transparent hover:border-[#B11226] hover-glow transition-all duration-300">
            <div className="w-12 h-12 border border-[#8B1E1E] rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-[#8B1E1E]"
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
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">
              Priority and Focus Mode
            </h3>
            <p className="text-[#D1D5DB]">
              Focus on what matters most with our distraction-free priority mode.
            </p>
          </div>

          <div className="border border-[#8B1E1E] rounded-lg p-6 bg-transparent hover:border-[#B11226] hover-glow transition-all duration-300">
            <div className="w-12 h-12 border border-[#8B1E1E] rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-[#8B1E1E]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">
              Minimal Distraction Interface
            </h3>
            <p className="text-[#D1D5DB]">
              Clean, focused interface that keeps you in the zone for deep work.
            </p>
          </div>

          <div className="border border-[#8B1E1E] rounded-lg p-6 bg-transparent hover:border-[#B11226] hover-glow transition-all duration-300">
            <div className="w-12 h-12 border border-[#8B1E1E] rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-[#8B1E1E]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">
              Fast and Lightweight
            </h3>
            <p className="text-[#D1D5DB]">
              Optimized for speed and performance to keep up with your workflow.
            </p>
          </div>
        </div>

        {/* Interface Preview */}
        <div className="py-16 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-[#E5E7EB] mb-12">Task Management Interface</h2>
          <div className="border border-[#8B1E1E] rounded-xl p-6 bg-[#111010]">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-[#E5E7EB]">Today's Tasks</h3>
              <span className="text-[#8B1E1E]">+ Add Task</span>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center p-3 border border-[#8B1E1E] rounded-lg bg-[#1A1919] hover-glow">
                <input 
                  type="checkbox" 
                  className="w-5 h-5 border border-[#8B1E1E] rounded checked:bg-[#8B1E1E] checked:border-[#8B1E1E] focus:ring-[#8B1E1E]" 
                />
                <span className="ml-3 text-[#E5E7EB]">Complete project proposal</span>
              </div>
              
              <div className="flex items-center p-3 border border-[#8B1E1E] rounded-lg bg-[#1A1919] hover-glow">
                <input 
                  type="checkbox" 
                  className="w-5 h-5 border border-[#8B1E1E] rounded checked:bg-[#8B1E1E] checked:border-[#8B1E1E] focus:ring-[#8B1E1E]" 
                />
                <span className="ml-3 text-[#E5E7EB]">Schedule team meeting</span>
              </div>
              
              <div className="flex items-center p-3 border border-[#8B1E1E] rounded-lg bg-[#1A1919] hover-glow">
                <input 
                  type="checkbox" 
                  className="w-5 h-5 border border-[#8B1E1E] rounded checked:bg-[#8B1E1E] checked:border-[#8B1E1E] focus:ring-[#8B1E1E]" 
                  defaultChecked
                />
                <span className="ml-3 text-[#8B1E1E] line-through">Review quarterly reports</span>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="py-16 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-[#E5E7EB] mb-12">How It Works</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-[#8B1E1E] rounded-full flex items-center justify-center mx-auto mb-4 hover-glow">
                <span className="text-[#E5E7EB] font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold text-[#E5E7EB] mb-2">Add your tasks</h3>
              <p className="text-[#D1D5DB]">Quickly add tasks with titles, due dates, and priorities</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-[#8B1E1E] rounded-full flex items-center justify-center mx-auto mb-4 hover-glow">
                <span className="text-[#E5E7EB] font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold text-[#E5E7EB] mb-2">Organize and prioritize</h3>
              <p className="text-[#D1D5DB]">Sort tasks by priority, category, or deadline</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-[#8B1E1E] rounded-full flex items-center justify-center mx-auto mb-4 hover-glow">
                <span className="text-[#E5E7EB] font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold text-[#E5E7EB] mb-2">Stay productive every day</h3>
              <p className="text-[#D1D5DB]">Track progress and maintain focus on your goals</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="py-16 border-t border-[#8B1E1E]">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-[#E5E7EB] mb-6">Build Your Daily Focus Habit</h2>
            <Link href="/signup">
              <Button variant="outline" size="lg">
                Start Using Todo App
              </Button>
            </Link>
          </div>
        </div>

        {/* Footer */}
        <footer className="py-8 text-center text-sm text-[#D1D5DB] border-t border-[#8B1E1E]">
          <div className="mb-2 text-[#8B1E1E]">✨ Todo App</div>
          <p>&copy; 2026 Todo App. Built with Next.js, FastAPI, and PostgreSQL.</p>
          <div className="mt-2 flex justify-center space-x-6">
            <a href="#" className="hover:text-[#8B1E1E]">Docs</a>
            <a href="#" className="hover:text-[#8B1E1E]">GitHub</a>
            <a href="#" className="hover:text-[#8B1E1E]">Contact</a>
          </div>
        </footer>
      </div>
    </div>
  );
}
