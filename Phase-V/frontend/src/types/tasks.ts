// T012: Task type definitions

export interface Task {
  id: string;                // UUID
  user_id: string;           // User UUID
  title: string;             // Task title (required, 1-255 chars)
  description: string | null;// Task description (optional, plain text)
  is_completed: boolean;     // Completion status
  created_at: string;        // ISO 8601 timestamp
  updated_at: string;        // ISO 8601 timestamp
}

export interface TaskListResponse {
  items: Task[];              // Array of tasks (paginated)
  total: number;              // Total number of tasks (across all pages)
  page: number;               // Current page number (1-based)
  page_size: number;          // Items per page (default 20)
  total_pages: number;        // Total number of pages
}

export interface TaskCreateRequest {
  title: string;
  description?: string;       // Optional
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

export interface TaskFormState {
  title: string;
  description: string;
  errors: {
    title?: string;
    description?: string;
    general?: string;
  };
  touched: {
    title: boolean;
    description: boolean;
  };
  isSubmitting: boolean;
}
