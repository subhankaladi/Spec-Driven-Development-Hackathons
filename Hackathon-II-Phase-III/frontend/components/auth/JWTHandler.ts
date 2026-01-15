/**
 * JWT authentication handler for the chat interface
 * Handles JWT token validation, decoding, and attachment to requests
 */

import { jwtDecode, JwtPayload } from 'jwt-decode';

export interface DecodedToken extends JwtPayload {
  user_id?: string;
  exp?: number;
  iat?: number;
}

export class JWTHandler {
  private static readonly TOKEN_KEY = 'chat_jwt_token';

  /**
   * Store the JWT token in browser storage
   */
  static storeToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  /**
   * Retrieve the JWT token from browser storage
   */
  static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  /**
   * Remove the JWT token from browser storage
   */
  static removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  /**
   * Decode the JWT token to extract user information
   */
  static decodeToken(token: string): DecodedToken | null {
    try {
      return jwtDecode<DecodedToken>(token);
    } catch (error) {
      console.error('Failed to decode JWT token:', error);
      return null;
    }
  }

  /**
   * Check if the token is expired
   */
  static isTokenExpired(token: string): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return true; // If there's no expiration, consider it expired
    }

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  }

  /**
   * Get the user ID from the token
   */
  static getUserIdFromToken(token: string): string | null {
    const decoded = this.decodeToken(token);
    return decoded?.user_id || null;
  }

  /**
   * Validate the token (check if exists and not expired)
   */
  static isValidToken(): boolean {
    const token = this.getToken();
    if (!token) {
      return false;
    }
    return !this.isTokenExpired(token);
  }

  /**
   * Get the Authorization header with the JWT token
   */
  static getAuthHeader(): { Authorization: string } | null {
    const token = this.getToken();
    if (!token || this.isTokenExpired(token)) {
      return null;
    }
    return { Authorization: `Bearer ${token}` };
  }

  /**
   * Attach JWT token to a fetch request options object
   */
  static attachTokenToRequest(init?: RequestInit): RequestInit {
    const authHeader = this.getAuthHeader();
    if (!authHeader) {
      throw new Error('No valid JWT token available for request');
    }

    return {
      ...init,
      headers: {
        ...init?.headers,
        ...authHeader,
        'Content-Type': 'application/json',
      },
    };
  }
}