/**
 * History Page
 * View and manage document generation history
 */

import { useState, useEffect, useRef } from 'react';
import { FileText, AlertCircle, Download } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { DocumentTable, type DocumentRecord } from '@/components/history/DocumentTable';
import { Filters, type DocumentFilters } from '@/components/history/Filters';
import { Pagination } from '@/components/history/Pagination';
import { useDocuments, useToast } from '@/hooks';
import type { DocumentListRequest } from '@/api/types/documents-types';

export function History() {
  const {
    fetchDocuments,
    downloadDocument,
    emailDocument,
    exportDocuments,
    isLoading,
    error,
  } = useDocuments();
  const toast = useToast();

  // Local state for display
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Filters state
  const [filters, setFilters] = useState<DocumentFilters>({
    search: '',
    type: 'all',
    status: 'all',
    dateFrom: '',
    dateTo: '',
  });

  // Ref to track if we're already loading (prevents duplicate calls)
  const isLoadingRef = useRef(false);
  // Ref to track previous filters for comparison
  const prevFiltersRef = useRef<DocumentFilters>(filters);

  // Load documents from API - single unified function
  const loadDocuments = async (page: number, size: number, currentFilters: DocumentFilters) => {
    // Prevent duplicate calls
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;

    try {
      const params: DocumentListRequest = {
        page,
        per_page: size,
        sort_by: 'created_at',
        sort_order: 'desc',
      };

      // Apply filters
      if (currentFilters.search) {
        params.search = currentFilters.search;
      }
      if (currentFilters.type !== 'all') {
        params.type = currentFilters.type;
      }
      if (currentFilters.status !== 'all') {
        params.status = currentFilters.status;
      }
      if (currentFilters.dateFrom) {
        params.date_from = currentFilters.dateFrom;
      }
      if (currentFilters.dateTo) {
        params.date_to = currentFilters.dateTo;
      }

      const response = await fetchDocuments(params);

      // Convert API response to display format
      // Backend returns: nombre_documento, tipo_documento, estado
      // Frontend expects: name, type, status
      const displayDocs: DocumentRecord[] = response.documents.map((doc: any) => ({
        id: doc.id,
        name: doc.nombre_documento || doc.name || 'Sin nombre',
        type: doc.tipo_documento || doc.type || 'otros',
        status: doc.estado || doc.status || 'completed',
        createdAt: doc.created_at,
        updatedAt: doc.updated_at,
        createdBy: doc.created_by,
        fileUrl: doc.file_url || doc.storage_path,
      }));

      setDocuments(displayDocs);
      setTotalItems(response.total);
      setTotalPages(response.total_pages);
    } catch (err: any) {
      console.error('Error loading documents:', err);
      // Set empty state on error to avoid showing stale data
      setDocuments([]);
      setTotalItems(0);
      setTotalPages(0);
    } finally {
      isLoadingRef.current = false;
      setIsInitialLoad(false);
    }
  };

  // Single useEffect for initial load only
  useEffect(() => {
    loadDocuments(currentPage, pageSize, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  // Effect for page changes (not initial load)
  useEffect(() => {
    if (isInitialLoad) return;
    loadDocuments(currentPage, pageSize, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, pageSize]);

  // Effect for filter changes - reset to page 1
  useEffect(() => {
    // Skip initial render
    if (isInitialLoad) return;

    // Check if filters actually changed
    const filtersChanged = JSON.stringify(prevFiltersRef.current) !== JSON.stringify(filters);
    if (!filtersChanged) return;

    prevFiltersRef.current = filters;

    // Reset to page 1 and load
    if (currentPage === 1) {
      loadDocuments(1, pageSize, filters);
    } else {
      setCurrentPage(1); // This will trigger the page change effect
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // Handlers
  const handleFiltersChange = (newFilters: DocumentFilters) => {
    setFilters(newFilters);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1);
  };

  const handleView = (doc: DocumentRecord) => {
    // TODO: Implement view details modal or navigation
    console.log('View document:', doc);
    toast.error('Funcionalidad de vista de detalles en desarrollo');
  };

  const handleDownload = async (doc: DocumentRecord) => {
    try {
      await downloadDocument(doc.id, `${doc.name}.pdf`);
      toast.success(`Documento "${doc.name}" descargado`);
    } catch (err: any) {
      toast.error(`Error al descargar: ${err.message}`);
    }
  };

  const handleEmail = async (doc: DocumentRecord) => {
    // TODO: Implement email dialog with form
    const email = prompt('Ingresa el email del destinatario:');
    if (!email) return;

    try {
      await emailDocument({
        document_id: doc.id,
        to_email: email,
        subject: `Documento: ${doc.name}`,
      });
      toast.success('Documento enviado exitosamente');
    } catch (err: any) {
      toast.error(`Error al enviar: ${err.message}`);
    }
  };

  const handleExportAll = async () => {
    try {
      const params: DocumentListRequest = {
        sort_by: 'created_at',
        sort_order: 'desc',
      };

      // Apply current filters to export
      if (filters.search) params.search = filters.search;
      if (filters.type !== 'all') params.type = filters.type;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.dateFrom) params.date_from = filters.dateFrom;
      if (filters.dateTo) params.date_to = filters.dateTo;

      await exportDocuments(params);
      toast.success('Documentos exportados exitosamente');
    } catch (err: any) {
      toast.error(`Error al exportar: ${err.message}`);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900">Historial</h1>
            <p className="text-neutral-600 mt-1">
              Consulta y gestiona todos los documentos generados
            </p>
          </div>
          <Button
            variant="outline"
            className="gap-2"
            onClick={handleExportAll}
            disabled={isLoading || documents.length === 0}
          >
            <Download className="w-4 h-4" />
            Exportar Todo
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Filters */}
        <Filters onFiltersChange={handleFiltersChange} isLoading={isLoading} />

        {/* Document Table */}
        <DocumentTable
          documents={documents}
          onView={handleView}
          onDownload={handleDownload}
          onEmail={handleEmail}
          isLoading={isLoading}
        />

        {/* Pagination */}
        {!isLoading && documents.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            pageSize={pageSize}
            totalItems={totalItems}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            isLoading={isLoading}
          />
        )}

        {/* Empty State with Icon (when no results after filtering) */}
        {!isLoading && documents.length === 0 && totalItems === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-neutral-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">
              No se encontraron documentos
            </h3>
            <p className="text-neutral-600 mt-2">
              {filters.search || filters.type !== 'all' || filters.status !== 'all'
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Los documentos generados aparecerán aquí'}
            </p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
