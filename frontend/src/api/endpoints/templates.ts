/**
 * Templates API endpoints
 * Connects to: /api/templates/*
 * NOTE: apiClient already has baseURL with /api prefix, so paths here don't need /api
 */

import { apiClient } from '../client';
import type {
  PlaceholderExtractionResponse,
  TemplateConfirmRequest,
  TemplateConfirmResponse,
  TemplateListResponse,
  DocumentTypesListResponse,
} from '../types';

export const templatesApi = {
  /**
   * POST /templates/upload
   * Upload a Word template (.docx)
   */
  upload: async (file: File): Promise<PlaceholderExtractionResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post<PlaceholderExtractionResponse>(
      '/templates/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return data;
  },

  /**
   * GET /templates/list
   * List all available templates
   */
  list: async (source?: 'drive' | 'local'): Promise<TemplateListResponse> => {
    const { data } = await apiClient.get<TemplateListResponse>(
      '/templates/list',
      {
        params: { source },
      }
    );

    return data;
  },

  /**
   * POST /templates/confirm
   * Confirm template and document type
   */
  confirm: async (
    payload: TemplateConfirmRequest
  ): Promise<TemplateConfirmResponse> => {
    const { data } = await apiClient.post<TemplateConfirmResponse>(
      '/templates/confirm',
      payload
    );

    return data;
  },

  /**
   * GET /templates/types
   * Get available document types
   */
  getTypes: async (): Promise<DocumentTypesListResponse> => {
    const { data } = await apiClient.get<DocumentTypesListResponse>(
      '/templates/types'
    );

    return data;
  },
};
