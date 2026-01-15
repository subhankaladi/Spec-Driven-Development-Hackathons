"use client";

import { useRedirectIfAuthenticated } from "@/hooks/useAuth";
import { SignUpForm } from "@/components/auth/SignUpForm";

export default function SignUpPage() {
  useRedirectIfAuthenticated();

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
              Create Account
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400 mt-2">
              Get started with your task management
            </p>
          </div>
          <SignUpForm />
        </div>
      </div>
    </div>
  );
}
