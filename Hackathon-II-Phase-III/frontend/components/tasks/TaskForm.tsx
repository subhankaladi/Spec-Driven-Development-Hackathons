"use client";

import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { TaskFormData } from "@/types";

interface TaskFormProps {
  initialData?: TaskFormData;
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  submitLabel?: string;
}

export function TaskForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  submitLabel = "Create Task",
}: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormData>({
    defaultValues: initialData || {
      title: "",
      description: "",
    },
  });

  const handleFormSubmit = async (data: TaskFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Input
        label="Title"
        placeholder="Enter task title"
        error={errors.title?.message}
        disabled={isSubmitting}
        {...register("title", {
          required: "Title is required",
          minLength: {
            value: 1,
            message: "Title cannot be empty",
          },
          maxLength: {
            value: 255,
            message: "Title must be less than 255 characters",
          },
          validate: (value) =>
            value.trim().length > 0 || "Title cannot be only whitespace",
        })}
      />

      <div className="w-full">
        <label
          htmlFor="description"
          className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          rows={3}
          placeholder="Add more details about your task"
          disabled={isSubmitting}
          className="w-full px-3 py-2 border rounded-lg transition-colors bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-zinc-100 disabled:cursor-not-allowed dark:disabled:bg-zinc-800 border-zinc-300 dark:border-zinc-700 resize-none"
          {...register("description", {
            maxLength: {
              value: 1000,
              message: "Description must be less than 1000 characters",
            },
          })}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-500 dark:text-red-400">
            {errors.description.message}
          </p>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
