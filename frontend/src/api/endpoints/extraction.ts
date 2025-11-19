/**
 * Extraction API endpoints (OCR + AI)
 * Connects to: /api/extraction/*
 */

import { apiClient } from '../client';
import type {
  OCRRequest,
  OCRResponse,
  AIExtractionRequest,
  AIExtractionResponse,
  DataEditRequest,
  DataEditResponse,
} from '../types';

export const extractionApi = {
  /**
   * POST /api/extraction/ocr
   * Process categorized images with OCR
   */
  processOCR: async (payload: OCRRequest): Promise<OCRResponse> => {
    const formData = new FormData();

    // Add document type
    formData.append('document_type', payload.document_type);

    // Add categorized files
    payload.categorized_files.forEach((category) => {
      category.files.forEach((file) => {
        formData.append(`${category.category_name}[]`, file);
      });
    });

    const { data } = await apiClient.post<OCRResponse>(
      '/api/extraction/ocr',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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
      '/api/extraction/ai',
      payload,
      {
        // AI extraction can take a while
        timeout: 180000, // 3 minutes
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
      '/api/extraction/edit',
      payload
    );

    return data;
  },
};
