/**
 * useFieldMetadata - Hook for loading field metadata from API
 * Dynamically fetches field definitions for any document type
 *
 * Replaces hardcoded field metadata in DataEditor component
 */

import { useQuery } from '@tanstack/react-query';
import { modelsApi } from '@/api/endpoints';
import type { DocumentFieldsResponse, FieldMetadata } from '@/api/types';

interface UseFieldMetadataOptions {
  enabled?: boolean;
}

export function useFieldMetadata(
  documentType: string | null,
  options: UseFieldMetadataOptions = {}
) {
  const { enabled = true } = options;

  const query = useQuery({
    queryKey: ['field-metadata', documentType],
    queryFn: async (): Promise<DocumentFieldsResponse> => {
      if (!documentType) {
        return {
          document_type: '',
          fields: [],
          categories: [],
          total_fields: 0,
        };
      }

      return modelsApi.getFields(documentType);
    },
    enabled: enabled && !!documentType,
    staleTime: 60 * 60 * 1000, // 1 hour - fields rarely change
    gcTime: 24 * 60 * 60 * 1000, // 24 hours cache
  });

  // Helper to get fields grouped by category
  const getFieldsByCategory = (): Record<string, FieldMetadata[]> => {
    if (!query.data?.fields) return {};

    const grouped: Record<string, FieldMetadata[]> = {};

    query.data.fields.forEach((field) => {
      const category = field.category || 'Otros Datos';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(field);
    });

    return grouped;
  };

  // Helper to get a specific field's metadata
  const getFieldMetadata = (fieldName: string): FieldMetadata | undefined => {
    return query.data?.fields.find((f) => f.name === fieldName);
  };

  // Helper to check if field exists
  const hasField = (fieldName: string): boolean => {
    return query.data?.fields.some((f) => f.name === fieldName) ?? false;
  };

  return {
    // Query state
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    isFetching: query.isFetching,

    // Data
    fields: query.data?.fields ?? [],
    categories: query.data?.categories ?? [],
    totalFields: query.data?.total_fields ?? 0,
    documentType: query.data?.document_type ?? null,

    // Helpers
    getFieldsByCategory,
    getFieldMetadata,
    hasField,

    // Refetch
    refetch: query.refetch,
  };
}
