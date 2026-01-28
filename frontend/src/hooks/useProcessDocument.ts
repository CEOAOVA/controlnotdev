/**
 * useProcessDocument - Main hook for orchestrating document processing workflow
 * Handles: Upload → Vision Extraction → Edit → Generate
 *
 * UPDATED FLOW (Vision Direct - better for photos/credentials):
 * 1. Upload files via /documents/upload → get session_id
 * 2. Extract with Claude Vision via /extraction/vision {session_id, document_type}
 *
 * This bypasses OCR for improved accuracy with low-quality images (WhatsApp photos, INEs, etc.)
 */

import { useMutation } from '@tanstack/react-query';
import { extractionApi, documentsApi } from '@/api/endpoints';
import { useDocumentStore, useCategoryStore, useTemplateStore } from '@/store';
import type {
  AIExtractionRequest,
  DocumentGenerationRequest,
  SendEmailRequest,
  QualityLevel,
  LegacyExtractionResponse,
} from '@/api/types';
import type { Category } from '@/types';

export function useProcessDocument() {
  const {
    setProcessing,
    setOCRResults,
    setExtractedData,
    setConfidence,
    setError,
    setQualityReport,
    setValidationReport,
    documentType,
    editedData,
  } = useDocumentStore();

  const { files } = useCategoryStore();
  const { selectedTemplate } = useTemplateStore();

  // Step 1: Upload categorized documents
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!documentType || !selectedTemplate) {
        throw new Error('Tipo de documento o plantilla no seleccionado');
      }

      setProcessing(true, 'ocr');
      setError(null);

      // Transform files from store format to API format
      const categorizedFiles: Record<Category, File[]> = {
        parte_a: [],
        parte_b: [],
        otros: [],
      };

      Object.entries(files).forEach(([category, uploadedFiles]) => {
        const cat = category as Category;
        categorizedFiles[cat] = uploadedFiles.map((f) => f.file);
      });

      return documentsApi.uploadCategorized(
        documentType,
        selectedTemplate.id,
        categorizedFiles
      );
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error al subir documentos';
      setError(message);
      setProcessing(false, 'idle');
    },
  });

  // Step 2: Process OCR
  const ocrMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      setProcessing(true, 'ocr');
      return extractionApi.processOCR(sessionId);
    },
    onSuccess: (data) => {
      // Transform OCR results to store format: concatenate text from each category
      if (data.results_by_category) {
        const transformedResults: { [category: string]: string } = {};
        Object.entries(data.results_by_category).forEach(([category, results]) => {
          if (Array.isArray(results)) {
            transformedResults[category] = results
              .filter((r) => r.success && r.text)
              .map((r) => r.text || '')
              .join('\n\n');
          }
        });
        setOCRResults(transformedResults);
      }
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error durante el OCR';
      setError(message);
      setProcessing(false, 'idle');
    },
  });

  // Step 3: AI Extraction (legacy - kept for backward compatibility)
  const aiMutation = useMutation({
    mutationFn: async (request: AIExtractionRequest) => {
      setProcessing(true, 'ai');
      setError(null);
      return extractionApi.extractWithAI(request);
    },
    onSuccess: (data) => {
      setExtractedData(data.extracted_data);
      if (data.completeness_percent !== undefined) {
        setConfidence(data.completeness_percent / 100);
      }
      setProcessing(false, 'complete');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error durante la extracción con IA';
      setError(message);
      setProcessing(false, 'idle');
    },
  });

  // Vision Extraction (preferred - better for photos/credentials)
  const visionMutation = useMutation({
    mutationFn: async ({
      sessionId,
      docType,
      qualityLevel,
      documentHints,
      enableValidation = true,
    }: {
      sessionId: string;
      docType: string;
      qualityLevel?: QualityLevel;
      documentHints?: string[];
      enableValidation?: boolean;
    }) => {
      setProcessing(true, 'ai');
      setError(null);
      return extractionApi.extractWithVision(sessionId, docType, {
        qualityLevel,
        documentHints,
        enableValidation,
      });
    },
    onSuccess: (data) => {
      setExtractedData(data.extracted_data);
      if (data.completeness_percent !== undefined) {
        setConfidence(data.completeness_percent / 100);
      }
      // OCR Robusto 2025: guardar reports de calidad y validación
      if (data.quality_report) {
        setQualityReport(data.quality_report);
      }
      if (data.validation_report) {
        setValidationReport(data.validation_report);
      }
      setProcessing(false, 'complete');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error durante la extracción con Vision';
      setError(message);
      setProcessing(false, 'idle');
    },
  });

  // Legacy Extraction for Cancelaciones (100% accuracy - movil_cancelaciones.py method)
  const legacyMutation = useMutation({
    mutationFn: async (text: string): Promise<LegacyExtractionResponse> => {
      setProcessing(true, 'ai');
      setError(null);
      return extractionApi.extractCancelacionLegacy(text);
    },
    onSuccess: (data) => {
      setExtractedData(data.extracted_data);
      if (data.stats?.tasa_exito_percent !== undefined) {
        setConfidence(data.stats.tasa_exito_percent / 100);
      }
      setProcessing(false, 'complete');
      console.log('[ProcessDocument] Legacy extraction complete', {
        campos_encontrados: data.stats?.campos_encontrados,
        tasa_exito: data.stats?.tasa_exito_percent,
      });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error durante la extracción legacy';
      setError(message);
      setProcessing(false, 'idle');
    },
  });

  // Document Generation
  const generateMutation = useMutation({
    mutationFn: async (request: DocumentGenerationRequest) => {
      return documentsApi.generate(request);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error al generar documento';
      setError(message);
    },
  });

  // Send Email
  const emailMutation = useMutation({
    mutationFn: async (request: SendEmailRequest) => {
      return documentsApi.sendEmail(request);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.message || 'Error al enviar email';
      setError(message);
    },
  });

  /**
   * Process document extraction using Claude Vision or Legacy method
   *
   * FLOW DEPENDS ON DOCUMENT TYPE:
   *
   * For CANCELACIONES (legacy - 100% accuracy):
   * 1. Upload files to /documents/upload → get session_id
   * 2. Process OCR to get text
   * 3. Extract with legacy method (movil_cancelaciones.py parameters)
   *
   * For OTHER DOCUMENTS (Vision Direct):
   * 1. Upload files to /documents/upload → get session_id
   * 2. Extract with Claude Vision (sends images directly to Claude)
   */
  const processFullWorkflow = async () => {
    if (!documentType) {
      setError('Tipo de documento no seleccionado');
      return;
    }

    if (!selectedTemplate) {
      setError('Plantilla no seleccionada');
      return;
    }

    // Check if there are files to process
    const hasFiles = Object.values(files).some((categoryFiles) => categoryFiles.length > 0);
    if (!hasFiles) {
      setError('No hay documentos para procesar');
      return;
    }

    try {
      // Step 1: Upload files and get session_id
      console.log('[ProcessDocument] Step 1: Uploading files...');
      const uploadResult = await uploadMutation.mutateAsync();
      const sessionId = uploadResult.session_id;
      console.log('[ProcessDocument] Upload complete, session_id:', sessionId);

      // Step 2: Extract based on document type
      if (documentType === 'cancelacion') {
        // CANCELACIONES: Use legacy method (OCR → Legacy Extraction)
        // This achieves 100% extraction accuracy
        console.log('[ProcessDocument] Step 2a: Processing OCR for cancelacion...');
        const ocrResult = await ocrMutation.mutateAsync(sessionId);
        console.log('[ProcessDocument] OCR complete, text length:', ocrResult.extracted_text?.length);

        console.log('[ProcessDocument] Step 2b: Extracting with LEGACY method (movil_cancelaciones.py)...');
        await legacyMutation.mutateAsync(ocrResult.extracted_text);
        console.log('[ProcessDocument] Legacy extraction complete');
      } else {
        // OTHER DOCUMENTS: Use Claude Vision directly (bypasses OCR)
        console.log('[ProcessDocument] Step 2: Extracting with Claude Vision...');
        await visionMutation.mutateAsync({
          sessionId,
          docType: documentType,
        });
        console.log('[ProcessDocument] Vision extraction complete');
      }

    } catch (error: any) {
      console.error('[ProcessDocument] Workflow failed:', error);
      // Error already set by individual mutations
    }
  };

  // Helper to generate document with current edited data
  const generateDocument = async (
    templateId: string,
    placeholdersList?: string[],
    outputFilename?: string
  ) => {
    if (!editedData || !documentType) {
      setError('Datos o tipo de documento faltantes');
      return null;
    }

    // Convert editedData values to strings for DocumentGenerationRequest
    const responses: Record<string, string> = {};
    Object.entries(editedData).forEach(([key, value]) => {
      responses[key] = value != null ? String(value) : '';
    });

    const request: DocumentGenerationRequest = {
      template_id: templateId,
      responses,
      placeholders: placeholdersList || Object.keys(editedData),
      output_filename: outputFilename || `documento_${documentType}_${Date.now()}.docx`,
    };

    const result = await generateMutation.mutateAsync(request);
    return result;
  };

  return {
    // Mutations
    uploadMutation,
    ocrMutation,
    aiMutation,
    visionMutation,
    legacyMutation,  // NEW: Legacy extraction for cancelaciones
    generateMutation,
    emailMutation,

    // Helper functions
    processFullWorkflow,
    generateDocument,

    // Loading states
    isUploading: uploadMutation.isPending,
    isProcessingOCR: ocrMutation.isPending,
    isProcessingAI: aiMutation.isPending,
    isProcessingVision: visionMutation.isPending,
    isProcessingLegacy: legacyMutation.isPending,  // NEW
    isGenerating: generateMutation.isPending,
    isSendingEmail: emailMutation.isPending,

    // Overall loading (includes Vision and Legacy)
    isProcessing: uploadMutation.isPending || ocrMutation.isPending || aiMutation.isPending || visionMutation.isPending || legacyMutation.isPending,
  };
}
