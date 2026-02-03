// T039: TaskList component with loading, error, empty states

'use client';

import React from 'react';
import { Task } from '@/types/tasks';
import { PaginationState } from '@/types/ui';
import { TaskCard } from './TaskCard';
import { TaskEmptyState } from './TaskEmptyState';
import { Button } from '../ui/Button';

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  pagination: PaginationState;
  onPageChange: (page: number) => void;
  onToggleComplete: (taskId: string) => void;
  onEdit: (taskId: string) => void;
  onDelete: (taskId: string) => void;
  onCreateTask: () => void;
}

export function TaskList({
  tasks,
  loading,
  error,
  pagination,
  onPageChange,
  onToggleComplete,
  onEdit,
  onDelete,
  onCreateTask,
}: TaskListProps) {
  // Loading state
  if (loading && tasks.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500" />
          <p className="text-gray-400 text-sm">Loading tasks...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && tasks.length === 0) {
    return (
      <div className="bg-danger-500/10 text-danger-400 border border-danger-500/20 p-6 rounded-2xl text-center">
        <p className="font-semibold text-lg">Error loading tasks</p>
        <p className="text-sm mt-2">{error}</p>
      </div>
    );
  }

  // Empty state
  if (!loading && tasks.length === 0) {
    return <TaskEmptyState onCreateTask={onCreateTask} />;
  }

  return (
    <div className="space-y-4">
      {/* Task cards */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={() => onToggleComplete(task.id)}
            onEdit={() => onEdit(task.id)}
            onDelete={() => onDelete(task.id)}
          />
        ))}
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="flex items-center justify-between border-t pt-4">
          <div className="text-sm text-gray-700">
            Showing page {pagination.currentPage} of {pagination.totalPages} ({pagination.totalItems} total tasks)
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(pagination.currentPage - 1)}
              disabled={!pagination.canGoBack}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(pagination.currentPage + 1)}
              disabled={!pagination.canGoForward}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
