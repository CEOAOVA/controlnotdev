/**
 * useDocuments Hook
 * Custom hook for document history management
 */

import { useState, useCallback } from 'react';
import { documentsApi } from '@/api/endpoints/documents';
import type {
  DocumentRecord,
  DocumentListRequest,
  DocumentListResponse,
  DocumentStatsResponse,
  EmailDocumentRequest,
} from '@/api/types/documents-types';

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [stats, setStats] = useState<DocumentStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch documents list
   */
  const fetchDocuments = useCallback(
    async (params?: DocumentListRequest): Promise<DocumentListResponse> => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await documentsApi.list(params);
        setDocuments(response.documents);
        return response;
      } catch (err: any) {
        const errorMessage = err.message || 'Error al cargar documentos';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Fetch document statistics
   */
  const fetchStats = useCallback(async (): Promise<DocumentStatsResponse> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await documentsApi.getStats();
      setStats(response);
      return response;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar estadísticas';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get single document by ID
   */
  const getDocument = useCallback(async (documentId: string): Promise<DocumentRecord> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await documentsApi.get(documentId);
      return response.document;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar documento';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Download a document
   */
  const downloadDocument = useCallback(async (documentId: string, filename: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Get the blob
      const blob = await documentsApi.download(documentId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      const errorMessage = err.message || 'Error al descargar documento';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get download URL for a document
   */
  const getDownloadUrl = useCallback(async (documentId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await documentsApi.getDownloadUrl(documentId);
      return response;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al obtener URL de descarga';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Send document via email
   */
  const emailDocument = useCallback(async (request: EmailDocumentRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await documentsApi.email(request);
      return response;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al enviar documento por email';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Delete a document
   */
  const deleteDocument = useCallback(
    async (documentId: string, deleteFile: boolean = false) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await documentsApi.delete({
          document_id: documentId,
          delete_file: deleteFile,
        });

        // Update local state
        setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));

        return response;
      } catch (err: any) {
        const errorMessage = err.message || 'Error al eliminar documento';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Bulk delete documents
   */
  const bulkDeleteDocuments = useCallback(
    async (documentIds: string[], deleteFiles: boolean = false) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await documentsApi.bulkDelete(documentIds, deleteFiles);

        // Update local state
        setDocuments((prev) => prev.filter((doc) => !documentIds.includes(doc.id)));

        return response;
      } catch (err: any) {
        const errorMessage = err.message || 'Error al eliminar documentos';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Export documents to CSV
   */
  const exportDocuments = useCallback(async (params?: DocumentListRequest) => {
    try {
      setIsLoading(true);
      setError(null);

      const blob = await documentsApi.export(params);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `documentos_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      const errorMessage = err.message || 'Error al exportar documentos';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    // State
    documents,
    stats,
    isLoading,
    error,

    // Methods
    fetchDocuments,
    fetchStats,
    getDocument,
    downloadDocument,
    getDownloadUrl,
    emailDocument,
    deleteDocument,
    bulkDeleteDocuments,
    exportDocuments,
  };
}
