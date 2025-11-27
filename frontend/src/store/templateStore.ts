/**
 * Template Store - Manages selected template and placeholders
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { DocumentType } from './documentStore';

export interface TemplateInfo {
  id: string;
  name: string;
  type?: DocumentType;
  source: 'drive' | 'local' | 'uploaded';
  placeholders?: string[];
  uploadedFile?: File;
  createdAt?: string;
}

interface TemplateState {
  // Selected template
  selectedTemplate: TemplateInfo | null;

  // Available templates
  availableTemplates: TemplateInfo[];

  // Extracted placeholders from template
  placeholders: string[];

  // Detected document type from template
  detectedType: DocumentType | null;

  // Loading state
  isLoading: boolean;

  // Error
  error: string | null;

  // Actions
  setSelectedTemplate: (template: TemplateInfo) => void;
  setAvailableTemplates: (templates: TemplateInfo[]) => void;
  setPlaceholders: (placeholders: string[]) => void;
  setDetectedType: (type: DocumentType | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  uploadCustomTemplate: (file: File) => void;
  clearTemplate: () => void;
  reset: () => void;
}

const initialState = {
  selectedTemplate: null,
  availableTemplates: [],
  placeholders: [],
  detectedType: null,
  isLoading: false,
  error: null,
};

export const useTemplateStore = create<TemplateState>()(
  devtools(
    (set) => ({
      ...initialState,

      setSelectedTemplate: (template) =>
        set(
          {
            selectedTemplate: template,
            placeholders: template.placeholders || [],
            detectedType: template.type || null,
          },
          false,
          'setSelectedTemplate'
        ),

      setAvailableTemplates: (templates) =>
        set({ availableTemplates: templates }, false, 'setAvailableTemplates'),

      setPlaceholders: (placeholders) =>
        set({ placeholders }, false, 'setPlaceholders'),

      setDetectedType: (type) =>
        set({ detectedType: type }, false, 'setDetectedType'),

      setLoading: (isLoading) =>
        set({ isLoading }, false, 'setLoading'),

      setError: (error) =>
        set({ error }, false, 'setError'),

      uploadCustomTemplate: (file) =>
        set(
          {
            selectedTemplate: {
              id: `custom-${Date.now()}`,
              name: file.name,
              source: 'uploaded',
              uploadedFile: file,
            },
          },
          false,
          'uploadCustomTemplate'
        ),

      clearTemplate: () =>
        set(
          {
            selectedTemplate: null,
            placeholders: [],
            detectedType: null,
          },
          false,
          'clearTemplate'
        ),

      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'TemplateStore' }
  )
);
