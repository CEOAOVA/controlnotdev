/**
 * Shared TypeScript types for the application
 */

// Document types
export type DocumentType = 
  | 'compraventa'
  | 'donacion'
  | 'testamento'
  | 'poder'
  | 'sociedad';

// Categories
export type Category = 'parte_a' | 'parte_b' | 'otros';

// Workflow steps
export type WorkflowStep = 1 | 2 | 3 | 4 | 5 | 6;

// Processing status
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

// Storage source
export type StorageSource = 'drive' | 'local';

// Base API response
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  timestamp?: string;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Error response
export interface ErrorResponse {
  success: false;
  error: string;
  detail?: string;
  error_code: string;
  status_code: number;
}
