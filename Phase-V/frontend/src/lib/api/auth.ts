// T018: Auth API methods - Updated for BetterAuth

import { signIn as betterAuthSignIn, signOut as betterAuthSignOut } from '@/lib/auth/client';
import apiClient from './client';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
  token_type: string;
}

export async function signUp(email: string, password: string): Promise<any> {
  // For compatibility with existing code, make an API call to our backend
  // BetterAuth handles the session management, but we need to return the expected format
  const response = await apiClient.post('/auth/auth/signup', {
    email,
    password,
  });

  // Use BetterAuth to initialize the session
  const result = await betterAuthSignIn.email({
    email,
    password,
    callbackURL: '/tasks',
  });

  if (result?.error) {
    throw new Error(result.error.message || 'Sign up failed');
  }

  return response.data;
}

export async function signIn(email: string, password: string): Promise<any> {
  // For compatibility with existing code, make an API call to our backend
  const response = await apiClient.post('/auth/auth/signin', {
    email,
    password,
  });

  // Use BetterAuth to initialize the session
  const result = await betterAuthSignIn.email({
    email,
    password,
    callbackURL: '/tasks',
  });

  if (result?.error) {
    throw new Error(result.error.message || 'Sign in failed');
  }

  return response.data;
}

export async function refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
  // With BetterAuth, token refresh is handled automatically
  // This function is maintained for compatibility but may not be needed
  throw new Error('Token refresh is handled automatically by BetterAuth');
}

export async function signOut(refreshToken: string | null): Promise<{ message: string }> {
  // Call the backend to invalidate the session
  try {
    await apiClient.post('/auth/signout', {
      refresh_token: refreshToken || '',
    });
  } catch (error) {
    // Continue with signout even if backend call fails
    console.error('Signout error:', error);
  }

  // Use BetterAuth to clear the session
  await betterAuthSignOut();
  return { message: 'Signed out successfully' };
}
