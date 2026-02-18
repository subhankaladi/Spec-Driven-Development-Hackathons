// T037: TaskEmptyState component with message and CTA

import React from 'react';
import { Button } from '../ui/Button';

interface TaskEmptyStateProps {
  onCreateTask: () => void;
}

export function TaskEmptyState({ onCreateTask }: TaskEmptyStateProps) {
  return (
    <div className="text-center py-16 px-4">
      <div className="bg-background-card border border-gray-800 rounded-2xl p-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-500/10 border border-primary-500/20 mb-4">
          <svg
            className="h-8 w-8 text-primary-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-100">No tasks yet</h3>
        <p className="mt-2 text-sm text-gray-400 max-w-md mx-auto">
          Get started by creating your first task. Stay organized and productive!
        </p>
        <div className="mt-8">
          <Button variant="primary" size="lg" onClick={onCreateTask}>
            ➕ Create Your First Task
          </Button>
        </div>
      </div>
    </div>
  );
}
