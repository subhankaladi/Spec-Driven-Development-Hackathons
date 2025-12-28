"use client";

import { ReactNode } from "react";
import { useRequireAuth } from "@/hooks/useAuth"
import { LoadingScreen } from "@/components/ui/Spinner";

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const { isReady, isLoading } = useRequireAuth();

  if (isLoading) {
    return fallback || <LoadingScreen message="Checking authentication..." />;
  }

  if (!isReady) {
    // Redirect is handled by useRequireAuth, show loading in meantime
    return fallback || <LoadingScreen message="Redirecting to sign in..." />;
  }

  return <>{children}</>;
}
