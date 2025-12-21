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
   */
  extractWithVision: async (
    sessionId: string,
    documentType: string
  ): Promise<AIExtractionResponse> => {
    const { data } = await apiClient.post<AIExtractionResponse>(
      '/extraction/vision',
      {
        session_id: sessionId,
        document_type: documentType,
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
};
