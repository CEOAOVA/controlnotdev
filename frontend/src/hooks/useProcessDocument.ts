/**
 * useProcessDocument - Main hook for orchestrating document processing workflow
 * Handles: OCR → AI Extraction → Edit → Generate
 */

import { useMutation } from '@tanstack/react-query';
import { extractionApi, documentsApi } from '@/api/endpoints';
import { useDocumentStore, useCategoryStore } from '@/store';
import type { OCRRequest, AIExtractionRequest, GenerateDocumentRequest } from '@/api/types';

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
      setOCRResults(data.ocr_results);
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
      setConfidence(data.confidence || null);
      setProcessing(false, 'complete');
    },
    onError: (error: any) => {
      setError(error?.message || 'Error durante la extracción con IA');
      setProcessing(false, 'idle');
    },
  });

  // Document Generation
  const generateMutation = useMutation({
    mutationFn: async (request: GenerateDocumentRequest) => {
      return documentsApi.generate(request);
    },
    onError: (error: any) => {
      setError(error?.message || 'Error al generar documento');
    },
  });

  // Send Email
  const emailMutation = useMutation({
    mutationFn: documentsApi.sendEmail,
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
      category_name: category,
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
  const generateDocument = async (templateName?: string) => {
    if (!editedData || !documentType) {
      setError('Datos o tipo de documento faltantes');
      return null;
    }

    const request: GenerateDocumentRequest = {
      document_type: documentType,
      data: editedData,
      template_name: templateName,
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
