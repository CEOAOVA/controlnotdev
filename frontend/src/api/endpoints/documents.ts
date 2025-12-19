/**
 * Documents API Endpoints
 * API client functions for document history management
 */

import { apiClient } from '../client';
import type {
  DocumentListRequest,
  DocumentListResponse,
  DocumentStatsResponse,
  GetDocumentResponse,
  DownloadDocumentResponse,
  EmailDocumentRequest,
  EmailDocumentResponse,
  DeleteDocumentRequest,
  DeleteDocumentResponse,
  DocumentPreviewRequest,
  DocumentPreviewResponse,
} from '../types/documents-types';
import type {
  DocumentGenerationRequest,
  DocumentGenerationResponse,
  SendEmailRequest,
  SendEmailResponse,
  CategorizedDocumentsUploadResponse,
} from '../types/document-types';
import type { Category, DocumentType } from '@/types';

export const documentsApi = {
  /**
   * Upload categorized documents for processing
   * This creates a session and stores files for subsequent OCR processing
   *
   * @param documentType - Type of document (compraventa, donacion, etc.)
   * @param templateId - Template ID to use for generation
   * @param categorizedFiles - Files organized by category (parte_a, parte_b, otros)
   */
  uploadCategorized: async (
    documentType: DocumentType,
    templateId: string,
    categorizedFiles: Record<Category, File[]>
  ): Promise<CategorizedDocumentsUploadResponse> => {
    const formData = new FormData();

    // Add document type and template ID
    formData.append('document_type', documentType);
    formData.append('template_id', templateId);

    // Add files by category
    Object.entries(categorizedFiles).forEach(([category, files]) => {
      files.forEach((file) => {
        formData.append(category, file);
      });
    });

    const response = await apiClient.post<CategorizedDocumentsUploadResponse>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 1 minute for upload
      }
    );
    return response.data;
  },

  /**
   * List all documents with optional filtering and pagination
   */
  list: async (params?: DocumentListRequest): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/documents', {
      params,
    });
    return response.data;
  },

  /**
   * Get document statistics
   */
  getStats: async (): Promise<DocumentStatsResponse> => {
    const response = await apiClient.get<DocumentStatsResponse>('/documents/stats');
    return response.data;
  },

  /**
   * Get a single document by ID
   */
  get: async (documentId: string): Promise<GetDocumentResponse> => {
    const response = await apiClient.get<GetDocumentResponse>(`/documents/${documentId}`);
    return response.data;
  },

  /**
   * Get download URL for a document
   */
  getDownloadUrl: async (documentId: string): Promise<DownloadDocumentResponse> => {
    const response = await apiClient.get<DownloadDocumentResponse>(
      `/documents/${documentId}/download`
    );
    return response.data;
  },

  /**
   * Download a document directly (triggers browser download)
   */
  download: async (documentId: string): Promise<Blob> => {
    const response = await apiClient.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Send document via email
   */
  email: async (request: EmailDocumentRequest): Promise<EmailDocumentResponse> => {
    const response = await apiClient.post<EmailDocumentResponse>(
      `/documents/${request.document_id}/email`,
      {
        to_email: request.to_email,
        subject: request.subject,
        message: request.message,
      }
    );
    return response.data;
  },

  /**
   * Delete a document
   */
  delete: async (request: DeleteDocumentRequest): Promise<DeleteDocumentResponse> => {
    const response = await apiClient.delete<DeleteDocumentResponse>(
      `/documents/${request.document_id}`,
      {
        params: {
          delete_file: request.delete_file,
        },
      }
    );
    return response.data;
  },

  /**
   * Bulk delete documents
   */
  bulkDelete: async (
    documentIds: string[],
    deleteFiles: boolean = false
  ): Promise<{ success: boolean; deleted: number; failed: number }> => {
    const response = await apiClient.post('/documents/bulk-delete', {
      document_ids: documentIds,
      delete_files: deleteFiles,
    });
    return response.data;
  },

  /**
   * Export documents to CSV
   */
  export: async (params?: DocumentListRequest): Promise<Blob> => {
    const response = await apiClient.get('/documents/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Generate a document from template
   */
  generate: async (request: DocumentGenerationRequest): Promise<DocumentGenerationResponse> => {
    const response = await apiClient.post<DocumentGenerationResponse>('/documents/generate', request);
    return response.data;
  },

  /**
   * Send document via email (alternative endpoint)
   */
  sendEmail: async (request: SendEmailRequest): Promise<SendEmailResponse> => {
    const response = await apiClient.post<SendEmailResponse>('/documents/send-email', request);
    return response.data;
  },

  /**
   * Generate a preview of the document (HTML)
   * Shows how the document will look with the current data
   */
  preview: async (request: DocumentPreviewRequest): Promise<DocumentPreviewResponse> => {
    const response = await apiClient.post<DocumentPreviewResponse>('/documents/preview', request);
    return response.data;
  },

  /**
   * Replace/update a document with a new file
   * @param documentId - UUID of the document to replace
   * @param file - New .docx file
   */
  replace: async (documentId: string, file: File): Promise<{ message: string; data: Record<string, unknown> }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.put<{ message: string; data: Record<string, unknown> }>(
      `/documents/${documentId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Download a document by doc_id (generated ID like doc_xxx)
   */
  downloadByDocId: async (docId: string): Promise<Blob> => {
    const response = await apiClient.get(`/documents/download/${docId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
