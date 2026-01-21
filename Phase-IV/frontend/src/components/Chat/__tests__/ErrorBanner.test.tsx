/**
 * Unit Tests: ErrorBanner Component
 *
 * Tests error display, retry functionality, and accessibility
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBanner, CompactErrorBanner } from '../ErrorBanner';
import type { ErrorMessage } from '@/types/chat';

describe('ErrorBanner', () => {
  const mockError: ErrorMessage = {
    code: 'NETWORK_ERROR',
    message: 'Connection failed',
    suggestion: 'Check your internet connection',
  };

  const mockRetry = jest.fn();
  const mockClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render error message', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });

    it('should render error suggestion', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.getByText('Check your internet connection')).toBeInTheDocument();
    });

    it('should render error code in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(<ErrorBanner error={mockError} />);

      expect(screen.getByText(/Error code: NETWORK_ERROR/)).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not render error code in production', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      render(<ErrorBanner error={mockError} />);

      expect(screen.queryByText(/Error code:/)).not.toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Visibility Control', () => {
    it('should render when show is true', () => {
      render(<ErrorBanner error={mockError} show={true} />);

      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });

    it('should not render when show is false', () => {
      render(<ErrorBanner error={mockError} show={false} />);

      expect(screen.queryByText('Connection failed')).not.toBeInTheDocument();
    });

    it('should render by default (show not specified)', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should render retry button when onRetry provided', () => {
      render(<ErrorBanner error={mockError} onRetry={mockRetry} />);

      expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
    });

    it('should not render retry button when onRetry not provided', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.queryByRole('button', { name: /Retry/i })).not.toBeInTheDocument();
    });

    it('should call onRetry when retry button clicked', () => {
      render(<ErrorBanner error={mockError} onRetry={mockRetry} />);

      const retryButton = screen.getByRole('button', { name: /Retry/i });
      fireEvent.click(retryButton);

      expect(mockRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Close/Dismiss Functionality', () => {
    it('should render close button when onClose provided', () => {
      render(<ErrorBanner error={mockError} onClose={mockClose} />);

      expect(screen.getByRole('button', { name: /Dismiss error/i })).toBeInTheDocument();
    });

    it('should not render close button when onClose not provided', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.queryByRole('button', { name: /Dismiss error/i })).not.toBeInTheDocument();
    });

    it('should call onClose when close button clicked', () => {
      render(<ErrorBanner error={mockError} onClose={mockClose} />);

      const closeButton = screen.getByRole('button', { name: /Dismiss error/i });
      fireEvent.click(closeButton);

      expect(mockClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Position Variants', () => {
    it('should render with inline position (default)', () => {
      const { container } = render(<ErrorBanner error={mockError} position="inline" />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('relative');
    });

    it('should render with top position', () => {
      const { container } = render(<ErrorBanner error={mockError} position="top" />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('fixed', 'top-0');
    });

    it('should render with bottom position', () => {
      const { container } = render(<ErrorBanner error={mockError} position="bottom" />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('fixed', 'bottom-0');
    });
  });

  describe('Severity Styling', () => {
    it('should render error severity for network errors', () => {
      const { container } = render(<ErrorBanner error={mockError} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('bg-red-50', 'border-red-200');
    });

    it('should render warning severity for auth errors', () => {
      const authError: ErrorMessage = {
        code: 'AUTH_EXPIRED',
        message: 'Session expired',
        suggestion: 'Please log in again',
      };

      const { container } = render(<ErrorBanner error={authError} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('bg-yellow-50', 'border-yellow-200');
    });

    it('should render warning severity for rate limit errors', () => {
      const rateLimitError: ErrorMessage = {
        code: 'RATE_LIMITED',
        message: 'Too many requests',
        suggestion: 'Please slow down',
      };

      const { container } = render(<ErrorBanner error={rateLimitError} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('bg-yellow-50', 'border-yellow-200');
    });

    it('should render info severity for other errors', () => {
      const infoError: ErrorMessage = {
        code: 'NOT_FOUND',
        message: 'Not found',
        suggestion: 'Try a different search',
      };

      const { container } = render(<ErrorBanner error={infoError} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('bg-blue-50', 'border-blue-200');
    });
  });

  describe('Accessibility', () => {
    it('should have role="alert"', () => {
      render(<ErrorBanner error={mockError} />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should have aria-live="assertive"', () => {
      render(<ErrorBanner error={mockError} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
    });

    it('should have aria-atomic="true"', () => {
      render(<ErrorBanner error={mockError} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-atomic', 'true');
    });

    it('should have aria-label on retry button', () => {
      render(<ErrorBanner error={mockError} onRetry={mockRetry} />);

      const retryButton = screen.getByRole('button', { name: /Retry action/i });
      expect(retryButton).toBeInTheDocument();
    });

    it('should have aria-label on close button', () => {
      render(<ErrorBanner error={mockError} onClose={mockClose} />);

      const closeButton = screen.getByRole('button', { name: /Dismiss error/i });
      expect(closeButton).toBeInTheDocument();
    });

    it('should have aria-hidden on icon', () => {
      const { container } = render(<ErrorBanner error={mockError} />);

      const icon = container.querySelector('svg');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Icon Display', () => {
    it('should render error icon for network errors', () => {
      const { container } = render(<ErrorBanner error={mockError} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should render warning icon for auth errors', () => {
      const authError: ErrorMessage = {
        code: 'AUTH_EXPIRED',
        message: 'Session expired',
        suggestion: 'Please log in again',
      };

      const { container } = render(<ErrorBanner error={authError} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<ErrorBanner error={mockError} className="custom-class" />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('custom-class');
    });
  });
});

describe('CompactErrorBanner', () => {
  const mockError: ErrorMessage = {
    code: 'NETWORK_ERROR',
    message: 'Connection failed',
    suggestion: 'Check your connection',
  };

  const mockRetry = jest.fn();
  const mockClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render error message', () => {
      render(<CompactErrorBanner error={mockError} />);

      expect(screen.getByText('Connection failed')).toBeInTheDocument();
    });

    it('should render with compact styling', () => {
      const { container } = render(<CompactErrorBanner error={mockError} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('bg-red-50', 'border-red-200');
    });

    it('should have role="alert"', () => {
      render(<CompactErrorBanner error={mockError} />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should render retry button when onRetry provided', () => {
      render(<CompactErrorBanner error={mockError} onRetry={mockRetry} />);

      expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
    });

    it('should call onRetry when retry button clicked', () => {
      render(<CompactErrorBanner error={mockError} onRetry={mockRetry} />);

      const retryButton = screen.getByRole('button', { name: /Retry/i });
      fireEvent.click(retryButton);

      expect(mockRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Close Functionality', () => {
    it('should render close button when onClose provided', () => {
      render(<CompactErrorBanner error={mockError} onClose={mockClose} />);

      const closeButtons = screen.getAllByRole('button');
      expect(closeButtons.length).toBeGreaterThanOrEqual(1);
    });

    it('should call onClose when close button clicked', () => {
      render(<CompactErrorBanner error={mockError} onClose={mockClose} />);

      const buttons = screen.getAllByRole('button');
      const closeButton = buttons[buttons.length - 1]; // Last button should be close

      fireEvent.click(closeButton);

      expect(mockClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Icon Display', () => {
    it('should render error icon', () => {
      const { container } = render(<CompactErrorBanner error={mockError} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });
});
