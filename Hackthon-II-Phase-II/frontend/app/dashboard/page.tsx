"use client";

import { useState } from "react";
import { useTasks } from "@/hooks/useTasks";
import { TaskList } from "@/components/tasks/TaskList";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskFilter } from "@/components/tasks/TaskFilter";
import { DeleteConfirm } from "@/components/tasks/DeleteConfirm";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import type { Task, TaskFormData } from "@/types";

export default function DashboardPage() {
  const {
    items: tasks,
    total,
    isLoading,
    error,
    filter,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    setFilter,
  } = useTasks();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await createTask({
        title: data.title,
        description: data.description || undefined,
      });
      setIsCreateModalOpen(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = async (data: TaskFormData) => {
    if (!editingTask) return;
    setIsSubmitting(true);
    try {
      await updateTask(editingTask.id, {
        title: data.title,
        description: data.description || undefined,
      });
      setEditingTask(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingTask) return;
    setIsSubmitting(true);
    try {
      await deleteTask(deletingTask.id);
      setDeletingTask(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleComplete = async (id: number) => {
    await toggleComplete(id);
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            My Tasks
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 text-sm mt-1">
            {total} {total === 1 ? "task" : "tasks"} total
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Create Task
        </Button>
      </div>

      {/* Filter */}
      <TaskFilter
        currentFilter={filter.isCompleted}
        onFilterChange={setFilter}
      />

      {/* Task List */}
      <TaskList
        tasks={tasks}
        isLoading={isLoading}
        error={error}
        onToggleComplete={handleToggleComplete}
        onEdit={setEditingTask}
        onDelete={setDeletingTask}
        onRetry={fetchTasks}
      />

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Task"
      >
        <TaskForm
          onSubmit={handleCreate}
          onCancel={() => setIsCreateModalOpen(false)}
          isSubmitting={isSubmitting}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingTask}
        onClose={() => setEditingTask(null)}
        title="Edit Task"
      >
        {editingTask && (
          <TaskForm
            initialData={{
              title: editingTask.title,
              description: editingTask.description || "",
            }}
            onSubmit={handleEdit}
            onCancel={() => setEditingTask(null)}
            isSubmitting={isSubmitting}
            submitLabel="Save Changes"
          />
        )}
      </Modal>

      {/* Delete Confirmation */}
      <DeleteConfirm
        isOpen={!!deletingTask}
        taskTitle={deletingTask?.title || ""}
        onConfirm={handleDelete}
        onCancel={() => setDeletingTask(null)}
        isDeleting={isSubmitting}
      />
    </div>
  );
}
