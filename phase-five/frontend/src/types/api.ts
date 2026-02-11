// T013: API type definitions

export interface ErrorResponse {
  error: {
    code: string;              // Error code (UNAUTHORIZED, INVALID_CREDENTIALS, etc.)
    message: string;           // User-friendly error message
    details: Record<string, any> | null;  // Additional error details
  };
}

export interface SignUpResponse {
  user: {
    id: string;
    email: string;
    created_at: string;
    updated_at: string;
  };
  token: string;
}

export interface SignInResponse {
  token: string;
}
