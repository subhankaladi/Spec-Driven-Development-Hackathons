// T018: Auth API methods - Updated for JWT-only authentication

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
  // Make an API call to our backend for sign up
  const response = await apiClient.post('/auth/auth/signup', {
    email,
    password,
  });

  return response.data;
}

export async function signIn(email: string, password: string): Promise<any> {
  // Make an API call to our backend for sign in
  const response = await apiClient.post('/auth/auth/signin', {
    email,
    password,
  });

  return response.data;
}

export async function refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
  // Make an API call to our backend to refresh the token
  const response = await apiClient.post('/auth/refresh', {
    refresh_token: refreshToken,
  });

  return response.data;
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
  
  return { message: 'Signed out successfully' };
}
