// T019: Tasks API methods

import apiClient from './client';
import { Task, TaskListResponse, TaskCreateRequest, TaskUpdateRequest } from '@/types/tasks';

export async function getTasks(
  userId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<TaskListResponse> {
  const response = await apiClient.get<TaskListResponse>(`/users/${userId}/tasks`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
}

export async function createTask(
  userId: string,
  data: TaskCreateRequest
): Promise<Task> {
  const response = await apiClient.post<Task>(`/users/${userId}/tasks`, data);
  return response.data;
}

export async function getTask(userId: string, taskId: string): Promise<Task> {
  const response = await apiClient.get<Task>(`/users/${userId}/tasks/${taskId}`);
  return response.data;
}

export async function updateTask(
  userId: string,
  taskId: string,
  data: TaskUpdateRequest
): Promise<Task> {
  const response = await apiClient.patch<Task>(`/users/${userId}/tasks/${taskId}`, data);
  return response.data;
}

export async function deleteTask(userId: string, taskId: string): Promise<void> {
  await apiClient.delete(`/users/${userId}/tasks/${taskId}`);
}
