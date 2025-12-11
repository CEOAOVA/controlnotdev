/**
 * useTemplates - Hook for managing templates
 * Handles: Loading templates, uploading, detecting document type
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { useCallback } from 'react';
import { templatesApi } from '@/api/endpoints';
import { useTemplateStore, useDocumentStore } from '@/store';
import type { TemplateInfo } from '@/store';

export function useTemplates() {
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

    // IMPORTANTE: Setear documentType inmediatamente si el template lo tiene
    // Esto activa useCategories que depende de documentType
    if (template.type) {
      setDocumentType(template.type);
      setDetectedType(template.type);
    }

    // If template has a file (uploaded), upload it first
    if (template.uploadedFile) {
      const result = await uploadMutation.mutateAsync(template.uploadedFile);

      // Confirm with detected type
      if (result.detected_type) {
        await confirmMutation.mutateAsync({
          template_id: result.template_id,
          document_type: result.detected_type,
          confirmed: true,
        });
      }
    } else if (template.type) {
      // Confirm existing template with its type
      await confirmMutation.mutateAsync({
        template_id: template.id,
        document_type: template.type,
        confirmed: true,
      });
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

  const deleteTemplate = async (_templateId: string) => {
    // TODO: Implement delete API call when backend supports it
    console.warn('Delete template not implemented in backend yet');
    throw new Error('Funcionalidad de eliminar no disponible aún');
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
    confirmMutation,

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
    isConfirming: confirmMutation.isPending,
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
