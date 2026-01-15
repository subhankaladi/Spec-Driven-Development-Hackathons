import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication
const protectedPaths = ["/dashboard"];

// Routes only for unauthenticated users
const authPaths = ["/auth/signin", "/auth/signup"];

// Check if path matches any protected paths
function isProtectedPath(pathname: string): boolean {
  return protectedPaths.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`)
  );
}

// Check if path is an auth path
function isAuthPath(pathname: string): boolean {
  return authPaths.some((path) => pathname === path);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookies (for middleware we can't access localStorage)
  // Better Auth stores token in cookie as well
  const token = request.cookies.get("auth_token")?.value;

  // For protected routes, redirect to sign-in if no token
  if (isProtectedPath(pathname) && !token) {
    const signInUrl = new URL("/auth/signin", request.url);
    signInUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(signInUrl);
  }

  // For auth routes, redirect to dashboard if already authenticated
  if (isAuthPath(pathname) && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
