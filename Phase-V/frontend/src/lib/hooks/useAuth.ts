// T021: useAuth custom hook

'use client';

import { useAuth as useAuthContext } from '@/context/AuthContext';

// Re-export useAuth from AuthContext for convenience
export const useAuth = useAuthContext;
