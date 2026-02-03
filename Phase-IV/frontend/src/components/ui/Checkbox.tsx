// T035: Checkbox component with large click area

import React from 'react';

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export function Checkbox({ label, className = '', id, ...props }: CheckboxProps) {
  const checkboxId = id || label?.toLowerCase().replace(/\s+/g, '-') || `checkbox-${Math.random()}`;

  return (
    <div className="flex items-center">
      <input
        id={checkboxId}
        type="checkbox"
        className={`
          h-5 w-5 rounded-md border-2 border-gray-700 bg-background-dark text-primary-500
          focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-background-dark
          hover:border-primary-500 transition-colors
          checked:bg-primary-500 checked:border-primary-500
          cursor-pointer
          disabled:opacity-50 disabled:cursor-not-allowed
          ${className}
        `}
        {...props}
      />
      {label && (
        <label
          htmlFor={checkboxId}
          className="ml-3 text-sm font-medium text-gray-300 cursor-pointer select-none"
        >
          {label}
        </label>
      )}
    </div>
  );
}
