// T029: Sign up page with SignUpForm and navigation links

import Link from 'next/link';
import { SignUpForm } from '@/components/auth/SignUpForm';

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0B] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#111111] rounded-xl  p-8 space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white">Sign Up</h2>
          <p className="mt-2 text-sm text-gray-400">
            Create an account to start managing your tasks.
          </p>
        </div>

        <SignUpForm />

        <div className="text-center text-sm pt-4 border-t border-[#E25555]/30">
          <span className="text-gray-400">Already have an account? </span>
          <Link
            href="/signin"
            className="font-medium text-[#E25555] hover:text-[#E25555]/80 transition-colors"
          >
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
