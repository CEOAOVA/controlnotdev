/**
 * Extraction API types
 * Match backend schemas from: backend/app/schemas/extraction_schemas.py
 */

import { Category, DocumentType } from '@/types';

// ============================================
// Quality Assessment Types (OCR Robusto 2025)
// ============================================

/**
 * Quality levels for document images
 */
export type QualityLevel = 'high' | 'medium' | 'low' | 'reject';

/**
 * Quality report from document_quality_service.py
 * Evaluates image quality for OCR processing
 */
export interface QualityReport {
  blur_score: number;        // 0-100, higher is better (sharper)
  contrast_score: number;    // 0-100, higher is better
  brightness_score: number;  // 0-100, higher is better (optimal range)
  resolution_score: number;  // 0-100, based on min dimension
  overall_level: QualityLevel;
  recommendations: string[];
  raw_metrics?: {
    laplacian_variance?: number;
    histogram_std?: number;
    mean_brightness?: number;
    dimensions?: {
      width: number;
      height: number;
      min: number;
    };
  };
}

// ============================================
// Validation Types (Anti-Hallucination 2025)
// ============================================

/**
 * Validation status for individual fields
 */
export type ValidationStatus = 'valid' | 'suspicious' | 'invalid' | 'not_validated';

/**
 * Validation result for a single field
 */
export interface FieldValidation {
  field: string;
  value: string;
  status: ValidationStatus;
  confidence: number;  // 0.0 - 1.0
  issues: string[];
}

/**
 * Complete validation report from validation_service.py
 */
export interface ValidationReport {
  total_fields: number;
  valid_fields: number;
  suspicious_fields: number;
  invalid_fields: number;
  overall_confidence: number;  // 0.0 - 1.0 (average)
  field_validations: FieldValidation[];
}

// ============================================
// OCR Result Types (with confidence)
// ============================================

/**
 * OCR result with confidence metrics
 */
export interface OCRResultWithConfidence {
  text: string;
  confidence: number;  // 0.0 - 1.0
  block_confidences: number[];
  word_count: number;
  success: boolean;
  error?: string;
  preprocessing_applied: 'none' | 'high' | 'medium' | 'low';
}

/**
 * OCR Request - files categorized by role
 */
export interface CategorizedFiles {
  category_name: Category;
  files: File[];
}

export interface OCRRequest {
  document_type: DocumentType;
  categorized_files: CategorizedFiles[];
}

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
  ocr_results?: Record<Category, OCRFileResult[]>;
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
  confidence?: number;
  model_used: string;
  tokens_used: number;
  processing_time_seconds: number;
  // OCR Robusto 2025 - nuevos campos
  quality_report?: QualityReport;
  validation_report?: ValidationReport;
  ocr_confidence?: number;  // Confidence del OCR (0.0-1.0)
  preprocessing_applied?: 'none' | 'high' | 'medium' | 'low';
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

export interface DataEditResponse {
  success: boolean;
  session_id: string;
  message: string;
}

// ============================================
// Legacy Extraction Types (Cancelaciones)
// ============================================

/**
 * Response from /api/cancelaciones/legacy/extract
 * Uses the exact method from movil_cancelaciones.py (100% accuracy)
 */
export interface LegacyExtractionResponse {
  source: string;
  extracted_data: Record<string, string>;
  stats: {
    total_claves: number;
    campos_encontrados: number;
    campos_no_encontrados: number;
    tasa_exito_percent: number;
    lista_encontrados: string[];
    lista_no_encontrados: string[];
  };
  parametros_usados: {
    model: string;
    temperature: number;
    max_tokens: number;
    top_p: number;
  };
  processing_time_seconds: number;
}

/**
 * Legacy keys response from /api/cancelaciones/legacy/keys
 */
export interface LegacyKeysResponse {
  source: string;
  total_claves: number;
  claves: Record<string, string>;
  nota: string;
}
