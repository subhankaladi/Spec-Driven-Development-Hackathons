/**
 * Unit Tests: LoadingIndicator Component
 *
 * Tests loading spinner rendering and accessibility
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator, LoadingDots, InlineLoadingSpinner } from '../LoadingIndicator';

describe('LoadingIndicator', () => {
  describe('Basic Rendering', () => {
    it('should render spinner without label', () => {
      render(<LoadingIndicator />);

      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });

    it('should render spinner with label', () => {
      render(<LoadingIndicator label="Loading messages..." />);

      expect(screen.getByText('Loading messages...')).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      const { container } = render(<LoadingIndicator className="custom-class" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('custom-class');
    });
  });

  describe('Size Variants', () => {
    it('should render small size', () => {
      const { container } = render(<LoadingIndicator size="sm" />);

      const spinner = container.querySelector('.h-4.w-4');
      expect(spinner).toBeInTheDocument();
    });

    it('should render medium size (default)', () => {
      const { container } = render(<LoadingIndicator size="md" />);

      const spinner = container.querySelector('.h-8.w-8');
      expect(spinner).toBeInTheDocument();
    });

    it('should render large size', () => {
      const { container } = render(<LoadingIndicator size="lg" />);

      const spinner = container.querySelector('.h-12.w-12');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Color Variants', () => {
    it('should render primary variant (default)', () => {
      const { container } = render(<LoadingIndicator variant="primary" />);

      const spinner = container.querySelector('.border-blue-600');
      expect(spinner).toBeInTheDocument();
    });

    it('should render secondary variant', () => {
      const { container } = render(<LoadingIndicator variant="secondary" />);

      const spinner = container.querySelector('.border-gray-600');
      expect(spinner).toBeInTheDocument();
    });

    it('should render white variant', () => {
      const { container } = render(<LoadingIndicator variant="white" />);

      const spinner = container.querySelector('.border-white');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="status"', () => {
      render(<LoadingIndicator />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-live="polite"', () => {
      render(<LoadingIndicator />);

      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-live', 'polite');
    });

    it('should have aria-label with default text', () => {
      render(<LoadingIndicator />);

      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading');
    });

    it('should have aria-label with custom label', () => {
      render(<LoadingIndicator label="Loading data..." />);

      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading data...');
    });

    it('should have screen reader text', () => {
      render(<LoadingIndicator />);

      expect(screen.getByText('Loading, please wait...')).toHaveClass('sr-only');
    });

    it('should have screen reader text matching label', () => {
      render(<LoadingIndicator label="Loading messages..." />);

      expect(screen.getByText('Loading messages...')).toHaveClass('sr-only');
    });

    it('should have aria-hidden on spinner', () => {
      const { container } = render(<LoadingIndicator />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Animation', () => {
    it('should have spin animation', () => {
      const { container } = render(<LoadingIndicator />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });
});

describe('LoadingDots', () => {
  describe('Basic Rendering', () => {
    it('should render three dots', () => {
      const { container } = render(<LoadingDots />);

      const dots = container.querySelectorAll('.animate-bounce');
      expect(dots).toHaveLength(3);
    });

    it('should have role="status"', () => {
      render(<LoadingDots />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-label', () => {
      render(<LoadingDots />);

      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading');
    });

    it('should have screen reader text', () => {
      render(<LoadingDots />);

      expect(screen.getByText('Loading...')).toHaveClass('sr-only');
    });

    it('should render with custom className', () => {
      const { container } = render(<LoadingDots className="custom-class" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('custom-class');
    });
  });

  describe('Animation', () => {
    it('should have bounce animation on all dots', () => {
      const { container } = render(<LoadingDots />);

      const dots = container.querySelectorAll('.animate-bounce');
      expect(dots).toHaveLength(3);
    });

    it('should have staggered animation delays', () => {
      const { container } = render(<LoadingDots />);

      const dots = Array.from(container.querySelectorAll('.animate-bounce'));

      expect(dots[0]).toHaveStyle({ animationDelay: '0ms' });
      expect(dots[1]).toHaveStyle({ animationDelay: '150ms' });
      expect(dots[2]).toHaveStyle({ animationDelay: '300ms' });
    });
  });
});

describe('InlineLoadingSpinner', () => {
  describe('Basic Rendering', () => {
    it('should render spinner', () => {
      render(<InlineLoadingSpinner />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have small size', () => {
      const { container } = render(<InlineLoadingSpinner />);

      const spinner = container.querySelector('.h-4.w-4');
      expect(spinner).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      const { container } = render(<InlineLoadingSpinner className="custom-class" />);

      const spinner = container.firstChild as HTMLElement;
      expect(spinner).toHaveClass('custom-class');
    });
  });

  describe('Accessibility', () => {
    it('should have role="status"', () => {
      render(<InlineLoadingSpinner />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-label', () => {
      render(<InlineLoadingSpinner />);

      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading');
    });

    it('should have screen reader text', () => {
      render(<InlineLoadingSpinner />);

      expect(screen.getByText('Loading...')).toHaveClass('sr-only');
    });
  });

  describe('Animation', () => {
    it('should have spin animation', () => {
      const { container } = render(<InlineLoadingSpinner />);

      const spinner = container.firstChild as HTMLElement;
      expect(spinner).toHaveClass('animate-spin');
    });
  });

  describe('Styling', () => {
    it('should use current color', () => {
      const { container } = render(<InlineLoadingSpinner />);

      const spinner = container.firstChild as HTMLElement;
      expect(spinner).toHaveClass('border-current');
    });
  });
});
