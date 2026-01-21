/**
 * usePlaceholderMapping - Hook for managing placeholder to standard key mappings
 * Handles: Loading mapping, loading standard keys, updating mapping
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { templatesApi } from '@/api/endpoints';
import type {
  StandardKey,
  TemplateMappingResponse,
  UpdateMappingResponse,
} from '@/api/types';

interface UsePlaceholderMappingOptions {
  /** Enable queries when template ID is provided */
  enabled?: boolean;
}

export function usePlaceholderMapping(
  templateId: string | null,
  options: UsePlaceholderMappingOptions = {}
) {
  const queryClient = useQueryClient();
  const { enabled = true } = options;

  // Query to load current placeholder mapping
  const mappingQuery = useQuery({
    queryKey: ['template-mapping', templateId],
    queryFn: async () => {
      if (!templateId) throw new Error('Template ID is required');
      return templatesApi.getMapping(templateId);
    },
    enabled: enabled && !!templateId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Query to load standard keys for the document type
  const standardKeysQuery = useQuery({
    queryKey: ['standard-keys', templateId],
    queryFn: async () => {
      if (!templateId) throw new Error('Template ID is required');
      return templatesApi.getStandardKeys(templateId);
    },
    enabled: enabled && !!templateId,
    staleTime: 10 * 60 * 1000, // 10 minutes (keys don't change often)
  });

  // Mutation to update mapping
  const updateMappingMutation = useMutation({
    mutationFn: async (newMapping: Record<string, string>) => {
      if (!templateId) throw new Error('Template ID is required');
      return templatesApi.updateMapping(templateId, newMapping);
    },
    onSuccess: (data) => {
      // Update the cache with new mapping
      queryClient.setQueryData<TemplateMappingResponse>(
        ['template-mapping', templateId],
        (old) => {
          if (!old) return old;
          return {
            ...old,
            mapping: data.mapping,
            total_mapped: Object.keys(data.mapping).length,
          };
        }
      );

      // Invalidate templates list to reflect any changes
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  // Helper to get mapped key for a placeholder
  const getMappedKey = (placeholder: string): string => {
    return mappingQuery.data?.mapping[placeholder] || placeholder;
  };

  // Helper to find standard key by name
  const findStandardKey = (keyName: string): StandardKey | undefined => {
    return standardKeysQuery.data?.keys.find((k) => k.key === keyName);
  };

  // Helper to check if a placeholder is properly mapped
  const isPlaceholderMapped = (placeholder: string): boolean => {
    const mappedKey = getMappedKey(placeholder);
    // Consider mapped if:
    // 1. Key is different from placeholder (explicit mapping)
    // 2. Key exists in standard keys
    if (mappedKey === placeholder) {
      // Check if placeholder itself is a standard key
      return !!findStandardKey(placeholder);
    }
    return !!findStandardKey(mappedKey);
  };

  // Calculate mapping stats
  const getMappingStats = () => {
    const data = mappingQuery.data;
    if (!data) return null;

    const totalPlaceholders = data.total_placeholders;
    const mappedCount = data.total_mapped;
    const unmappedCount = totalPlaceholders - mappedCount;
    const mappingPercentage = totalPlaceholders > 0
      ? Math.round((mappedCount / totalPlaceholders) * 100)
      : 0;

    return {
      totalPlaceholders,
      mappedCount,
      unmappedCount,
      mappingPercentage,
      hasUnmapped: unmappedCount > 0,
    };
  };

  return {
    // Queries
    mappingQuery,
    standardKeysQuery,

    // Mutations
    updateMappingMutation,

    // Data
    mapping: mappingQuery.data?.mapping || {},
    placeholders: mappingQuery.data?.placeholders || [],
    standardKeys: standardKeysQuery.data?.keys || [],
    documentType: mappingQuery.data?.document_type,
    templateName: mappingQuery.data?.template_name,

    // Stats
    stats: getMappingStats(),

    // Helpers
    getMappedKey,
    findStandardKey,
    isPlaceholderMapped,

    // Loading states
    isLoadingMapping: mappingQuery.isLoading,
    isLoadingKeys: standardKeysQuery.isLoading,
    isLoading: mappingQuery.isLoading || standardKeysQuery.isLoading,
    isUpdating: updateMappingMutation.isPending,

    // Error states
    mappingError: mappingQuery.error?.message || null,
    keysError: standardKeysQuery.error?.message || null,
    updateError: updateMappingMutation.error?.message || null,

    // Actions
    updateMapping: updateMappingMutation.mutateAsync,
    refetch: () => {
      mappingQuery.refetch();
      standardKeysQuery.refetch();
    },
  };
}

// Export types for use in components
export type { StandardKey, TemplateMappingResponse, UpdateMappingResponse };
