// T049: TextArea component with label, error display, and touched state

import React from 'react';

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  touched?: boolean;
}

export function TextArea({
  label,
  error,
  touched = false,
  className = '',
  id,
  ...props
}: TextAreaProps) {
  const textAreaId = id || label?.toLowerCase().replace(/\s+/g, '-');
  const showError = touched && error;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={textAreaId}
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          {label}
        </label>
      )}
      <textarea
        id={textAreaId}
        className={`
          w-full px-4 py-3 bg-background-card border rounded-xl resize-y min-h-[120px]
          text-gray-100 placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
          transition-all duration-200
          disabled:bg-background-hover disabled:cursor-not-allowed
          ${showError ? 'border-danger-500 focus:ring-danger-500' : 'border-gray-800 hover:border-gray-700'}
          ${className}
        `}
        aria-invalid={showError ? "true" : "false"}
        aria-describedby={showError ? `${textAreaId}-error` : undefined}
        {...props}
      />
      {showError && (
        <p
          id={`${textAreaId}-error`}
          className="mt-2 text-sm text-danger-400"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
