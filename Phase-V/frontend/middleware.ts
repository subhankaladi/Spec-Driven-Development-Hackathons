// T022: Middleware for route protection

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  // Check if trying to access protected routes
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/tasks');

  // If protected route and no token, redirect to signin
  if (isProtectedRoute && !token) {
    // Check localStorage via client-side (this will be handled by AuthContext)
    // Middleware can't access localStorage, so we redirect
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
  matcher: ['/tasks/:path*', '/signin', '/signup'],
};
