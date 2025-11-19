/**
 * Extraction API types
 * Match backend schemas from: backend/app/schemas/extraction_schemas.py
 */

import { Category, DocumentType } from '@/types';

export interface OCRFileResult {
  filename: string;
  success: boolean;
  text?: string;
  error?: string;
}

export interface OCRResponse {
  session_id: string;
  extracted_text: string;
  total_text_length: number;
  files_processed: number;
  files_success: number;
  files_failed: number;
  processing_time_seconds: number;
  results_by_category: Record<Category, OCRFileResult[]>;
}

export interface AIExtractionRequest {
  session_id: string;
  text: string;
  document_type: DocumentType;
  template_placeholders?: string[];
  model?: string;
}

export interface AIExtractionResponse {
  session_id: string;
  extracted_data: Record<string, string>;
  total_keys: number;
  keys_found: number;
  keys_missing: number;
  missing_list: string[];
  completeness_percent: number;
  model_used: string;
  tokens_used: number;
  processing_time_seconds: number;
}

export interface DataEditRequest {
  session_id: string;
  edited_data: Record<string, string>;
  confirmed: boolean;
}

export interface ExtractionResultsResponse {
  session_id: string;
  has_ocr: boolean;
  has_ai_extraction: boolean;
  has_edits: boolean;
  confirmed: boolean;
  text_length: number;
  fields_count: number;
}
