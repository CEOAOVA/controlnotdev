/**
 * useTemplates - Hook for managing templates
 * Handles: Loading templates, uploading, detecting document type
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { templatesApi } from '@/api/endpoints';
import { useTemplateStore, useDocumentStore } from '@/store';
import type { TemplateInfo } from '@/store';

export function useTemplates() {
  const {
    setAvailableTemplates,
    setSelectedTemplate,
    setPlaceholders,
    setDetectedType,
    setLoading,
    setError,
    selectedTemplate,
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
          id: t.name,
          name: t.display_name || t.name,
          type: t.document_type,
          source: t.source as 'drive' | 'local',
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

      if (data.detected_type) {
        setDetectedType(data.detected_type);
        setDocumentType(data.detected_type);
      }

      setLoading(false);
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al subir template');
      setLoading(false);
    },
  });

  // Mutation to confirm template selection
  const confirmMutation = useMutation({
    mutationFn: templatesApi.confirm,
    onSuccess: (data) => {
      if (data.document_type) {
        setDocumentType(data.document_type);
        setDetectedType(data.document_type);
      }
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al confirmar template');
    },
  });

  // Helper to select and confirm a template
  const selectTemplate = async (template: TemplateInfo) => {
    setSelectedTemplate(template);

    // If template has a file (uploaded), upload it first
    if (template.uploadedFile) {
      const result = await uploadMutation.mutateAsync(template.uploadedFile);

      // Confirm with detected type
      if (result.detected_type) {
        await confirmMutation.mutateAsync({
          template_name: template.name,
          document_type: result.detected_type,
        });
      }
    } else {
      // Confirm existing template
      if (template.type) {
        await confirmMutation.mutateAsync({
          template_name: template.name,
          document_type: template.type,
        });
      }
    }
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

  return {
    // Queries
    templatesQuery,

    // Mutations
    uploadMutation,
    confirmMutation,

    // Helpers
    selectTemplate,
    uploadCustomTemplate,

    // Loading states
    isLoadingTemplates: templatesQuery.isLoading,
    isUploading: uploadMutation.isPending,
    isConfirming: confirmMutation.isPending,

    // Data
    templates: templatesQuery.data || [],
    selectedTemplate,
  };
}
