// T011: Auth type definitions

export interface User {
  id: string;           // UUID from JWT sub claim
  email: string;        // User's email address
  token?: string;       // JWT access token (optional for BetterAuth compatibility)
}

export interface AuthState {
  user: User | null;           // Current authenticated user (null = not logged in)
  loading: boolean;            // Auth check in progress
  error: string | null;        // Last auth error message
  isAuthenticated: boolean;    // Computed: user !== null
}

export interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

export interface SignInFormState {
  email: string;
  password: string;
  errors: {
    email?: string;
    password?: string;
    general?: string;
  };
  touched: {
    email: boolean;
    password: boolean;
  };
  isSubmitting: boolean;
}

export interface SignUpFormState {
  email: string;
  password: string;
  confirmPassword: string;
  errors: {
    email?: string;
    password?: string;
    confirmPassword?: string;
    general?: string;
  };
  touched: {
    email: boolean;
    password: boolean;
    confirmPassword: boolean;
  };
  isSubmitting: boolean;
}
