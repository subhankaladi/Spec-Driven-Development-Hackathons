// Middleware for route protection and domain validation

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Validate domain allowlist
 * Returns true if domain is allowed, false otherwise
 */
function isAllowedDomain(request: NextRequest): boolean {
  const environment = process.env.NEXT_PUBLIC_ENVIRONMENT || 'development';

  // Development: Allow all domains
  if (environment === 'development') {
    return true;
  }

  const hostname = request.nextUrl.hostname;
  const allowedDomainsEnv = process.env.NEXT_PUBLIC_ALLOWED_DOMAINS || '';

  if (!allowedDomainsEnv) {
    console.warn('NEXT_PUBLIC_ALLOWED_DOMAINS not set for production');
    return false;
  }

  const allowedDomains = allowedDomainsEnv.split(',').map((d) => d.trim());

  // Check exact match
  if (allowedDomains.includes(hostname)) {
    return true;
  }

  // Check wildcard subdomain (*.example.com)
  return allowedDomains.some((allowed) => {
    if (allowed.startsWith('*.')) {
      const baseDomain = allowed.slice(2);
      return hostname.endsWith(`.${baseDomain}`) || hostname === baseDomain;
    }
    return false;
  });
}

export function middleware(request: NextRequest) {
  // 1. Domain Allowlist Validation
  if (!isAllowedDomain(request)) {
    return new NextResponse(
      `<html><body style="font-family: sans-serif; padding: 2rem; text-align: center;">
        <h1>Access Denied</h1>
        <p>This application is not available on this domain.</p>
        <p><small>Domain: ${request.nextUrl.hostname}</small></p>
      </body></html>`,
      {
        status: 403,
        headers: { 'Content-Type': 'text/html' },
      }
    );
  }

  // 2. Authentication Check
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  // Check if trying to access protected routes (tasks or chat)
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/tasks') ||
                           request.nextUrl.pathname.startsWith('/chat');

  // If protected route and no token, redirect to signin
  if (isProtectedRoute && !token) {
    const signInUrl = new URL('/signin', request.url);
    return NextResponse.redirect(signInUrl);
  }

  // If on signin/signup page and has token, redirect to tasks
  const isAuthRoute = request.nextUrl.pathname.startsWith('/signin') ||
                      request.nextUrl.pathname.startsWith('/signup');

  if (isAuthRoute && token) {
    const tasksUrl = new URL('/tasks', request.url);
    return NextResponse.redirect(tasksUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/tasks/:path*', '/chat/:path*', '/signin', '/signup'],
};
