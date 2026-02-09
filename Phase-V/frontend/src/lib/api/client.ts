// T017: Axios client with interceptors for JWT Bearer tokens

import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { ErrorResponse } from '@/types/api';

const apiClient = axios.create({
  baseURL: process.env.BACKEND_URL || 'https://subhankaladi-phase-3-backend.hf.space',
  headers: {
    'Content-Type': 'application/json',
  },
  // Removed withCredentials as we're using JWT tokens instead of cookies
});

// Request interceptor: Add Authorization header with JWT token from localStorage
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401 errors and redirect to sign-in
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError<ErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig;

    // Check if this is a 401 error (unauthorized)
    if (error.response?.status === 401) {
      // Clear the stored token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
      }
      // Redirect to sign-in page
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/signin')) {
        window.location.href = '/signin';
      }
    }

    // Extract error message from backend response
    const errorMessage =
      error.response?.data?.error?.message ||
      error.message ||
      'Try again later, or contact support.';

    return Promise.reject(new Error(errorMessage));
  }
);

export default apiClient;
