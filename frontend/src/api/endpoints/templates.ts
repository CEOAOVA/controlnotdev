/**
 * Templates API endpoints
 * Connects to: /api/templates/*
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
   * POST /api/templates/upload
   * Upload a Word template (.docx)
   */
  upload: async (file: File): Promise<PlaceholderExtractionResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post<PlaceholderExtractionResponse>(
      '/api/templates/upload',
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
   * GET /api/templates/list
   * List all available templates
   */
  list: async (source?: 'drive' | 'local'): Promise<TemplateListResponse> => {
    const { data } = await apiClient.get<TemplateListResponse>(
      '/api/templates/list',
      {
        params: { source },
      }
    );

    return data;
  },

  /**
   * POST /api/templates/confirm
   * Confirm template and document type
   */
  confirm: async (
    payload: TemplateConfirmRequest
  ): Promise<TemplateConfirmResponse> => {
    const { data } = await apiClient.post<TemplateConfirmResponse>(
      '/api/templates/confirm',
      payload
    );

    return data;
  },

  /**
   * GET /api/templates/types
   * Get available document types
   */
  getTypes: async (): Promise<DocumentTypesListResponse> => {
    const { data } = await apiClient.get<DocumentTypesListResponse>(
      '/api/templates/types'
    );

    return data;
  },
};
