/**
 * Documents API endpoints
 * Connects to: /api/documents/*
 */

import { apiClient } from '../client';
import type {
  CategorizeRequest,
  CategorizeResponse,
  GenerateDocumentRequest,
  GenerateDocumentResponse,
  SendEmailRequest,
  SendEmailResponse,
} from '../types';

export const documentsApi = {
  /**
   * POST /api/documents/categorize
   * Categorize uploaded files
   */
  categorize: async (
    payload: CategorizeRequest
  ): Promise<CategorizeResponse> => {
    const { data } = await apiClient.post<CategorizeResponse>(
      '/api/documents/categorize',
      payload
    );
    return data;
  },

  /**
   * POST /api/documents/generate
   * Generate final Word document with extracted data
   */
  generate: async (
    payload: GenerateDocumentRequest
  ): Promise<GenerateDocumentResponse> => {
    const { data } = await apiClient.post<GenerateDocumentResponse>(
      '/api/documents/generate',
      payload,
      {
        responseType: 'blob', // Important for file download
      }
    );
    return data;
  },

  /**
   * POST /api/documents/send-email
   * Send generated document via email
   */
  sendEmail: async (payload: SendEmailRequest): Promise<SendEmailResponse> => {
    const { data } = await apiClient.post<SendEmailResponse>(
      '/api/documents/send-email',
      payload
    );
    return data;
  },

  /**
   * GET /api/documents/download/{filename}
   * Download a generated document
   */
  download: async (filename: string): Promise<Blob> => {
    const { data } = await apiClient.get<Blob>(
      `/api/documents/download/${filename}`,
      {
        responseType: 'blob',
      }
    );
    return data;
  },
};
