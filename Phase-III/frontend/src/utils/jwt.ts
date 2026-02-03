/**
 * JWT Token Management Utility
 *
 * Handles JWT token retrieval, expiration checking, and refresh logic.
 * Tokens are stored in httpOnly cookies by the backend.
 */

/**
 * Decode JWT token payload (without verification)
 * Used for reading expiration time and user info
 */
function decodeJWT(token: string): { exp?: number; [key: string]: unknown } | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

/**
 * Get JWT token from httpOnly cookie (via document.cookie if accessible)
 * Note: httpOnly cookies are NOT accessible via JavaScript for security.
 * This function attempts to read non-httpOnly JWT if present, but
 * the primary authentication method uses httpOnly cookies sent automatically.
 */
export function getJWTToken(): string | null {
  if (typeof document === 'undefined') return null;

  const cookies = document.cookie.split('; ');
  // Check both possible cookie names
  const jwtCookie = cookies.find((c) => c.startsWith('access_token=') || c.startsWith('jwt='));

  if (!jwtCookie) return null;

  return jwtCookie.split('=')[1];
}

/**
 * Check if JWT token is expired
 * Returns true if token is expired or invalid
 */
export function isTokenExpired(token?: string): boolean {
  const jwt = token || getJWTToken();
  if (!jwt) return true;

  const decoded = decodeJWT(jwt);
  if (!decoded || !decoded.exp) return true;

  // Check if token expires within next 60 seconds (1 minute buffer)
  const expirationTime = decoded.exp * 1000; // Convert to milliseconds
  const currentTime = Date.now();
  const bufferTime = 60 * 1000; // 1 minute

  return currentTime + bufferTime >= expirationTime;
}

/**
 * Setup automatic token refresh
 * Calls onExpire callback when token is about to expire
 */
export function setupTokenRefresh(onExpire: () => void): () => void {
  const checkInterval = 60 * 1000; // Check every minute

  const intervalId = setInterval(() => {
    if (isTokenExpired()) {
      onExpire();
    }
  }, checkInterval);

  // Return cleanup function
  return () => clearInterval(intervalId);
}

/**
 * Get token from httpOnly cookie (server-side safe)
 * This is a placeholder - actual token retrieval happens via
 * credentials: 'include' in fetch requests
 */
export function getTokenFromCookie(): string | null {
  // In production, httpOnly cookies are sent automatically with fetch
  // This function is for compatibility and potential fallback scenarios
  return getJWTToken();
}

/**
 * Check if user is authenticated
 * Returns true if valid, non-expired token exists
 */
export function isAuthenticated(): boolean {
  const token = getJWTToken();
  return token !== null && !isTokenExpired(token);
}

/**
 * Parse user info from JWT token
 */
export function getUserFromToken(token?: string): { userId?: string; email?: string } | null {
  const jwt = token || getJWTToken();
  if (!jwt) return null;

  const decoded = decodeJWT(jwt);
  if (!decoded) return null;

  return {
    userId: decoded.sub as string | undefined,
    email: decoded.email as string | undefined,
  };
}
