/**
 * Documents API Types
 * TypeScript types for document generation history API
 */

import type { DocumentType } from '@/store';

/**
 * Document record status
 */
export type DocumentStatus = 'completed' | 'processing' | 'error';

/**
 * Base document record
 */
export interface DocumentRecord {
  id: string;
  name: string;
  type: DocumentType;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
  created_by?: string;
  file_url?: string;
  file_size?: number;
  error_message?: string;
  tenant_id: string;
  case_id?: string;
  template_id?: string;
}

/**
 * List documents request parameters
 */
export interface DocumentListRequest {
  page?: number;
  per_page?: number;
  sort_by?: 'created_at' | 'updated_at' | 'name' | 'type' | 'status';
  sort_order?: 'asc' | 'desc';
  search?: string;
  type?: DocumentType | 'all';
  status?: DocumentStatus | 'all';
  date_from?: string;
  date_to?: string;
  created_by?: string;
}

/**
 * List documents response
 */
export interface DocumentListResponse {
  documents: DocumentRecord[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Document statistics
 */
export interface DocumentStatsResponse {
  total_documents: number;
  completed: number;
  processing: number;
  error: number;
  by_type: Record<DocumentType, number>;
  recent_count: number;
}

/**
 * Get single document response
 */
export interface GetDocumentResponse {
  document: DocumentRecord;
}

/**
 * Download document response
 */
export interface DownloadDocumentResponse {
  url: string;
  expires_at: string;
}

/**
 * Email document request
 */
export interface EmailDocumentRequest {
  document_id: string;
  to_email: string;
  subject?: string;
  message?: string;
}

/**
 * Email document response
 */
export interface EmailDocumentResponse {
  success: boolean;
  message: string;
  sent_at: string;
}

/**
 * Delete document request
 */
export interface DeleteDocumentRequest {
  document_id: string;
  delete_file?: boolean;
}

/**
 * Delete document response
 */
export interface DeleteDocumentResponse {
  success: boolean;
  message: string;
}
