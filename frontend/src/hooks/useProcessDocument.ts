/**
 * useProcessDocument - Main hook for orchestrating document processing workflow
 * Handles: OCR → AI Extraction → Edit → Generate
 */

import { useMutation } from '@tanstack/react-query';
import { extractionApi, documentsApi } from '@/api/endpoints';
import { useDocumentStore, useCategoryStore } from '@/store';
import type {
  OCRRequest,
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

  // OCR Processing
  const ocrMutation = useMutation({
    mutationFn: async (request: OCRRequest) => {
      setProcessing(true, 'ocr');
      setError(null);
      return extractionApi.processOCR(request);
    },
    onSuccess: (data) => {
      // Transform OCR results to store format: concatenate text from each category
      if (data.ocr_results) {
        const transformedResults: { [category: string]: string } = {};
        Object.entries(data.ocr_results).forEach(([category, results]) => {
          transformedResults[category] = results
            .filter((r) => r.success && r.text)
            .map((r) => r.text)
            .join('\n\n');
        });
        setOCRResults(transformedResults);
      }
      setProcessing(false, 'idle');
    },
    onError: (error: any) => {
      setError(error?.message || 'Error durante el OCR');
      setProcessing(false, 'idle');
    },
  });

  // AI Extraction
  const aiMutation = useMutation({
    mutationFn: async (request: AIExtractionRequest) => {
      setProcessing(true, 'ai');
      setError(null);
      return extractionApi.extractWithAI(request);
    },
    onSuccess: (data) => {
      setExtractedData(data.extracted_data);
      if (data.confidence !== undefined && data.confidence !== null) {
        setConfidence(data.confidence);
      }
      setProcessing(false, 'complete');
    },
    onError: (error: any) => {
      setError(error?.message || 'Error durante la extracción con IA');
      setProcessing(false, 'idle');
    },
  });

  // Document Generation
  const generateMutation = useMutation({
    mutationFn: async (request: DocumentGenerationRequest) => {
      return documentsApi.generate(request);
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al generar documento');
    },
  });

  // Send Email
  const emailMutation = useMutation({
    mutationFn: async (request: SendEmailRequest) => {
      return documentsApi.sendEmail(request);
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al enviar email');
    },
  });

  // Helper to process full OCR + AI workflow
  const processFullWorkflow = async () => {
    if (!documentType) {
      setError('Tipo de documento no seleccionado');
      return;
    }

    // Step 1: OCR
    const categorizedFiles = Object.entries(files).map(([category, uploadedFiles]) => ({
      category_name: category as Category,
      files: uploadedFiles.map((f) => f.file),
    }));

    const ocrRequest: OCRRequest = {
      document_type: documentType,
      categorized_files: categorizedFiles,
    };

    const ocrResult = await ocrMutation.mutateAsync(ocrRequest);

    // Step 2: AI Extraction
    const aiRequest: AIExtractionRequest = {
      document_type: documentType,
      ocr_results: ocrResult.ocr_results,
    };

    await aiMutation.mutateAsync(aiRequest);
  };

  // Helper to generate document with current edited data
  const generateDocument = async (templateId: string, placeholders?: string[], outputFilename?: string) => {
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
      placeholders: placeholders || Object.keys(editedData),
      output_filename: outputFilename || `documento_${documentType}_${Date.now()}.docx`,
    };

    const result = await generateMutation.mutateAsync(request);
    return result;
  };

  return {
    // Mutations
    ocrMutation,
    aiMutation,
    generateMutation,
    emailMutation,

    // Helper functions
    processFullWorkflow,
    generateDocument,

    // Loading states
    isProcessingOCR: ocrMutation.isPending,
    isProcessingAI: aiMutation.isPending,
    isGenerating: generateMutation.isPending,
    isSendingEmail: emailMutation.isPending,

    // Overall loading
    isProcessing: ocrMutation.isPending || aiMutation.isPending,
  };
}
