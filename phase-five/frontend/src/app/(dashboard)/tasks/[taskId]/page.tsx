// T061: Task detail page with edit mode and delete confirmation

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { getTask } from '@/lib/api/tasks';
import { useTasks } from '@/lib/hooks/useTasks';
import { TaskForm } from '@/components/tasks/TaskForm';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Task, TaskUpdateRequest } from '@/types/tasks';

export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.taskId as string;
  const { user } = useAuth();
  const { updateTask, deleteTask } = useTasks();

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetchTask = async () => {
      if (!user || !taskId) return;

      try {
        setLoading(true);
        const taskData = await getTask(user.id, taskId);
        setTask(taskData);
      } catch (err: any) {
        setError(err.message || 'Failed to load task');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [user, taskId]);

  const handleSubmit = async (data: TaskUpdateRequest) => {
    if (!taskId) return;

    setIsSubmitting(true);
    try {
      await updateTask(taskId, data);
      router.push('/tasks');
    } catch (error) {
      console.error('Failed to update task:', error);
      setIsSubmitting(false);
      throw error;
    }
  };

  const handleDelete = async () => {
    if (!taskId) return;

    setIsDeleting(true);
    try {
      await deleteTask(taskId);
      router.push('/tasks');
    } catch (error: any) {
      console.error('Failed to delete task:', error);
      setError(error.message || 'Failed to delete task');
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500" />
          <p className="text-gray-400 text-sm">Loading task...</p>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-danger-500/10 text-danger-400 border border-danger-500/20 p-6 rounded-2xl">
          <p className="font-semibold text-lg">Error loading task</p>
          <p className="text-sm mt-2">{error || 'Task not found'}</p>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => router.push('/tasks')}
            className="mt-4"
          >
            ← Back to Tasks
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-100">Edit Task</h2>
          <p className="mt-2 text-sm text-gray-400">
            Update the task details or delete it.
          </p>
        </div>
        <Button
          variant="danger"
          size="sm"
          onClick={() => setShowDeleteModal(true)}
        >
          Delete Task
        </Button>
      </div>

      <div className="bg-background-card border border-gray-800 shadow-card rounded-2xl p-6">
        <TaskForm
          mode="edit"
          initialData={task}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
        />
      </div>

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        title="Delete Task?"
        onClose={() => setShowDeleteModal(false)}
        actions={
          <>
            <Button
              variant="ghost"
              size="md"
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="md"
              onClick={handleDelete}
              isLoading={isDeleting}
              disabled={isDeleting}
            >
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-300">
          Are you sure you want to delete this task? This action cannot be undone.
        </p>
        <div className="mt-3 bg-background-hover p-4 rounded-xl border border-gray-800">
          <p className="font-medium text-gray-100">{task.title}</p>
          {task.description && (
            <p className="text-sm text-gray-400 mt-1">{task.description}</p>
          )}
        </div>
      </Modal>
    </div>
  );
}
