/**
 * Document Store - Manages extracted and edited document data
 * Updated for OCR Robusto 2025 with quality and validation reports
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { QualityReport, ValidationReport, FieldValidation } from '@/api/types/extraction-types';

export type DocumentType =
  | 'compraventa'
  | 'donacion'
  | 'testamento'
  | 'poder'
  | 'sociedad'
  | 'cancelacion';

interface DocumentData {
  [key: string]: string | number | boolean | null | undefined;
}

interface DocumentState {
  // Document type
  documentType: DocumentType | null;

  // Extracted data from AI
  extractedData: DocumentData | null;

  // User-edited data
  editedData: DocumentData | null;

  // Processing status
  isProcessing: boolean;
  processingStep: 'idle' | 'ocr' | 'ai' | 'complete';
  error: string | null;

  // OCR results (raw text by category)
  ocrResults: {
    [category: string]: string;
  } | null;

  // Confidence scores (legacy - overall)
  confidence: number | null;

  // === OCR Robusto 2025 - Nuevos campos ===

  // Quality report from document_quality_service
  qualityReport: QualityReport | null;

  // Validation report from validation_service
  validationReport: ValidationReport | null;

  // Per-field confidence (from validation_report)
  perFieldConfidence: Record<string, number>;

  // Per-field validation status
  perFieldValidation: Record<string, FieldValidation>;

  // === End OCR Robusto 2025 ===

  // Preview approval (mandatory before generating)
  previewApproved: boolean;

  // Actions
  setDocumentType: (type: DocumentType) => void;
  setExtractedData: (data: DocumentData) => void;
  setEditedData: (data: DocumentData) => void;
  updateField: (fieldName: string, value: any) => void;
  setProcessing: (isProcessing: boolean, step?: DocumentState['processingStep']) => void;
  setError: (error: string | null) => void;
  setOCRResults: (results: DocumentState['ocrResults']) => void;
  setConfidence: (confidence: number) => void;
  // OCR Robusto 2025 actions
  setQualityReport: (report: QualityReport | null) => void;
  setValidationReport: (report: ValidationReport | null) => void;
  getFieldConfidence: (fieldName: string) => number | undefined;
  getFieldValidation: (fieldName: string) => FieldValidation | undefined;
  setPreviewApproved: (approved: boolean) => void;
  reset: () => void;
}

const initialState = {
  documentType: null,
  extractedData: null,
  editedData: null,
  isProcessing: false,
  processingStep: 'idle' as const,
  error: null,
  ocrResults: null,
  confidence: null,
  // OCR Robusto 2025
  qualityReport: null,
  validationReport: null,
  perFieldConfidence: {} as Record<string, number>,
  perFieldValidation: {} as Record<string, FieldValidation>,
  previewApproved: false,
};

export const useDocumentStore = create<DocumentState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setDocumentType: (type) =>
        set({ documentType: type }, false, 'setDocumentType'),

      setExtractedData: (data) =>
        set(
          { extractedData: data, editedData: data },
          false,
          'setExtractedData'
        ),

      setEditedData: (data) =>
        set({ editedData: data }, false, 'setEditedData'),

      updateField: (fieldName, value) =>
        set(
          (state) => ({
            editedData: {
              ...(state.editedData || {}),
              [fieldName]: value,
            },
          }),
          false,
          'updateField'
        ),

      setProcessing: (isProcessing, step = 'idle') =>
        set(
          { isProcessing, processingStep: step },
          false,
          'setProcessing'
        ),

      setError: (error) => set({ error }, false, 'setError'),

      setOCRResults: (results) =>
        set({ ocrResults: results }, false, 'setOCRResults'),

      setConfidence: (confidence) =>
        set({ confidence }, false, 'setConfidence'),

      // OCR Robusto 2025 - Quality Report
      setQualityReport: (report) =>
        set({ qualityReport: report }, false, 'setQualityReport'),

      // OCR Robusto 2025 - Validation Report
      setValidationReport: (report) => {
        if (report) {
          // Extract per-field confidence and validation for easy access
          const perFieldConfidence: Record<string, number> = {};
          const perFieldValidation: Record<string, FieldValidation> = {};

          report.field_validations.forEach((fv) => {
            perFieldConfidence[fv.field] = fv.confidence;
            perFieldValidation[fv.field] = fv;
          });

          set({
            validationReport: report,
            perFieldConfidence,
            perFieldValidation,
          }, false, 'setValidationReport');
        } else {
          set({
            validationReport: null,
            perFieldConfidence: {},
            perFieldValidation: {},
          }, false, 'setValidationReport');
        }
      },

      // Helper to get field confidence
      getFieldConfidence: (fieldName: string): number | undefined => {
        return get().perFieldConfidence[fieldName];
      },

      // Helper to get field validation
      getFieldValidation: (fieldName: string): FieldValidation | undefined => {
        return get().perFieldValidation[fieldName];
      },

      setPreviewApproved: (approved: boolean) =>
        set({ previewApproved: approved }, false, 'setPreviewApproved'),

      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'DocumentStore' }
  )
);
