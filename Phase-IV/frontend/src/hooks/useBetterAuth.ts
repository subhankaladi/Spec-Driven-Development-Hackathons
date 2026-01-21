import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import apiClient from '@/lib/api/client';

// For now, since BetterAuth uses atoms instead of standard hooks, we'll create a simple wrapper
// that works with our existing system but represents the BetterAuth integration
interface User {
  id: string;
  email: string;
  token?: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshAuth: () => void;
}

export function useBetterAuth(): AuthContextType {
  const router = useRouter();

  // Direct API calls to match our backend endpoints
  const signInHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signin', {
        email,
        password
      });

      if (response.data.access_token) {
        // Store the token in localStorage for use with API calls
        localStorage.setItem('access_token', response.data.access_token);
        router.push('/tasks');
      } else {
        throw new Error('Sign in failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Sign in failed';
      throw new Error(errorMessage);
    }
  }, [router]);

  const signUpHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signup', {
        email,
        password
      });

      if (response.data.access_token) {
        // Store the token in localStorage for use with API calls
        localStorage.setItem('access_token', response.data.access_token);
        router.push('/tasks');
      } else {
        throw new Error('Sign up failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Sign up failed';
      throw new Error(errorMessage);
    }
  }, [router]);

  const signOutHandler = useCallback(async () => {
    try {
      // Call backend to clear the httpOnly cookie
      await apiClient.post('/auth/signout', {});

      // Clear the stored token from localStorage
      localStorage.removeItem('access_token');

      // Redirect to sign in page
      router.push('/signin');
    } catch (error) {
      console.error('Sign out error:', error);
      // Even if sign out fails, clear local storage and redirect
      localStorage.removeItem('access_token');
      router.push('/signin');
    }
  }, [router]);

  const refreshAuth = useCallback(() => {
    // Session refreshing would happen automatically with JWT
  }, []);

  // Return initial state - the actual state will be managed by AuthContext
  return {
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false,
    signIn: signInHandler,
    signUp: signUpHandler,
    signOut: signOutHandler,
    refreshAuth,
  };
}