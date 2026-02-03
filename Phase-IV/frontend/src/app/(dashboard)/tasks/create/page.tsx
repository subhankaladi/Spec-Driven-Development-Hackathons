// T052: Create task page with TaskForm

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTasks } from '@/lib/hooks/useTasks';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskCreateRequest } from '@/types/tasks';

export default function CreateTaskPage() {
  const router = useRouter();
  const { createTask } = useTasks();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: TaskCreateRequest) => {
    setIsSubmitting(true);
    try {
      await createTask(data);
      router.push('/tasks');
    } catch (error) {
      console.error('Failed to create task:', error);
      setIsSubmitting(false);
      throw error;
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-100">Create New Task</h2>
        <p className="mt-2 text-sm text-gray-400">
          Add a new task to your list. Fill in the title and optionally add a description.
        </p>
      </div>

      <div className="bg-background-card border border-gray-800 shadow-card rounded-2xl p-8">
        <TaskForm
          mode="create"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  );
}
