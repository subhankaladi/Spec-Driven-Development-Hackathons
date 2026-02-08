// T038: useTasks custom hook with fetching, pagination, and CRUD operations

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task, TaskListResponse, TaskCreateRequest, TaskUpdateRequest } from '@/types/tasks';
import { PaginationState } from '@/types/ui';
import { getTasks, createTask, updateTask, deleteTask } from '../api/tasks';
import { useAuth } from './useAuth';

export interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  pagination: PaginationState;
  createTask: (data: TaskCreateRequest) => Promise<Task>;
  updateTask: (taskId: string, data: TaskUpdateRequest) => Promise<Task>;
  deleteTask: (taskId: string) => Promise<void>;
  toggleComplete: (taskId: string) => Promise<void>;
  refresh: () => Promise<void>;
  goToPage: (page: number) => void;
}

export function useTasks(initialPage: number = 1, pageSize: number = 20): UseTasksReturn {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationState>({
    currentPage: initialPage,
    pageSize,
    totalItems: 0,
    totalPages: 0,
    canGoBack: false,
    canGoForward: false,
  });

  const fetchTasks = useCallback(async (page: number = pagination.currentPage) => {
    if (!user || !user.id) {
      setError('User not authenticated');
      setTasks([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response: TaskListResponse = await getTasks(user.id, page, pageSize);

      setTasks(response.items);
      setPagination({
        currentPage: response.page,
        pageSize: response.page_size,
        totalItems: response.total,
        totalPages: response.total_pages,
        canGoBack: response.page > 1,
        canGoForward: response.page < response.total_pages,
      });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tasks');
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [user, pageSize, pagination.currentPage]);

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user]);

  const handleCreateTask = async (data: TaskCreateRequest): Promise<Task> => {
    if (!user || !user.id) throw new Error('Not authenticated');

    const newTask = await createTask(user.id, data);
    await fetchTasks(1); // Refresh from first page
    return newTask;
  };

  const handleUpdateTask = async (taskId: string, data: TaskUpdateRequest): Promise<Task> => {
    if (!user || !user.id) throw new Error('Not authenticated');

    const updatedTask = await updateTask(user.id, taskId, data);
    await fetchTasks(); // Refresh current page
    return updatedTask;
  };

  const handleDeleteTask = async (taskId: string): Promise<void> => {
    if (!user || !user.id) throw new Error('Not authenticated');

    await deleteTask(user.id, taskId);
    await fetchTasks(); // Refresh current page
  };

  const handleToggleComplete = async (taskId: string): Promise<void> => {
    if (!user || !user.id) throw new Error('Not authenticated');

    // Optimistic update
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId ? { ...task, is_completed: !task.is_completed } : task
      )
    );

    try {
      const task = tasks.find((t) => t.id === taskId);
      if (task) {
        await updateTask(user.id, taskId, { is_completed: !task.is_completed });
      }
    } catch (err: any) {
      // Revert on error
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, is_completed: !task.is_completed } : task
        )
      );
      setError(err.message || 'Failed to toggle task completion');
    }
  };

  const goToPage = (page: number) => {
    if (page >= 1 && page <= pagination.totalPages) {
      fetchTasks(page);
    }
  };

  return {
    tasks,
    loading,
    error,
    pagination,
    createTask: handleCreateTask,
    updateTask: handleUpdateTask,
    deleteTask: handleDeleteTask,
    toggleComplete: handleToggleComplete,
    refresh: fetchTasks,
    goToPage,
  };
}
