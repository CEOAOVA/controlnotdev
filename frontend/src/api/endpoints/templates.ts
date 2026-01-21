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
  StandardKeysResponse,
  TemplateMappingResponse,
  UpdateMappingResponse,
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

  /**
   * DELETE /templates/{templateId}
   * Delete a template
   */
  delete: async (templateId: string): Promise<void> => {
    await apiClient.delete(`/templates/${templateId}`);
  },

  /**
   * GET /templates/{templateId}/standard-keys
   * Get standard keys available for the template's document type
   */
  getStandardKeys: async (templateId: string): Promise<StandardKeysResponse> => {
    const { data } = await apiClient.get<StandardKeysResponse>(
      `/templates/${templateId}/standard-keys`
    );
    return data;
  },

  /**
   * GET /templates/{templateId}/mapping
   * Get current placeholder mapping for a template
   */
  getMapping: async (templateId: string): Promise<TemplateMappingResponse> => {
    const { data } = await apiClient.get<TemplateMappingResponse>(
      `/templates/${templateId}/mapping`
    );
    return data;
  },

  /**
   * PUT /templates/{templateId}/mapping
   * Update placeholder mapping for a template
   */
  updateMapping: async (
    templateId: string,
    mapping: Record<string, string>
  ): Promise<UpdateMappingResponse> => {
    const { data } = await apiClient.put<UpdateMappingResponse>(
      `/templates/${templateId}/mapping`,
      { mapping }
    );
    return data;
  },
};
