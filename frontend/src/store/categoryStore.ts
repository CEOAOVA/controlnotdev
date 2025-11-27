/**
 * Category Store - Manages uploaded files by category
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type CategoryName = 'Parte A' | 'Parte B' | 'Otros';

export interface UploadedFile {
  file: File;
  id: string; // unique identifier
  preview?: string; // preview URL for images
}

interface CategoryFiles {
  [category: string]: UploadedFile[];
}

interface CategoryState {
  // Files organized by category
  files: CategoryFiles;

  // Available categories for current document type
  availableCategories: {
    name: CategoryName;
    description: string;
    icon?: string;
  }[];

  // Actions
  addFiles: (category: CategoryName, files: File[]) => void;
  removeFile: (category: CategoryName, fileId: string) => void;
  clearCategory: (category: CategoryName) => void;
  clearAll: () => void;
  getFilesByCategory: (category: CategoryName) => UploadedFile[];
  getTotalFiles: () => number;
  setAvailableCategories: (
    categories: CategoryState['availableCategories']
  ) => void;
}

const initialState = {
  files: {},
  availableCategories: [],
};

export const useCategoryStore = create<CategoryState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      addFiles: (category, newFiles) =>
        set(
          (state) => {
            // Generate unique IDs and preview URLs
            const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
              file,
              id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              preview: file.type.startsWith('image/')
                ? URL.createObjectURL(file)
                : undefined,
            }));

            return {
              files: {
                ...state.files,
                [category]: [...(state.files[category] || []), ...uploadedFiles],
              },
            };
          },
          false,
          'addFiles'
        ),

      removeFile: (category, fileId) =>
        set(
          (state) => {
            const categoryFiles = state.files[category] || [];
            const fileToRemove = categoryFiles.find((f) => f.id === fileId);

            // Revoke preview URL if exists
            if (fileToRemove?.preview) {
              URL.revokeObjectURL(fileToRemove.preview);
            }

            return {
              files: {
                ...state.files,
                [category]: categoryFiles.filter((f) => f.id !== fileId),
              },
            };
          },
          false,
          'removeFile'
        ),

      clearCategory: (category) =>
        set(
          (state) => {
            // Revoke all preview URLs
            const categoryFiles = state.files[category] || [];
            categoryFiles.forEach((f) => {
              if (f.preview) URL.revokeObjectURL(f.preview);
            });

            return {
              files: {
                ...state.files,
                [category]: [],
              },
            };
          },
          false,
          'clearCategory'
        ),

      clearAll: () =>
        set(
          (state) => {
            // Revoke all preview URLs
            Object.values(state.files).forEach((categoryFiles) => {
              categoryFiles.forEach((f) => {
                if (f.preview) URL.revokeObjectURL(f.preview);
              });
            });

            return { files: {} };
          },
          false,
          'clearAll'
        ),

      getFilesByCategory: (category) => {
        return get().files[category] || [];
      },

      getTotalFiles: () => {
        const { files } = get();
        return Object.values(files).reduce(
          (total, categoryFiles) => total + categoryFiles.length,
          0
        );
      },

      setAvailableCategories: (categories) =>
        set({ availableCategories: categories }, false, 'setAvailableCategories'),
    }),
    { name: 'CategoryStore' }
  )
);
