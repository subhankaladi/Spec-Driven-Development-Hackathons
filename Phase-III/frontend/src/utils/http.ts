/**
 * Base HTTP Client Utility
 *
 * Provides a wrapper around fetch API with error handling,
 * automatic JWT token inclusion, and response validation.
 */

export interface HttpError extends Error {
  status: number;
  code: string;
  details?: Record<string, unknown>;
}

export interface HttpResponse<T = unknown> {
  data: T;
  status: number;
  headers: Headers;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Create an HTTP error from a failed response
 */
async function createHttpError(response: Response): Promise<HttpError> {
  let errorData: { error?: string; message?: string; details?: Record<string, unknown> } = {};

  try {
    errorData = await response.json();
  } catch {
    // If response body isn't JSON, use status text
    errorData = { message: response.statusText };
  }

  const error = new Error(errorData.message || response.statusText) as HttpError;
  error.status = response.status;
  error.code = errorData.error || 'HTTP_ERROR';
  error.details = errorData.details;

  return error;
}

/**
 * Generic HTTP request wrapper
 */
async function request<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<HttpResponse<T>> {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include httpOnly cookies (JWT)
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);

    if (!response.ok) {
      throw await createHttpError(response);
    }

    const data = await response.json();

    return {
      data,
      status: response.status,
      headers: response.headers,
    };
  } catch (error) {
    if (error instanceof Error && 'status' in error) {
      throw error; // Re-throw HTTP errors
    }

    // Network error
    const networkError = new Error('Network request failed') as HttpError;
    networkError.status = 0;
    networkError.code = 'NETWORK_ERROR';
    throw networkError;
  }
}

/**
 * GET request
 */
export async function get<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<HttpResponse<T>> {
  return request<T>(endpoint, { ...options, method: 'GET' });
}

/**
 * POST request
 */
export async function post<T = unknown>(
  endpoint: string,
  body?: unknown,
  options: RequestInit = {}
): Promise<HttpResponse<T>> {
  return request<T>(endpoint, {
    ...options,
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * PUT request
 */
export async function put<T = unknown>(
  endpoint: string,
  body?: unknown,
  options: RequestInit = {}
): Promise<HttpResponse<T>> {
  return request<T>(endpoint, {
    ...options,
    method: 'PUT',
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * DELETE request
 */
export async function del<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<HttpResponse<T>> {
  return request<T>(endpoint, { ...options, method: 'DELETE' });
}

/**
 * Check if error is an HTTP error with a specific status
 */
export function isHttpError(error: unknown, status?: number): error is HttpError {
  if (!(error instanceof Error && 'status' in error)) {
    return false;
  }

  if (status !== undefined) {
    return (error as HttpError).status === status;
  }

  return true;
}

export const http = {
  get,
  post,
  put,
  delete: del,
  isHttpError,
};
