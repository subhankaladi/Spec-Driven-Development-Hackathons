/**
 * Integration Tests: AuthGuard Component
 *
 * Tests authentication guard functionality and redirects
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { AuthGuard } from '../AuthGuard';
import * as jwtUtils from '@/utils/jwt';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/utils/jwt', () => ({
  isAuthenticated: jest.fn(),
}));

const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockIsAuthenticated = jwtUtils.isAuthenticated as jest.MockedFunction<
  typeof jwtUtils.isAuthenticated
>;

describe('AuthGuard - JWT Authentication Integration', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      prefetch: jest.fn(),
    } as any);
  });

  describe('Authenticated Users', () => {
    it('should render children when user is authenticated', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Protected Content')).toBeInTheDocument();
      });
    });

    it('should not redirect when user is authenticated', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(mockPush).not.toHaveBeenCalled();
      });
    });

    it('should not show loading state after authentication check', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(screen.queryByText('Checking authentication...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Unauthenticated Users', () => {
    it('should redirect to signin when user is not authenticated', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/signin');
      });
    });

    it('should not render children when user is not authenticated', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
      });
    });

    it('should show loading state before redirect', () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert - Loading state should appear briefly
      expect(screen.getByText('Checking authentication...')).toBeInTheDocument();
    });
  });

  describe('Custom Fallback', () => {
    it('should render custom fallback during loading', () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);
      const customFallback = <div>Custom Loading...</div>;

      // Act
      render(
        <AuthGuard fallback={customFallback}>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      expect(screen.getByText('Custom Loading...')).toBeInTheDocument();
    });

    it('should not render custom fallback after authentication check', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);
      const customFallback = <div>Custom Loading...</div>;

      // Act
      render(
        <AuthGuard fallback={customFallback}>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(screen.queryByText('Custom Loading...')).not.toBeInTheDocument();
      });
    });
  });

  describe('JWT Token Validation', () => {
    it('should call isAuthenticated from jwt utils', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(mockIsAuthenticated).toHaveBeenCalled();
      });
    });

    it('should handle expired JWT tokens', async () => {
      // Arrange - Simulate expired token
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert - Should redirect to signin
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/signin');
      });
    });

    it('should handle missing JWT tokens', async () => {
      // Arrange - Simulate no token
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert - Should redirect to signin
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/signin');
      });
    });
  });

  describe('Loading State', () => {
    it('should show default loading spinner during authentication check', () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      const spinner = screen.getByText('Checking authentication...').previousSibling;
      expect(spinner).toHaveClass('animate-spin');
    });

    it('should display loading message', () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(false);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      expect(screen.getByText('Checking authentication...')).toBeInTheDocument();
    });
  });

  describe('Component Lifecycle', () => {
    it('should check authentication on mount', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert
      await waitFor(() => {
        expect(mockIsAuthenticated).toHaveBeenCalledTimes(1);
      });
    });

    it('should not re-check authentication on re-render', async () => {
      // Arrange
      mockIsAuthenticated.mockReturnValue(true);

      // Act
      const { rerender } = render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      await waitFor(() => {
        expect(screen.getByText('Protected Content')).toBeInTheDocument();
      });

      // Re-render
      rerender(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Assert - Should only call once on initial mount
      expect(mockIsAuthenticated).toHaveBeenCalledTimes(1);
    });
  });
});
