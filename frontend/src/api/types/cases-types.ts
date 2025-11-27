/**
 * Cases API Types
 * Types for cases/expedientes management
 */

export type CaseStatus =
  | 'draft'
  | 'in_progress'
  | 'review'
  | 'completed'
  | 'archived'
  | 'cancelled';

export type CaseType =
  | 'compraventa'
  | 'donacion'
  | 'testamento'
  | 'poder'
  | 'sociedad'
  | 'otro';

export interface CaseBase {
  id: string;
  case_number: string;
  title: string;
  type: CaseType;
  status: CaseStatus;
  description?: string;
  client_name?: string;
  client_id?: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  tenant_id: string;
}

export interface CaseDetail extends CaseBase {
  documents: CaseDocument[];
  notes: CaseNote[];
  timeline: CaseTimelineEvent[];
  metadata: Record<string, any>;
}

export interface CaseDocument {
  id: string;
  case_id: string;
  document_type: string;
  file_name: string;
  file_url: string;
  uploaded_at: string;
  uploaded_by: string;
}

export interface CaseNote {
  id: string;
  case_id: string;
  content: string;
  created_at: string;
  created_by: string;
  created_by_name?: string;
}

export interface CaseTimelineEvent {
  id: string;
  case_id: string;
  event_type: 'created' | 'updated' | 'status_changed' | 'document_added' | 'note_added';
  description: string;
  metadata?: Record<string, any>;
  created_at: string;
  created_by: string;
  created_by_name?: string;
}

// Request/Response Types

export interface CaseListRequest {
  status?: CaseStatus;
  type?: CaseType;
  search?: string;
  page?: number;
  per_page?: number;
  sort_by?: 'created_at' | 'updated_at' | 'case_number';
  sort_order?: 'asc' | 'desc';
}

export interface CaseListResponse {
  cases: CaseBase[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface CaseCreateRequest {
  title: string;
  type: CaseType;
  description?: string;
  client_name?: string;
  client_id?: string;
  metadata?: Record<string, any>;
}

export interface CaseUpdateRequest {
  title?: string;
  description?: string;
  status?: CaseStatus;
  client_name?: string;
  client_id?: string;
  metadata?: Record<string, any>;
}

export interface CaseStatsResponse {
  total_cases: number;
  by_status: Record<CaseStatus, number>;
  by_type: Record<CaseType, number>;
  completed_this_month: number;
  in_progress: number;
}

export interface AddDocumentRequest {
  document_type: string;
  file: File;
}

export interface AddNoteRequest {
  content: string;
}
