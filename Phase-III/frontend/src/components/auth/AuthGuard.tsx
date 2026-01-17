/**
 * AuthGuard Component
 *
 * Wraps protected components and ensures user is authenticated.
 * Redirects to login if not authenticated, shows loading state while checking.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    // Check authentication status by calling backend
    const checkAuth = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/me`, {
          method: 'GET',
          credentials: 'include', // Include httpOnly cookies
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          // User is authenticated
          setIsAuth(true);
          setIsChecking(false);
        } else {
          // Not authenticated, redirect to login
          setIsAuth(false);
          setIsChecking(false);
          router.push('/signin');
        }
      } catch (error) {
        // Network error or backend down, redirect to login
        console.error('Auth check failed:', error);
        setIsAuth(false);
        setIsChecking(false);
        router.push('/signin');
      }
    };

    checkAuth();
  }, [router]);

  // Show loading state while checking
  if (isChecking) {
    return (
      fallback || (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-600">Checking authentication...</p>
          </div>
        </div>
      )
    );
  }

  // Don't render children if not authenticated (will redirect)
  if (!isAuth) {
    return null;
  }

  // Render children if authenticated
  return <>{children}</>;
}
