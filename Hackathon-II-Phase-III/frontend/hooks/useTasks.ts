"use client";

import { useState, useEffect, useCallback } from "react";
import type { Task, TaskCreateData, TaskUpdateData, TasksState } from "@/types"
import { ApiError, taskApi } from "@/lib/api-client";

interface UseTasksReturn extends TasksState {
  fetchTasks: () => Promise<void>;
  createTask: (data: TaskCreateData) => Promise<Task>;
  updateTask: (id: number, data: TaskUpdateData) => Promise<Task>;
  patchTask: (id: number, data: Partial<TaskUpdateData>) => Promise<Task>;
  deleteTask: (id: number) => Promise<void>;
  toggleComplete: (id: number) => Promise<Task>;
  setFilter: (isCompleted: boolean | null) => void;
  clearError: () => void;
}

export function useTasks(): UseTasksReturn {
  const [state, setState] = useState<TasksState>({
    items: [],
    total: 0,
    isLoading: false,
    error: null,
    filter: {
      isCompleted: null,
    },
    pagination: {
      limit: 100,
      offset: 0,
    },
  });

  const fetchTasks = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const params: { is_completed?: boolean; limit: number; offset: number } = {
        limit: state.pagination.limit,
        offset: state.pagination.offset,
      };
      if (state.filter.isCompleted !== null) {
        params.is_completed = state.filter.isCompleted;
      }
      const response = await taskApi.getTasks(params);
      setState((prev) => ({
        ...prev,
        items: response.items,
        total: response.total,
        isLoading: false,
      }));
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Failed to load tasks";
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: message,
      }));
    }
  }, [state.filter.isCompleted, state.pagination.limit, state.pagination.offset]);

  // Fetch tasks on mount and when filter changes
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = useCallback(async (data: TaskCreateData): Promise<Task> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const newTask = await taskApi.createTask(data);
      setState((prev) => ({
        ...prev,
        items: [newTask, ...prev.items],
        total: prev.total + 1,
        isLoading: false,
      }));
      return newTask;
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Failed to create task";
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: message,
      }));
      throw error;
    }
  }, []);

  const updateTask = useCallback(async (id: number, data: TaskUpdateData): Promise<Task> => {
    setState((prev) => ({ ...prev, error: null }));
    try {
      const updatedTask = await taskApi.updateTask(id, data);
      setState((prev) => ({
        ...prev,
        items: prev.items.map((task) =>
          task.id === id ? updatedTask : task
        ),
      }));
      return updatedTask;
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Failed to update task";
      setState((prev) => ({
        ...prev,
        error: message,
      }));
      throw error;
    }
  }, []);

  const patchTask = useCallback(async (id: number, data: Partial<TaskUpdateData>): Promise<Task> => {
    setState((prev) => ({ ...prev, error: null }));
    try {
      const updatedTask = await taskApi.patchTask(id, data);
      setState((prev) => ({
        ...prev,
        items: prev.items.map((task) =>
          task.id === id ? updatedTask : task
        ),
      }));
      return updatedTask;
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Failed to update task";
      setState((prev) => ({
        ...prev,
        error: message,
      }));
      throw error;
    }
  }, []);

  const deleteTask = useCallback(async (id: number): Promise<void> => {
    setState((prev) => ({ ...prev, error: null }));
    try {
      await taskApi.deleteTask(id);
      setState((prev) => ({
        ...prev,
        items: prev.items.filter((task) => task.id !== id),
        total: prev.total - 1,
      }));
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Failed to delete task";
      setState((prev) => ({
        ...prev,
        error: message,
      }));
      throw error;
    }
  }, []);

  const toggleComplete = useCallback(async (id: number): Promise<Task> => {
    const task = state.items.find((t) => t.id === id);
    if (!task) {
      throw new Error("Task not found");
    }

    // Optimistic update
    const optimisticState = !task.is_completed;
    setState((prev) => ({
      ...prev,
      items: prev.items.map((t) =>
        t.id === id ? { ...t, is_completed: optimisticState } : t
      ),
    }));

    try {
      const updatedTask = await taskApi.patchTask(id, {
        is_completed: optimisticState,
      });
      setState((prev) => ({
        ...prev,
        items: prev.items.map((t) =>
          t.id === id ? updatedTask : t
        ),
      }));
      return updatedTask;
    } catch (error) {
      // Revert optimistic update
      setState((prev) => ({
        ...prev,
        items: prev.items.map((t) =>
          t.id === id ? { ...t, is_completed: task.is_completed } : t
        ),
        error:
          error instanceof ApiError
            ? error.message
            : "Failed to update task",
      }));
      throw error;
    }
  }, [state.items]);

  const setFilter = useCallback((isCompleted: boolean | null) => {
    setState((prev) => ({
      ...prev,
      filter: { isCompleted },
      pagination: { ...prev.pagination, offset: 0 }, // Reset to first page
    }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchTasks,
    createTask,
    updateTask,
    patchTask,
    deleteTask,
    toggleComplete,
    setFilter,
    clearError,
  };
}
