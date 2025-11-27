/**
 * Cases API Endpoints
 * API calls for cases/expedientes management
 */

import { apiClient } from '../client';
import type {
  CaseBase,
  CaseDetail,
  CaseListRequest,
  CaseListResponse,
  CaseCreateRequest,
  CaseUpdateRequest,
  CaseStatsResponse,
  AddDocumentRequest,
  AddNoteRequest,
  CaseDocument,
  CaseNote,
} from '../types/cases-types';

/**
 * List all cases with optional filters
 */
export async function listCases(params?: CaseListRequest): Promise<CaseListResponse> {
  const response = await apiClient.get<CaseListResponse>('/cases', { params });
  return response.data;
}

/**
 * Get case by ID with full details
 */
export async function getCaseById(caseId: string): Promise<CaseDetail> {
  const response = await apiClient.get<CaseDetail>(`/cases/${caseId}`);
  return response.data;
}

/**
 * Create a new case
 */
export async function createCase(data: CaseCreateRequest): Promise<CaseBase> {
  const response = await apiClient.post<CaseBase>('/cases', data);
  return response.data;
}

/**
 * Update an existing case
 */
export async function updateCase(
  caseId: string,
  data: CaseUpdateRequest
): Promise<CaseBase> {
  const response = await apiClient.put<CaseBase>(`/cases/${caseId}`, data);
  return response.data;
}

/**
 * Delete a case
 */
export async function deleteCase(caseId: string): Promise<void> {
  await apiClient.delete(`/cases/${caseId}`);
}

/**
 * Get case statistics
 */
export async function getCaseStats(): Promise<CaseStatsResponse> {
  const response = await apiClient.get<CaseStatsResponse>('/cases/statistics');
  return response.data;
}

/**
 * Add document to case
 */
export async function addDocumentToCase(
  caseId: string,
  data: AddDocumentRequest
): Promise<CaseDocument> {
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('document_type', data.document_type);

  const response = await apiClient.post<CaseDocument>(
    `/cases/${caseId}/documents`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

/**
 * Add note to case
 */
export async function addNoteToCase(
  caseId: string,
  data: AddNoteRequest
): Promise<CaseNote> {
  const response = await apiClient.post<CaseNote>(`/cases/${caseId}/notes`, data);
  return response.data;
}

/**
 * Change case status
 */
export async function changeCaseStatus(
  caseId: string,
  status: CaseBase['status']
): Promise<CaseBase> {
  const response = await apiClient.patch<CaseBase>(`/cases/${caseId}/status`, {
    status,
  });
  return response.data;
}
