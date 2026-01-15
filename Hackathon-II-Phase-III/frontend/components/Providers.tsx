"use client";

import { ReactNode } from "react";
import { AuthProvider } from "@/hooks/useAuth"
import { ToastProvider, useToast } from "@/hooks/useToast"
import { ToastContainer } from "@/components/ui/Toast";

function ToastWrapper({ children }: { children: ReactNode }) {
  const { toasts, removeToast } = useToast();

  return (
    <>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>
        <ToastWrapper>{children}</ToastWrapper>
      </ToastProvider>
    </AuthProvider>
  );
}
