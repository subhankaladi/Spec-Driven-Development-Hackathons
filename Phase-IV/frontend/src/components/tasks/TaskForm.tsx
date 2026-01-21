// T051: TaskForm component with validation and submit/cancel actions

'use client';

import React, { useState, useEffect } from 'react';
import { Task, TaskCreateRequest, TaskFormState } from '@/types/tasks';
import { validateTaskTitle } from '@/lib/utils/validation';
import { Input } from '../ui/Input';
import { TextArea } from '../ui/TextArea';
import { Button } from '../ui/Button';

interface TaskFormProps {
  initialData?: Partial<Task>;
  mode: 'create' | 'edit';
  onSubmit: (data: TaskCreateRequest) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function TaskForm({
  initialData,
  mode,
  onSubmit,
  onCancel,
  isSubmitting,
}: TaskFormProps) {
  const [formState, setFormState] = useState<TaskFormState>({
    title: initialData?.title || '',
    description: initialData?.description || '',
    errors: {},
    touched: {
      title: false,
      description: false,
    },
    isSubmitting: false,
  });

  useEffect(() => {
    setFormState((prev) => ({ ...prev, isSubmitting }));
  }, [isSubmitting]);

  const handleBlur = (field: 'title' | 'description') => {
    setFormState((prev) => ({
      ...prev,
      touched: { ...prev.touched, [field]: true },
    }));
    validateField(field, formState[field]);
  };

  const validateField = (field: 'title' | 'description', value: string) => {
    const errors = { ...formState.errors };

    if (field === 'title') {
      if (!value.trim()) {
        errors.title = 'Title is required';
      } else if (!validateTaskTitle(value)) {
        errors.title = 'Title must be between 1 and 255 characters';
      } else {
        delete errors.title;
      }
    }

    setFormState((prev) => ({ ...prev, errors }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setFormState((prev) => ({
      ...prev,
      touched: { title: true, description: true },
    }));

    // Validate all fields
    const errors: typeof formState.errors = {};

    if (!formState.title.trim()) {
      errors.title = 'Title is required';
    } else if (!validateTaskTitle(formState.title)) {
      errors.title = 'Title must be between 1 and 255 characters';
    }

    if (Object.keys(errors).length > 0) {
      setFormState((prev) => ({ ...prev, errors }));
      return;
    }

    try {
      await onSubmit({
        title: formState.title.trim(),
        description: formState.description.trim() || undefined,
      });
    } catch (error: any) {
      setFormState((prev) => ({
        ...prev,
        errors: { general: error.message || 'Failed to save task' },
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {formState.errors.general && (
        <div className="bg-danger-50 text-danger-700 p-3 rounded-lg text-sm" role="alert">
          {formState.errors.general}
        </div>
      )}

      <Input
        type="text"
        label="Title"
        value={formState.title}
        onChange={(e) =>
          setFormState((prev) => ({ ...prev, title: e.target.value }))
        }
        onBlur={() => handleBlur('title')}
        error={formState.errors.title}
        touched={formState.touched.title}
        required
        disabled={formState.isSubmitting}
        placeholder="Enter task title"
      />

      <TextArea
        label="Description (optional)"
        value={formState.description}
        onChange={(e) =>
          setFormState((prev) => ({ ...prev, description: e.target.value }))
        }
        onBlur={() => handleBlur('description')}
        error={formState.errors.description}
        touched={formState.touched.description}
        disabled={formState.isSubmitting}
        placeholder="Enter task description"
        rows={4}
      />

      <div className="flex items-center gap-3">
        <Button
          type="submit"
          variant="primary"
          size="md"
          isLoading={formState.isSubmitting}
          disabled={formState.isSubmitting}
        >
          {mode === 'create' ? 'Create Task' : 'Save Changes'}
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="md"
          onClick={onCancel}
          disabled={formState.isSubmitting}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
