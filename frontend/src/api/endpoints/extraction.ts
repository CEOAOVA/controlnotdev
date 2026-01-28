/**
 * Extraction API endpoints (OCR + AI)
 * Connects to: /api/extraction/*
 */

import { apiClient } from '../client';
import type {
  OCRResponse,
  AIExtractionRequest,
  AIExtractionResponse,
  DataEditRequest,
  DataEditResponse,
  QualityLevel,
  LegacyExtractionResponse,
} from '../types';

export const extractionApi = {
  /**
   * POST /api/extraction/ocr
   * Process OCR for documents in an existing session
   *
   * IMPORTANT: Files must be uploaded first via /documents/upload
   * This endpoint processes files already stored in the session
   */
  processOCR: async (sessionId: string): Promise<OCRResponse> => {
    const { data } = await apiClient.post<OCRResponse>(
      `/extraction/ocr?session_id=${encodeURIComponent(sessionId)}`,
      {},
      {
        // OCR can take a while, extend timeout
        timeout: 120000, // 2 minutes
      }
    );

    return data;
  },

  /**
   * POST /api/extraction/ai
   * Extract structured data from OCR text using AI
   */
  extractWithAI: async (
    payload: AIExtractionRequest
  ): Promise<AIExtractionResponse> => {
    const { data } = await apiClient.post<AIExtractionResponse>(
      '/extraction/ai',
      payload,
      {
        // AI extraction can take a while
        timeout: 180000, // 3 minutes
      }
    );

    return data;
  },

  /**
   * POST /api/extraction/vision
   * Extract data directly from images using Claude Vision
   * Better for photos of documents (INE, credentials, etc.)
   * Bypasses OCR step for improved accuracy with low-quality images
   *
   * OCR Robusto 2025:
   * - quality_level: Informs Claude about image quality for specialized prompts
   * - document_hints: List of document type hints for specialized extraction
   */
  extractWithVision: async (
    sessionId: string,
    documentType: string,
    options?: {
      qualityLevel?: QualityLevel;
      documentHints?: string[];
      enableValidation?: boolean;
    }
  ): Promise<AIExtractionResponse> => {
    const { data } = await apiClient.post<AIExtractionResponse>(
      '/extraction/vision',
      {
        session_id: sessionId,
        document_type: documentType,
        // OCR Robusto 2025 parameters
        quality_level: options?.qualityLevel || 'high',
        document_hints: options?.documentHints,
        enable_validation: options?.enableValidation ?? true,
      },
      {
        // Vision extraction can take longer with many images
        timeout: 300000, // 5 minutes
      }
    );

    return data;
  },

  /**
   * POST /api/extraction/edit
   * Save edited data
   */
  saveEditedData: async (
    payload: DataEditRequest
  ): Promise<DataEditResponse> => {
    const { data } = await apiClient.post<DataEditResponse>(
      '/extraction/edit',
      payload
    );

    return data;
  },

  /**
   * POST /api/cancelaciones/legacy/extract
   * Extract cancellation data using the LEGACY method from movil_cancelaciones.py
   *
   * This method achieves 100% extraction accuracy using:
   * - model: gpt-4o
   * - temperature: 0.5 (NOT 0.0)
   * - max_tokens: 1500 (NOT 3000)
   * - top_p: 1
   * - Simple prompt with CLAVES_ESTANDARIZADAS_LEGACY
   *
   * @param text - OCR text from cancellation documents
   * @returns Extracted data with 31 fields formatted with **bold** for Word
   */
  extractCancelacionLegacy: async (
    text: string
  ): Promise<LegacyExtractionResponse> => {
    const formData = new FormData();
    formData.append('text', text);

    const { data } = await apiClient.post<LegacyExtractionResponse>(
      '/cancelaciones/legacy/extract',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000, // 3 minutes
      }
    );

    return data;
  },
};
