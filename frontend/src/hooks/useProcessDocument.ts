/**
 * useProcessDocument - Main hook for orchestrating document processing workflow
 * Handles: Upload → OCR → AI Extraction → Edit → Generate
 *
 * CORRECT FLOW:
 * 1. Upload files via /documents/upload → get session_id
 * 2. Process OCR via /extraction/ocr?session_id=xxx
 * 3. Extract with AI via /extraction/ai {session_id, text, document_type}
 */

import { useMutation } from '@tanstack/react-query';
import { extractionApi, documentsApi } from '@/api/endpoints';
import { useDocumentStore, useCategoryStore, useTemplateStore } from '@/store';
import type {
  AIExtractionRequest,
  DocumentGenerationRequest,
  SendEmailRequest,
} from '@/api/types';
import type { Category } from '@/types';

export function useProcessDocument() {
  const {
    setProcessing,
    setOCRResults,
    setExtractedData,
    setConfidence,
    setError,
    documentType,
    editedData,
  } = useDocumentStore();

  const { files } = useCategoryStore();
  const { selectedTemplate, placeholders } = useTemplateStore();

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

  // Step 3: AI Extraction
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
   * Process full OCR + AI workflow
   *
   * CORRECT FLOW:
   * 1. Upload files to /documents/upload → get session_id
   * 2. Process OCR with /extraction/ocr?session_id=xxx
   * 3. Extract with AI using session_id + extracted_text
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

      // Step 2: Process OCR with session_id
      console.log('[ProcessDocument] Step 2: Processing OCR...');
      const ocrResult = await ocrMutation.mutateAsync(sessionId);
      console.log('[ProcessDocument] OCR complete, extracted_text length:', ocrResult.extracted_text?.length);

      // Step 3: AI Extraction with session_id + text
      console.log('[ProcessDocument] Step 3: Extracting with AI...');
      const aiRequest: AIExtractionRequest = {
        session_id: sessionId,
        text: ocrResult.extracted_text,
        document_type: documentType,
        template_placeholders: placeholders.length > 0 ? placeholders : undefined,
      };

      await aiMutation.mutateAsync(aiRequest);
      console.log('[ProcessDocument] AI extraction complete');

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
    generateMutation,
    emailMutation,

    // Helper functions
    processFullWorkflow,
    generateDocument,

    // Loading states
    isUploading: uploadMutation.isPending,
    isProcessingOCR: ocrMutation.isPending,
    isProcessingAI: aiMutation.isPending,
    isGenerating: generateMutation.isPending,
    isSendingEmail: emailMutation.isPending,

    // Overall loading
    isProcessing: uploadMutation.isPending || ocrMutation.isPending || aiMutation.isPending,
  };
}
