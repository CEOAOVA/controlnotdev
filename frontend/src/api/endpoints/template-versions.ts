/**
 * Template Versions API endpoints
 * Connects to: /api/templates/{id}/versions/*
 */

import { apiClient } from '../client';
import type {
  TemplateVersion,
  TemplateVersionListResponse,
  VersionCompareRequest,
  VersionCompareResponse,
  ActivateVersionResponse,
} from '../types/version-types';

export const templateVersionsApi = {
  /**
   * GET /templates/{templateId}/versions
   * List all versions of a template
   */
  list: async (templateId: string): Promise<TemplateVersionListResponse> => {
    const { data } = await apiClient.get<TemplateVersionListResponse>(
      `/templates/${templateId}/versions`
    );
    return data;
  },

  /**
   * GET /templates/{templateId}/versions/active
   * Get the active version of a template
   */
  getActive: async (templateId: string): Promise<TemplateVersion> => {
    const { data } = await apiClient.get<TemplateVersion>(
      `/templates/${templateId}/versions/active`
    );
    return data;
  },

  /**
   * GET /templates/{templateId}/versions/{versionId}
   * Get details of a specific version
   */
  getDetail: async (
    templateId: string,
    versionId: string
  ): Promise<TemplateVersion> => {
    const { data } = await apiClient.get<TemplateVersion>(
      `/templates/${templateId}/versions/${versionId}`
    );
    return data;
  },

  /**
   * POST /templates/{templateId}/versions/{versionId}/activate
   * Activate a specific version (rollback)
   */
  activate: async (
    templateId: string,
    versionId: string
  ): Promise<ActivateVersionResponse> => {
    const { data } = await apiClient.post<ActivateVersionResponse>(
      `/templates/${templateId}/versions/${versionId}/activate`
    );
    return data;
  },

  /**
   * POST /templates/{templateId}/versions/compare
   * Compare two versions
   */
  compare: async (
    templateId: string,
    payload: VersionCompareRequest
  ): Promise<VersionCompareResponse> => {
    const { data } = await apiClient.post<VersionCompareResponse>(
      `/templates/${templateId}/versions/compare`,
      payload
    );
    return data;
  },
};
