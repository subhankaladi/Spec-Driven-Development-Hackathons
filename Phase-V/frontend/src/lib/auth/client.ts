import { createAuthClient } from 'better-auth/client';

const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  fetchOptions: {
    // Configure to work with our backend's specific endpoint paths
    credentials: 'include', // Include cookies for session handling
  },
});

// Export the session hook for use in components
export { authClient };
export const { useSession, signIn, signOut } = authClient;