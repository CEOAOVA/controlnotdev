/**
 * Document Store - Manages extracted and edited document data
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type DocumentType =
  | 'compraventa'
  | 'donacion'
  | 'testamento'
  | 'poder'
  | 'sociedad';

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

  // Confidence scores
  confidence: number | null;

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
  previewApproved: false,
};

export const useDocumentStore = create<DocumentState>()(
  devtools(
    (set) => ({
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

      setPreviewApproved: (approved) =>
        set({ previewApproved: approved }, false, 'setPreviewApproved'),

      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'DocumentStore' }
  )
);
