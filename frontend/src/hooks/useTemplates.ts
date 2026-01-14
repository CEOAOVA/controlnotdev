/**
 * useTemplates - Hook for managing templates
 * Handles: Loading templates, uploading, detecting document type
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { templatesApi } from '@/api/endpoints';
import { useTemplateStore, useDocumentStore } from '@/store';
import type { TemplateInfo } from '@/store';

export function useTemplates() {
  const queryClient = useQueryClient();

  const {
    setAvailableTemplates,
    setSelectedTemplate,
    setPlaceholders,
    setDetectedType,
    setConfidence,
    setLoading,
    setError,
    selectedTemplate,
    confidenceScore,
    requiresConfirmation,
  } = useTemplateStore();

  const { setDocumentType } = useDocumentStore();

  // Query to load available templates
  const templatesQuery = useQuery({
    queryKey: ['templates', 'list'],
    queryFn: async () => {
      setLoading(true);
      try {
        const response = await templatesApi.list();

        // Transform to TemplateInfo format
        const templates: TemplateInfo[] = response.templates.map((t) => ({
          id: t.id || t.name,  // Usar UUID del backend, fallback a nombre
          name: t.display_name || t.name,
          type: t.document_type,
          source: t.source as 'drive' | 'local' | 'uploaded' | 'supabase',
          placeholders: t.placeholders,
        }));

        setAvailableTemplates(templates);
        setLoading(false);
        return templates;
      } catch (error: any) {
        setError(error?.message || 'Error al cargar templates');
        setLoading(false);
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Mutation to upload custom template
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setLoading(true);
      setError(null);
      return templatesApi.upload(file);
    },
    onSuccess: (data) => {
      // Set placeholders and detected type
      setPlaceholders(data.placeholders);

      // Set detected type
      const detectedType = data.detected_type || data.document_type;
      if (detectedType) {
        setDetectedType(detectedType);
        setDocumentType(detectedType);
      }

      // Set confidence score from API response
      if (data.confidence_score !== undefined) {
        setConfidence(data.confidence_score, data.requires_confirmation || false);
      }

      setLoading(false);
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al subir template');
      setLoading(false);
    },
  });

  // Helper to select a template (removed server-side confirm - state is managed locally)
  const selectTemplate = async (template: TemplateInfo) => {
    setSelectedTemplate(template);

    // IMPORTANTE: Setear documentType inmediatamente si el template lo tiene
    // Esto activa useCategories que depende de documentType
    if (template.type) {
      setDocumentType(template.type);
      setDetectedType(template.type);
    }

    // If template has a file (uploaded), upload it first
    if (template.uploadedFile) {
      const result = await uploadMutation.mutateAsync(template.uploadedFile);

      // Set detected type from upload response (no server-side confirm needed)
      if (result.detected_type) {
        setDocumentType(result.detected_type);
        setDetectedType(result.detected_type);
      }
    }
    // For existing templates, the type is already set above - no confirm needed
  };

  // Helper to upload a custom template
  const uploadCustomTemplate = async (file: File) => {
    const result = await uploadMutation.mutateAsync(file);

    // Create template info
    const customTemplate: TemplateInfo = {
      id: `custom-${Date.now()}`,
      name: file.name,
      source: 'uploaded',
      type: result.detected_type,
      placeholders: result.placeholders,
      uploadedFile: file,
    };

    setSelectedTemplate(customTemplate);
    return customTemplate;
  };

  // Wrapper functions for Templates.tsx compatibility
  // Memoized to prevent infinite re-renders in useEffect dependencies
  const fetchTemplates = useCallback(() => {
    templatesQuery.refetch();
  }, []);

  const uploadTemplate = async (file: File, _name?: string, _type?: string) => {
    const result = await uploadMutation.mutateAsync(file);
    // After upload, refetch templates list
    await templatesQuery.refetch();
    return result;
  };

  const deleteTemplate = async (templateId: string) => {
    await templatesApi.delete(templateId);
    // Invalidar query para refrescar lista
    await queryClient.invalidateQueries({ queryKey: ['templates'] });
  };

  const updateTemplateName = async (_templateId: string, _newName: string) => {
    // TODO: Implement update API call when backend supports it
    console.warn('Update template not implemented in backend yet');
    throw new Error('Funcionalidad de actualizar nombre no disponible aún');
  };

  // Get error from store or query
  const { error } = useTemplateStore.getState();

  return {
    // Queries
    templatesQuery,

    // Mutations
    uploadMutation,

    // Helpers
    selectTemplate,
    uploadCustomTemplate,

    // For Templates.tsx page compatibility
    fetchTemplates,
    uploadTemplate,
    deleteTemplate,
    updateTemplateName,

    // Loading states
    isLoadingTemplates: templatesQuery.isLoading,
    isUploading: uploadMutation.isPending,
    isLoading: templatesQuery.isLoading || uploadMutation.isPending,

    // Error
    error: templatesQuery.error?.message || error || null,

    // Data
    templates: templatesQuery.data || [],
    selectedTemplate,

    // Confidence (for auto-detection)
    confidenceScore,
    requiresConfirmation,
  };
}
