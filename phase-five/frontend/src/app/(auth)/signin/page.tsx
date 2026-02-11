// T028: Sign in page with SignInForm and navigation links

import Link from 'next/link';
import { SignInForm } from '@/components/auth/SignInForm';

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0B] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#111111] rounded-xl p-8 space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white">Sign In</h2>
          <p className="mt-2 text-sm text-gray-400">
            Welcome back! Sign in to manage your tasks.
          </p>
        </div>

        <SignInForm />

        <div className="text-center text-sm pt-4 border-t border-[#E25555]/30">
          <span className="text-gray-400">Don't have an account? </span>
          <Link
            href="/signup"
            className="font-medium text-[#E25555] hover:text-[#E25555]/80 transition-colors"
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
