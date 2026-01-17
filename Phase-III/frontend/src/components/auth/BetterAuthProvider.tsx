'use client';

import { AuthContextProvider } from '@/context/AuthContext';

// Wrapper component that integrates BetterAuth with the existing AuthContext
// The authClient is initialized in the client.ts file
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