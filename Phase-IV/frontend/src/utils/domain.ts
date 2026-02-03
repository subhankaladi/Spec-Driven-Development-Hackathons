/**
 * Domain Validation Utility
 *
 * Validates that the application is running on an allowlisted domain.
 * Required for production deployment with OpenAI domain key configuration.
 */

/**
 * Get allowed domains from environment configuration
 * In development, all domains are allowed
 * In production, only domains specified in NEXT_PUBLIC_ALLOWED_DOMAINS are permitted
 */
export function getAllowedDomains(): string[] {
  const environment = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';

  // Development: Allow all domains (localhost, 127.0.0.1, etc.)
  if (environment === 'development') {
    return ['localhost', '127.0.0.1', '[::1]'];
  }

  // Production: Read from environment variable
  // Format: "example.com,app.example.com,www.example.com"
  const allowedDomainsEnv = process.env.NEXT_PUBLIC_ALLOWED_DOMAINS || '';

  if (!allowedDomainsEnv) {
    console.warn('NEXT_PUBLIC_ALLOWED_DOMAINS not set for production environment');
    return [];
  }

  return allowedDomainsEnv.split(',').map((domain) => domain.trim());
}

/**
 * Get current domain (hostname) from window.location
 * Returns null in server-side context
 */
export function getCurrentDomain(): string | null {
  if (typeof window === 'undefined') return null;

  return window.location.hostname;
}

/**
 * Check if current domain is in the allowlist
 * Returns true in development or if domain matches allowlist
 */
export function isAllowedDomain(): boolean {
  const environment = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';

  // Development: Always allow
  if (environment === 'development') {
    return true;
  }

  const currentDomain = getCurrentDomain();
  if (!currentDomain) return false; // Server-side or invalid context

  const allowedDomains = getAllowedDomains();

  // Check exact match
  if (allowedDomains.includes(currentDomain)) {
    return true;
  }

  // Check wildcard subdomain match (e.g., *.example.com)
  const wildcardMatch = allowedDomains.some((allowed) => {
    if (allowed.startsWith('*.')) {
      const baseDomain = allowed.slice(2); // Remove "*."
      return currentDomain.endsWith(`.${baseDomain}`) || currentDomain === baseDomain;
    }
    return false;
  });

  return wildcardMatch;
}

/**
 * Validate domain and return error message if invalid
 * Returns null if domain is valid
 */
export function validateDomainAllowlist(): string | null {
  if (isAllowedDomain()) {
    return null;
  }

  const currentDomain = getCurrentDomain();
  const environment = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';

  return `Access denied: This application is not available on domain "${currentDomain}". Environment: ${environment}`;
}

/**
 * Get OpenAI domain key from environment
 * Required for production deployment
 */
export function getOpenAIDomainKey(): string | null {
  return process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || null;
}

/**
 * Check if OpenAI domain key is configured
 * Required in production, optional in development
 */
export function isOpenAIDomainKeyConfigured(): boolean {
  const environment = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';

  if (environment === 'development') {
    return true; // Not required in development
  }

  return getOpenAIDomainKey() !== null;
}
