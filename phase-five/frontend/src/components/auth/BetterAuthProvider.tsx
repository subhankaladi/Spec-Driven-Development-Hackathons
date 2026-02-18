'use client';

import { AuthContextProvider } from '@/context/AuthContext';

// Wrapper component that provides the JWT-based authentication context
// This component wraps the entire app to provide auth context to all components
export function BetterAuthProvider({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <AuthContextProvider>
      {children}
    </AuthContextProvider>
  );
}