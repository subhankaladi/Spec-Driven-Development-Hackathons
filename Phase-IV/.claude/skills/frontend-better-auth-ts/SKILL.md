# Frontend Better Auth TypeScript Skill

## Overview
Specialized skill for implementing Better Auth on the frontend with TypeScript. Better Auth is a modern, framework-agnostic authentication library that provides type-safe authentication with minimal configuration.

## Core Capabilities

### 1. Better Auth Client Setup
- Configure type-safe auth client
- Initialize Better Auth with proper TypeScript types
- Set up authentication providers (OAuth, Email, etc.)
- Configure session management
- Handle client-side routing protection

### 2. Authentication Flows
- Email/password authentication
- OAuth providers (Google, GitHub, Discord, etc.)
- Magic link authentication
- Two-factor authentication (2FA)
- Email verification
- Password reset flows

### 3. Session Management
- Access user session data with type safety
- Handle session refresh automatically
- Implement session persistence
- Handle session expiration
- Clear sessions on logout

### 4. Protected Routes & Components
- Create route guards for protected pages
- Implement loading states during auth checks
- Handle unauthorized access
- Redirect logic after authentication
- Role-based UI rendering

## Installation & Setup

### Install Better Auth
```bash
npm install better-auth
# or
pnpm add better-auth
# or
yarn add better-auth
```

### Basic Client Configuration
```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000",
  // Optional: customize session storage
  storage: {
    type: "cookie", // or "localStorage"
    cookieOptions: {
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    },
  },
})

// Export typed auth methods
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient
```

## Framework-Specific Implementations

### React / Next.js

#### Auth Provider Setup
```typescript
// components/auth-provider.tsx
"use client"

import { SessionProvider } from "better-auth/react"
import { authClient } from "@/lib/auth-client"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider client={authClient}>
      {children}
    </SessionProvider>
  )
}
```

#### Using Session in Components
```typescript
// components/user-menu.tsx
"use client"

import { useSession } from "@/lib/auth-client"
import { signOut } from "@/lib/auth-client"

export function UserMenu() {
  const { data: session, isPending } = useSession()

  if (isPending) {
    return <div>Loading...</div>
  }

  if (!session) {
    return <a href="/login">Sign In</a>
  }

  return (
    <div>
      <p>Welcome, {session.user.name}</p>
      <button onClick={() => signOut()}>
        Sign Out
      </button>
    </div>
  )
}
```

#### Protected Route Component
```typescript
// components/protected-route.tsx
"use client"

import { useSession } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data: session, isPending } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login")
    }
  }, [session, isPending, router])

  if (isPending) {
    return <div>Loading...</div>
  }

  if (!session) {
    return null
  }

  return <>{children}</>
}
```

#### Login Form Component
```typescript
// components/login-form.tsx
"use client"

import { useState } from "react"
import { signIn } from "@/lib/auth-client"
import { useRouter } from "next/navigation"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const result = await signIn.email({
        email,
        password,
      })

      if (result.error) {
        setError(result.error.message)
      } else {
        router.push("/dashboard")
      }
    } catch (err) {
      setError("An unexpected error occurred")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? "Signing in..." : "Sign In"}
      </button>
    </form>
  )
}
```

#### OAuth Sign In
```typescript
// components/oauth-buttons.tsx
"use client"

import { signIn } from "@/lib/auth-client"

export function OAuthButtons() {
  const handleOAuthSignIn = async (provider: "google" | "github") => {
    await signIn.social({
      provider,
      callbackURL: "/dashboard",
    })
  }

  return (
    <div>
      <button onClick={() => handleOAuthSignIn("google")}>
        Sign in with Google
      </button>
      <button onClick={() => handleOAuthSignIn("github")}>
        Sign in with GitHub
      </button>
    </div>
  )
}
```

### Vue.js

#### Setup Composable
```typescript
// composables/useAuth.ts
import { ref, computed } from "vue"
import { authClient } from "@/lib/auth-client"

export function useAuth() {
  const session = ref(null)
  const loading = ref(true)

  const isAuthenticated = computed(() => !!session.value)

  const loadSession = async () => {
    try {
      session.value = await authClient.getSession()
    } finally {
      loading.value = false
    }
  }

  const signIn = async (email: string, password: string) => {
    const result = await authClient.signIn.email({ email, password })
    if (!result.error) {
      session.value = result.data
    }
    return result
  }

  const signOut = async () => {
    await authClient.signOut()
    session.value = null
  }

  return {
    session,
    loading,
    isAuthenticated,
    loadSession,
    signIn,
    signOut,
  }
}
```

### Svelte

#### Auth Store
```typescript
// stores/auth.ts
import { writable } from "svelte/store"
import { authClient } from "@/lib/auth-client"

function createAuthStore() {
  const { subscribe, set, update } = writable({
    session: null,
    loading: true,
  })

  return {
    subscribe,
    loadSession: async () => {
      const session = await authClient.getSession()
      set({ session, loading: false })
    },
    signIn: async (email: string, password: string) => {
      const result = await authClient.signIn.email({ email, password })
      if (!result.error) {
        update(state => ({ ...state, session: result.data }))
      }
      return result
    },
    signOut: async () => {
      await authClient.signOut()
      set({ session: null, loading: false })
    },
  }
}

export const auth = createAuthStore()
```

## Advanced Patterns

### Role-Based Access Control
```typescript
// hooks/useAuthorization.ts
import { useSession } from "@/lib/auth-client"

type Role = "admin" | "user" | "moderator"

export function useAuthorization() {
  const { data: session } = useSession()

  const hasRole = (role: Role | Role[]) => {
    if (!session?.user) return false
    
    const userRoles = session.user.roles || []
    const rolesToCheck = Array.isArray(role) ? role : [role]
    
    return rolesToCheck.some(r => userRoles.includes(r))
  }

  const hasPermission = (permission: string) => {
    if (!session?.user) return false
    
    const userPermissions = session.user.permissions || []
    return userPermissions.includes(permission)
  }

  return {
    hasRole,
    hasPermission,
    isAdmin: hasRole("admin"),
    isModerator: hasRole("moderator"),
  }
}
```

### Conditional Rendering Component
```typescript
// components/can.tsx
import { useAuthorization } from "@/hooks/useAuthorization"

interface CanProps {
  role?: string | string[]
  permission?: string
  fallback?: React.ReactNode
  children: React.ReactNode
}

export function Can({ role, permission, fallback = null, children }: CanProps) {
  const { hasRole, hasPermission } = useAuthorization()

  const isAuthorized = role 
    ? hasRole(role as any)
    : permission 
    ? hasPermission(permission)
    : false

  return isAuthorized ? <>{children}</> : <>{fallback}</>
}

// Usage:
// <Can role="admin">
//   <AdminPanel />
// </Can>
```

### Server-Side Session Validation (Next.js)
```typescript
// lib/auth-server.ts
import { cookies } from "next/headers"
import { authClient } from "./auth-client"

export async function getServerSession() {
  const cookieStore = cookies()
  const sessionToken = cookieStore.get("session")?.value

  if (!sessionToken) {
    return null
  }

  try {
    const session = await authClient.getSession()
    return session
  } catch {
    return null
  }
}

// Usage in Server Components:
// const session = await getServerSession()
```

### Middleware for Protected Routes (Next.js)
```typescript
// middleware.ts
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export async function middleware(request: NextRequest) {
  const session = request.cookies.get("session")

  // Protected routes
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url))
    }
  }

  // Auth routes (redirect if logged in)
  if (request.nextUrl.pathname.startsWith("/login")) {
    if (session) {
      return NextResponse.redirect(new URL("/dashboard", request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/signup"],
}
```

## TypeScript Types & Interfaces

### Extend Session Types
```typescript
// types/auth.ts
import "better-auth"

declare module "better-auth" {
  interface Session {
    user: {
      id: string
      email: string
      name: string
      image?: string
      emailVerified: boolean
      roles?: string[]
      permissions?: string[]
    }
  }
}
```

## Best Practices

### 1. Error Handling
```typescript
const handleAuth = async () => {
  try {
    const result = await signIn.email({ email, password })
    
    if (result.error) {
      // Handle specific errors
      switch (result.error.code) {
        case "INVALID_CREDENTIALS":
          setError("Invalid email or password")
          break
        case "EMAIL_NOT_VERIFIED":
          setError("Please verify your email first")
          break
        default:
          setError("Authentication failed")
      }
    }
  } catch (err) {
    setError("An unexpected error occurred")
    console.error(err)
  }
}
```

### 2. Loading States
```typescript
function AuthButton() {
  const { data: session, isPending } = useSession()
  const [isLoading, setIsLoading] = useState(false)

  if (isPending) {
    return <Spinner />
  }

  return session ? (
    <button 
      onClick={() => {
        setIsLoading(true)
        signOut().finally(() => setIsLoading(false))
      }}
      disabled={isLoading}
    >
      {isLoading ? "Signing out..." : "Sign Out"}
    </button>
  ) : (
    <a href="/login">Sign In</a>
  )
}
```

### 3. Optimistic Updates
```typescript
const handleSignOut = async () => {
  // Optimistically update UI
  queryClient.setQueryData(["session"], null)
  
  try {
    await signOut()
    router.push("/")
  } catch (error) {
    // Rollback on error
    queryClient.invalidateQueries(["session"])
  }
}
```

### 4. Persist Redirect Path
```typescript
// Store intended destination before redirecting to login
const login = () => {
  const returnUrl = window.location.pathname
  sessionStorage.setItem("returnUrl", returnUrl)
  router.push(`/login?returnUrl=${encodeURIComponent(returnUrl)}`)
}

// After successful login
const returnUrl = sessionStorage.getItem("returnUrl") || "/dashboard"
sessionStorage.removeItem("returnUrl")
router.push(returnUrl)
```

## Security Considerations

1. **CSRF Protection**: Better Auth handles CSRF tokens automatically
2. **Secure Cookies**: Always use `secure: true` in production
3. **XSS Prevention**: Never store sensitive tokens in localStorage
4. **Session Timeout**: Implement automatic session refresh
5. **Rate Limiting**: Implement on login/signup endpoints

## Testing

### Mock Auth for Tests
```typescript
// __mocks__/auth-client.ts
export const mockSession = {
  user: {
    id: "test-user-id",
    email: "test@example.com",
    name: "Test User",
  },
}

export const useSession = jest.fn(() => ({
  data: mockSession,
  isPending: false,
}))

export const signIn = {
  email: jest.fn(),
  social: jest.fn(),
}

export const signOut = jest.fn()
```

---

**When to use this skill:**
- Implementing authentication in React/Next.js/Vue/Svelte apps
- Building type-safe authentication flows
- Creating protected routes and components
- Integrating OAuth providers
- Managing user sessions on the frontend
- Implementing role-based access control
- Building authentication UI components