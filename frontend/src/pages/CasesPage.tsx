/**
 * CasesPage
 * List of expedientes with filters, table, pagination, and create dialog
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Plus, AlertCircle } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CaseFilters, type CaseFiltersState } from '@/components/cases/CaseFilters';
import { CaseTable } from '@/components/cases/CaseTable';
import { CaseCreateDialog } from '@/components/cases/CaseCreateDialog';
import { Pagination } from '@/components/history/Pagination';
import { useCases } from '@/hooks';
import type { CaseListParams, CaseCreateRequest, CaseStatus, CasePriority } from '@/api/types/cases-types';
import type { DocumentType } from '@/types';

export function CasesPage() {
  const navigate = useNavigate();
  const { cases, totalItems, isLoading, error, fetchCases, createCase } = useCases();

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const [filters, setFilters] = useState<CaseFiltersState>({
    search: '',
    status: 'all',
    document_type: 'all',
    priority: 'all',
  });

  const isLoadingRef = useRef(false);
  const prevFiltersRef = useRef<CaseFiltersState>(filters);

  const totalPages = Math.ceil(totalItems / pageSize);

  const loadCases = useCallback(async (page: number, size: number, currentFilters: CaseFiltersState) => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;

    try {
      const params: CaseListParams = {
        page,
        page_size: size,
      };

      if (currentFilters.search) params.search = currentFilters.search;
      if (currentFilters.status !== 'all') params.status = currentFilters.status as CaseStatus;
      if (currentFilters.document_type !== 'all') params.document_type = currentFilters.document_type as DocumentType;
      if (currentFilters.priority !== 'all') params.priority = currentFilters.priority as CasePriority;

      await fetchCases(params);
    } catch (err) {
      console.error('Error loading cases:', err);
    } finally {
      isLoadingRef.current = false;
      setIsInitialLoad(false);
    }
  }, [fetchCases]);

  // Initial load
  useEffect(() => {
    loadCases(currentPage, pageSize, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Page changes
  useEffect(() => {
    if (isInitialLoad) return;
    loadCases(currentPage, pageSize, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, pageSize]);

  // Filter changes - reset to page 1
  useEffect(() => {
    if (isInitialLoad) return;
    const filtersChanged = JSON.stringify(prevFiltersRef.current) !== JSON.stringify(filters);
    if (!filtersChanged) return;
    prevFiltersRef.current = filters;

    if (currentPage === 1) {
      loadCases(1, pageSize, filters);
    } else {
      setCurrentPage(1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const handleFiltersChange = useCallback((newFilters: CaseFiltersState) => {
    setFilters(newFilters);
  }, []);

  const handleCreateCase = async (data: CaseCreateRequest) => {
    const newCase = await createCase(data);
    navigate(`/cases/${newCase.id}`);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900">Expedientes</h1>
            <p className="text-neutral-600 mt-1">
              Gestiona todos los expedientes de la notaria
            </p>
          </div>
          <Button className="gap-2 w-full sm:w-auto" onClick={() => setShowCreateDialog(true)}>
            <Plus className="w-4 h-4" />
            Nuevo Expediente
          </Button>
        </div>

        {/* Error */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Filters */}
        <CaseFilters onFiltersChange={handleFiltersChange} isLoading={isLoading} />

        {/* Table */}
        <CaseTable cases={cases} isLoading={isLoading} />

        {/* Pagination */}
        {!isLoading && cases.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            pageSize={pageSize}
            totalItems={totalItems}
            onPageChange={setCurrentPage}
            onPageSizeChange={(size) => { setPageSize(size); setCurrentPage(1); }}
            isLoading={isLoading}
          />
        )}

        {/* Empty state */}
        {!isLoading && cases.length === 0 && totalItems === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Briefcase className="w-8 h-8 text-neutral-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">No se encontraron expedientes</h3>
            <p className="text-neutral-600 mt-2">
              {filters.search || filters.status !== 'all' || filters.document_type !== 'all' || filters.priority !== 'all'
                ? 'Intenta ajustar los filtros de busqueda'
                : 'Los expedientes creados apareceran aqui'}
            </p>
          </div>
        )}
      </div>

      {/* Create Dialog */}
      <CaseCreateDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSubmit={handleCreateCase}
      />
    </MainLayout>
  );
}
