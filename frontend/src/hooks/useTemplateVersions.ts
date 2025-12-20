/**
 * useTemplateVersions - Hook for managing template versions
 * Handles: Loading versions, activating versions, comparing versions
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import { templateVersionsApi } from '@/api/endpoints';
import type {
  TemplateVersion,
  TemplateVersionListResponse,
  VersionCompareResponse,
} from '@/api/types/version-types';

interface UseTemplateVersionsOptions {
  templateId: string;
  enabled?: boolean;
}

export function useTemplateVersions({
  templateId,
  enabled = true,
}: UseTemplateVersionsOptions) {
  const queryClient = useQueryClient();
  const [compareResult, setCompareResult] = useState<VersionCompareResponse | null>(null);

  // Query to load all versions
  const versionsQuery = useQuery({
    queryKey: ['template-versions', templateId],
    queryFn: async (): Promise<TemplateVersionListResponse> => {
      return templateVersionsApi.list(templateId);
    },
    enabled: enabled && !!templateId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Query to get active version
  const activeVersionQuery = useQuery({
    queryKey: ['template-versions', templateId, 'active'],
    queryFn: async (): Promise<TemplateVersion> => {
      return templateVersionsApi.getActive(templateId);
    },
    enabled: enabled && !!templateId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Mutation to activate a version
  const activateMutation = useMutation({
    mutationFn: async (versionId: string) => {
      return templateVersionsApi.activate(templateId, versionId);
    },
    onSuccess: () => {
      // Invalidate and refetch versions
      queryClient.invalidateQueries({
        queryKey: ['template-versions', templateId],
      });
    },
  });

  // Mutation to compare versions
  const compareMutation = useMutation({
    mutationFn: async ({
      versionId1,
      versionId2,
    }: {
      versionId1: string;
      versionId2: string;
    }) => {
      const result = await templateVersionsApi.compare(templateId, {
        version_id_1: versionId1,
        version_id_2: versionId2,
      });
      setCompareResult(result);
      return result;
    },
  });

  // Helper to activate a version
  const activateVersion = useCallback(
    async (version: TemplateVersion) => {
      return activateMutation.mutateAsync(version.id);
    },
    [activateMutation]
  );

  // Helper to compare two versions
  const compareVersions = useCallback(
    async (version1: TemplateVersion, version2: TemplateVersion) => {
      return compareMutation.mutateAsync({
        versionId1: version1.id,
        versionId2: version2.id,
      });
    },
    [compareMutation]
  );

  // Helper to clear compare result
  const clearCompareResult = useCallback(() => {
    setCompareResult(null);
  }, []);

  // Helper to refetch versions
  const refetchVersions = useCallback(() => {
    versionsQuery.refetch();
    activeVersionQuery.refetch();
  }, [versionsQuery, activeVersionQuery]);

  // Get versions array from query data
  const versions = versionsQuery.data?.versions || [];
  const activeVersion = versions.find((v) => v.es_activa) || activeVersionQuery.data;
  const totalVersions = versionsQuery.data?.total_versions || 0;

  return {
    // Queries
    versionsQuery,
    activeVersionQuery,

    // Mutations
    activateMutation,
    compareMutation,

    // Helpers
    activateVersion,
    compareVersions,
    clearCompareResult,
    refetchVersions,

    // Data
    versions,
    activeVersion,
    totalVersions,
    templateName: versionsQuery.data?.template_name || '',
    compareResult,

    // Loading states
    isLoadingVersions: versionsQuery.isLoading,
    isActivating: activateMutation.isPending,
    isComparing: compareMutation.isPending,
    isLoading:
      versionsQuery.isLoading ||
      activateMutation.isPending ||
      compareMutation.isPending,

    // Errors
    error:
      versionsQuery.error?.message ||
      activateMutation.error?.message ||
      compareMutation.error?.message ||
      null,
  };
}

/**
 * Hook for a single template version detail
 */
export function useTemplateVersion(templateId: string, versionId: string) {
  return useQuery({
    queryKey: ['template-version', templateId, versionId],
    queryFn: async (): Promise<TemplateVersion> => {
      return templateVersionsApi.getDetail(templateId, versionId);
    },
    enabled: !!templateId && !!versionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
