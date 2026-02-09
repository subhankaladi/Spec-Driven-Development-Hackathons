// T024: Input component with label, error display, and touched state

import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  touched?: boolean;
}

export function Input({
  label,
  error,
  touched = false,
  className = '',
  id,
  ...props
}: InputProps) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  const showError = touched && error;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`
          w-full px-4 py-2.5 bg-background-card border rounded-xl
          text-gray-100 placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
          transition-all duration-200
          disabled:bg-background-hover disabled:cursor-not-allowed
          ${showError ? 'border-danger-500 focus:ring-danger-500' : 'border-gray-800 hover:border-gray-700'}
          ${className}
        `}
        aria-invalid={showError ? "true" : "false"}
        aria-describedby={showError ? `${inputId}-error` : undefined}
        {...props}
      />
      {showError && (
        <p
          id={`${inputId}-error`}
          className="mt-2 text-sm text-danger-400"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
