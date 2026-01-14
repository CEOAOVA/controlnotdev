/**
 * useCategories - Hook for managing document categories
 * Handles: Loading categories for document type, validating uploads
 */

import { useQuery } from '@tanstack/react-query';
import { modelsApi } from '@/api/endpoints';
import { useCategoryStore, useDocumentStore } from '@/store';
import type { CategoryName } from '@/store';

export function useCategories() {
  const { documentType } = useDocumentStore();
  const { setAvailableCategories, files, addFiles, removeFile, clearCategory } =
    useCategoryStore();

  // Query to load categories for current document type
  const categoriesQuery = useQuery({
    queryKey: ['categories', documentType],
    queryFn: async () => {
      if (!documentType) {
        return null;
      }

      const response = await modelsApi.getCategories(documentType);

      // Transform to category format (including required field)
      const categories = response.categories.map((cat) => ({
        name: cat.name as CategoryName,
        description: cat.description,
        icon: cat.icon,
        required: cat.required !== false, // Default to true if not specified
      }));

      setAvailableCategories(categories);
      return categories;
    },
    enabled: !!documentType, // Only run if document type is set
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Helper to validate file type
  const isValidFileType = (file: File): boolean => {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    return validTypes.includes(file.type);
  };

  // Helper to validate file size (max 10MB)
  const isValidFileSize = (file: File, maxSizeMB: number = 10): boolean => {
    const maxBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxBytes;
  };

  // Helper to add files with validation
  const addFilesWithValidation = (category: CategoryName, newFiles: File[]) => {
    const validFiles: File[] = [];
    const errors: string[] = [];

    newFiles.forEach((file) => {
      if (!isValidFileType(file)) {
        errors.push(`${file.name}: Tipo de archivo no válido. Solo JPG, PNG, PDF`);
      } else if (!isValidFileSize(file)) {
        errors.push(`${file.name}: Archivo demasiado grande (max 10MB)`);
      } else {
        validFiles.push(file);
      }
    });

    if (validFiles.length > 0) {
      addFiles(category, validFiles);
    }

    return { validFiles, errors };
  };

  // Helper to get file count by category
  const getFilesCount = (category: CategoryName): number => {
    return files[category]?.length || 0;
  };

  // Helper to check if category has files
  const hasFiles = (category: CategoryName): boolean => {
    return getFilesCount(category) > 0;
  };

  // Helper to check if all REQUIRED categories have files
  // Categories with required=false can be skipped
  const areAllCategoriesPopulated = (): boolean => {
    const categories = categoriesQuery.data || [];
    // Only check categories where required !== false
    return categories
      .filter((cat) => cat.required !== false)
      .every((cat) => hasFiles(cat.name));
  };

  // Helper to get total files across all categories
  const getTotalFilesCount = (): number => {
    return Object.values(files).reduce(
      (total, categoryFiles) => total + categoryFiles.length,
      0
    );
  };

  return {
    // Query
    categoriesQuery,

    // Helpers
    addFilesWithValidation,
    isValidFileType,
    isValidFileSize,
    getFilesCount,
    hasFiles,
    areAllCategoriesPopulated,
    getTotalFilesCount,

    // Store actions (pass-through)
    removeFile,
    clearCategory,

    // Loading state
    isLoadingCategories: categoriesQuery.isLoading,

    // Data
    categories: categoriesQuery.data || [],
    files,
  };
}
