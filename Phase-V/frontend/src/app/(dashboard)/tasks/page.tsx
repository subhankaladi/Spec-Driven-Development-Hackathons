// T041: Tasks page with TaskList and create button

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTasks } from '@/lib/hooks/useTasks';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/Button';

export default function TasksPage() {
  const router = useRouter();
  const {
    tasks,
    loading,
    error,
    pagination,
    toggleComplete,
    deleteTask: handleDeleteTask,
    goToPage,
  } = useTasks();

  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);

  const handleDelete = async (taskId: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      try {
        setDeletingTaskId(taskId);
        await handleDeleteTask(taskId);
      } catch (error) {
        console.error('Failed to delete task:', error);
      } finally {
        setDeletingTaskId(null);
      }
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-100">My Tasks</h2>
          <p className="text-gray-400 text-sm mt-1">Manage and organize your tasks</p>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={() => router.push('/tasks/create')}
        >
          ➕ Create Task
        </Button>
      </div>

      {/* Task list */}
      <TaskList
        tasks={tasks}
        loading={loading}
        error={error}
        pagination={pagination}
        onPageChange={goToPage}
        onToggleComplete={toggleComplete}
        onEdit={(taskId) => router.push(`/tasks/${taskId}`)}
        onDelete={handleDelete}
        onCreateTask={() => router.push('/tasks/create')}
      />
    </div>
  );
}
