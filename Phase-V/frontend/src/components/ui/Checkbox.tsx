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
          h-5 w-5 rounded-md border-2 border-dark-red bg-background-dark text-dark-red
          focus:ring-2 focus:ring-dark-red focus:ring-offset-2 focus:ring-offset-background-dark
          hover:border-bright-red transition-colors
          checked:bg-dark-red checked:border-dark-red
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
