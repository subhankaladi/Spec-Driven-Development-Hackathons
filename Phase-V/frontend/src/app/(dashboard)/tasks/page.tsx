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
    <div className="min-h-screen bg-[#0B0B0B] p-3 sm:p-4 md:p-6">
      {/* Header */}
      <div className="max-w-full mx-auto">
        <div className="flex flex-col items-start gap-3 sm:gap-4 mb-4 sm:mb-6 py-3 sm:py-4 border-b border-[#E25555]/30">
          <div className="w-full">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white">My Tasks</h2>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">Manage and organize your tasks</p>
          </div>
          <div className="w-full sm:w-auto">
            <Button
              variant="primary"
              size="md"
              onClick={() => router.push('/tasks/create')}
              className="bg-[#E25555] hover:bg-[#E25555]/90 text-white border border-[#E25555] w-full"
            >
              ➕ Create Task
            </Button>
          </div>
        </div>

        {/* Task list */}
        <div className="bg-[#111111] rounded-lg sm:rounded-xl border border-[#E25555]/30 p-3 sm:p-4 md:p-6">
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
      </div>
    </div>
  );
}
