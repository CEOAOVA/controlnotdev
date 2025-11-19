/**
 * Models API endpoints
 * Connects to: /api/models/*
 */

import { apiClient } from '../client';
import type {
  DocumentTypesListResponse,
  CategoriesResponse,
  AIModelsResponse,
} from '../types';

export const modelsApi = {
  /**
   * GET /api/models/types
   * Get available document types
   */
  getDocumentTypes: async (): Promise<DocumentTypesListResponse> => {
    const { data } = await apiClient.get<DocumentTypesListResponse>(
      '/api/models/types'
    );
    return data;
  },

  /**
   * GET /api/models/categories/{doc_type}
   * Get categories for a specific document type
   */
  getCategories: async (docType: string): Promise<CategoriesResponse> => {
    const { data } = await apiClient.get<CategoriesResponse>(
      `/api/models/categories/${docType}`
    );
    return data;
  },

  /**
   * GET /api/models/ai-models
   * Get available AI models
   */
  getAIModels: async (): Promise<AIModelsResponse> => {
    const { data } = await apiClient.get<AIModelsResponse>(
      '/api/models/ai-models'
    );
    return data;
  },

  /**
   * GET /api/models/ai-provider
   * Get active AI provider
   */
  getAIProvider: async (): Promise<{ provider: string; model: string }> => {
    const { data } = await apiClient.get<{ provider: string; model: string }>(
      '/api/models/ai-provider'
    );
    return data;
  },
};
