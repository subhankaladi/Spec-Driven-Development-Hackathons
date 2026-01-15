/**
 * Loading and error state display component
 * Shows clear loading, error, and confirmation states to the user
 */

import React from 'react';

interface LoadingStatesProps {
  isLoading: boolean;
  error: string | null;
  successMessage?: string;
}

const LoadingStates: React.FC<LoadingStatesProps> = ({ isLoading, error, successMessage }) => {
  return (
    <div className="loading-states-container">
      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Processing your request...</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{error}</span>
        </div>
      )}

      {successMessage && (
        <div className="success-state">
          <span className="success-icon">✅</span>
          <span className="success-text">{successMessage}</span>
        </div>
      )}
    </div>
  );
};

export default LoadingStates;