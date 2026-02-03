// T020: AuthContext with AuthContextProvider - Updated for BetterAuth

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthState, AuthContextType } from '@/types/auth';
import { useBetterAuth } from '@/hooks/useBetterAuth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper function to decode JWT token
function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error parsing JWT token:', error);
    return null;
  }
}

export function AuthContextProvider({ children }: { children: ReactNode }) {
  const authHook = useBetterAuth();
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false,
  });
  const router = useRouter();

  // Check for existing token on initial load and decode user info
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const decoded = parseJwt(token);
      if (decoded) {
        const user: User = {
          id: decoded.sub,
          email: decoded.email,
          token: token
        };
        setAuthState({
          user,
          loading: false,
          error: null,
          isAuthenticated: true
        });
      }
    }
  }, []);

  const signIn = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      await authHook.signIn(email, password);

      // After successful sign in, get the token and decode user info
      const token = localStorage.getItem('access_token');
      if (token) {
        const decoded = parseJwt(token);
        if (decoded) {
          const user: User = {
            id: decoded.sub,
            email: decoded.email,
            token: token
          };
          setAuthState({
            user,
            loading: false,
            error: null,
            isAuthenticated: true
          });
        }
      }
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Sign in failed',
        isAuthenticated: false,
        user: null
      }));
      throw error;
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      await authHook.signUp(email, password);

      // After successful sign up, get the token and decode user info
      const token = localStorage.getItem('access_token');
      if (token) {
        const decoded = parseJwt(token);
        if (decoded) {
          const user: User = {
            id: decoded.sub,
            email: decoded.email,
            token: token
          };
          setAuthState({
            user,
            loading: false,
            error: null,
            isAuthenticated: true
          });
        }
      }
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Sign up failed',
        isAuthenticated: false,
        user: null
      }));
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await authHook.signOut();
      setAuthState({
        user: null,
        loading: false,
        error: null,
        isAuthenticated: false
      });
      router.push('/signin');
    } catch (error) {
      console.error('Sign out error:', error);
      // Even if sign out fails, clear local state
      setAuthState({
        user: null,
        loading: false,
        error: null,
        isAuthenticated: false
      });
      router.push('/signin');
    }
  };

  const refreshAuth = async () => {
    // In a real implementation, you might want to validate the token
    // This function is maintained for compatibility
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        signIn,
        signUp,
        signOut,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthContextProvider');
  }
  return context;
}
