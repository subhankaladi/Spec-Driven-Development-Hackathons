import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import apiClient from '@/lib/api/client';

// Pure JWT-based auth hook without BetterAuth dependencies
// This hook handles the API calls but not the navigation - that's handled by AuthContext
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
  // Navigation is handled by the AuthContext after successful auth
  const signInHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/auth/signin', {
        email,
        password
      });

      if (response.data.access_token) {
        // Store the token in localStorage for use with API calls
        localStorage.setItem('access_token', response.data.access_token);
        // Don't navigate here - let AuthContext handle it
        return response.data;
      } else {
        throw new Error('Sign in failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Sign in failed';
      throw new Error(errorMessage);
    }
  }, []);

  const signUpHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/auth/signup', {
        email,
        password
      });

      if (response.data.access_token) {
        // Store the token in localStorage for use with API calls
        localStorage.setItem('access_token', response.data.access_token);
        // Don't navigate here - let AuthContext handle it
        return response.data;
      } else {
        throw new Error('Sign up failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Sign up failed';
      throw new Error(errorMessage);
    }
  }, []);

  const signOutHandler = useCallback(async () => {
    try {
      // Clear the stored token
      localStorage.removeItem('access_token');
      // Also clear any other auth-related storage
      localStorage.removeItem('refresh_token');
      // Don't navigate here - let AuthContext handle it
    } catch (error) {
      // Even if sign out fails, clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }, []);

  const refreshAuth = useCallback(() => {
    // Session refreshing would happen automatically with JWT
    // In a real implementation, you might want to refresh the token here
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