/**
 * Integration Tests: ReAuthenticationModal Component
 *
 * Tests re-authentication modal display and user interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { ReAuthenticationModal } from '../ReAuthenticationModal';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('ReAuthenticationModal - JWT Session Expiry', () => {
  const mockPush = jest.fn();
  const mockOnClose = jest.fn();

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

  describe('Modal Visibility', () => {
    it('should render modal when show is true', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Session Expired')).toBeInTheDocument();
    });

    it('should not render modal when show is false', () => {
      // Act
      render(<ReAuthenticationModal show={false} onClose={mockOnClose} />);

      // Assert
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(screen.queryByText('Session Expired')).not.toBeInTheDocument();
    });
  });

  describe('Modal Content', () => {
    it('should display session expired title', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(screen.getByText('Session Expired')).toBeInTheDocument();
    });

    it('should display explanatory message', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(
        screen.getByText(/Your session has expired for security reasons/i)
      ).toBeInTheDocument();
    });

    it('should display Stay Here button', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(screen.getByRole('button', { name: /Stay Here/i })).toBeInTheDocument();
    });

    it('should display Log In button', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(screen.getByRole('button', { name: /Log In/i })).toBeInTheDocument();
    });

    it('should display warning icon', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      const icon = screen.getByRole('dialog').querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display additional info about unsent messages', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(
        screen.getByText(/Your unsent messages will be saved/i)
      ).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should redirect to signin when Log In button is clicked', async () => {
      // Arrange
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Act
      const loginButton = screen.getByRole('button', { name: /Log In/i });
      fireEvent.click(loginButton);

      // Assert
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/signin');
      });
    });

    it('should call onClose when Stay Here button is clicked', () => {
      // Arrange
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Act
      const stayButton = screen.getByRole('button', { name: /Stay Here/i });
      fireEvent.click(stayButton);

      // Assert
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when backdrop is clicked', () => {
      // Arrange
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Act
      const backdrop = screen.getByRole('dialog').previousSibling as HTMLElement;
      fireEvent.click(backdrop);

      // Assert
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not call onClose when modal content is clicked', () => {
      // Arrange
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Act
      const modalContent = screen.getByRole('dialog');
      fireEvent.click(modalContent);

      // Assert
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have role="dialog"', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should have aria-modal="true"', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
    });

    it('should have aria-labelledby pointing to title', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      const dialog = screen.getByRole('dialog');
      const title = screen.getByText('Session Expired');
      expect(dialog).toHaveAttribute('aria-labelledby', 'reauth-modal-title');
      expect(title).toHaveAttribute('id', 'reauth-modal-title');
    });

    it('should autofocus Log In button', () => {
      // Act
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert
      const loginButton = screen.getByRole('button', { name: /Log In/i });
      expect(loginButton).toHaveAttribute('autoFocus');
    });

    it('should have backdrop with aria-hidden="true"', () => {
      // Arrange
      const { container } = render(
        <ReAuthenticationModal show={true} onClose={mockOnClose} />
      );

      // Assert
      const backdrop = container.querySelector('.fixed.inset-0.bg-black');
      expect(backdrop).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Modal Behavior', () => {
    it('should not close when undefined onClose is provided and Stay Here is clicked', () => {
      // Act
      render(<ReAuthenticationModal show={true} />);

      const stayButton = screen.getByRole('button', { name: /Stay Here/i });
      fireEvent.click(stayButton);

      // Assert - Modal should still be visible
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should still navigate to signin when Log In is clicked with undefined onClose', async () => {
      // Arrange
      render(<ReAuthenticationModal show={true} />);

      // Act
      const loginButton = screen.getByRole('button', { name: /Log In/i });
      fireEvent.click(loginButton);

      // Assert
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/signin');
      });
    });
  });

  describe('JWT Session Expiry Scenarios', () => {
    it('should handle token expiry during chat message send', () => {
      // Arrange - Simulate showing modal after failed chat message
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert - Modal displays with appropriate message
      expect(screen.getByText('Session Expired')).toBeInTheDocument();
      expect(
        screen.getByText(/Your unsent messages will be saved/i)
      ).toBeInTheDocument();
    });

    it('should handle token expiry during conversation load', () => {
      // Arrange - Simulate showing modal after failed conversation load
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Assert - User can choose to re-authenticate
      expect(screen.getByRole('button', { name: /Log In/i })).toBeInTheDocument();
    });

    it('should allow user to dismiss modal and stay on page', () => {
      // Arrange
      render(<ReAuthenticationModal show={true} onClose={mockOnClose} />);

      // Act
      const stayButton = screen.getByRole('button', { name: /Stay Here/i });
      fireEvent.click(stayButton);

      // Assert - onClose was called, allowing user to stay
      expect(mockOnClose).toHaveBeenCalled();
      expect(mockPush).not.toHaveBeenCalled();
    });
  });

  describe('Visual Styling', () => {
    it('should have backdrop with semi-transparent background', () => {
      // Arrange
      const { container } = render(
        <ReAuthenticationModal show={true} onClose={mockOnClose} />
      );

      // Assert
      const backdrop = container.querySelector('.fixed.inset-0.bg-black.bg-opacity-50');
      expect(backdrop).toBeInTheDocument();
    });

    it('should have correct z-index layering', () => {
      // Arrange
      const { container } = render(
        <ReAuthenticationModal show={true} onClose={mockOnClose} />
      );

      // Assert
      const backdrop = container.querySelector('.z-40');
      const modal = container.querySelector('.z-50');
      expect(backdrop).toBeInTheDocument();
      expect(modal).toBeInTheDocument();
    });

    it('should have warning icon with yellow styling', () => {
      // Arrange
      const { container } = render(
        <ReAuthenticationModal show={true} onClose={mockOnClose} />
      );

      // Assert
      const iconContainer = container.querySelector('.bg-yellow-100');
      expect(iconContainer).toBeInTheDocument();
    });
  });
});
