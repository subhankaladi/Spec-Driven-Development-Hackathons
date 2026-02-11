// T022: Middleware for route protection - Updated for JWT localStorage approach

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // For JWT stored in localStorage, we can't access it in middleware
  // So we'll allow all routes to pass through and handle auth on the client side
  // However, if there's an Authorization header, we can still check that for API routes
  
  const authHeader = request.headers.get('authorization');
  const hasBearerToken = authHeader && authHeader.startsWith('Bearer ');

  // If on signin/signup page and has token in header, redirect to tasks
  const isAuthRoute = request.nextUrl.pathname.startsWith('/signin') ||
                      request.nextUrl.pathname.startsWith('/signup');

  if (isAuthRoute && hasBearerToken) {
    const tasksUrl = new URL('/tasks', request.url);
    return NextResponse.redirect(tasksUrl);
  }

  // Allow all requests to proceed - authentication will be handled client-side
  // where localStorage can be accessed
  return NextResponse.next();
}

export const config = {
  matcher: ['/signin', '/signup'], // Only check auth routes based on header
};
