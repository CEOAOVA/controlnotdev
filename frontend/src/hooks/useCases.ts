/**
 * useCases Hook
 * Custom hook for CRM cases/expedientes management
 */

import { useState, useCallback } from 'react';
import { casesApi } from '@/api/endpoints/cases';
import type {
  Case,
  CaseDetail,
  CaseListParams,
  CaseCreateRequest,
  CaseUpdateRequest,
  CaseStatistics,
  CaseDashboard,
} from '@/api/types/cases-types';

export function useCases() {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseDetail | null>(null);
  const [statistics, setStatistics] = useState<CaseStatistics | null>(null);
  const [dashboard, setDashboard] = useState<CaseDashboard | null>(null);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCases = useCallback(async (params?: CaseListParams) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await casesApi.list(params);
      setCases(response.cases);
      setTotalItems(response.total);
      setCurrentPage(response.page);
      setPageSize(response.page_size);
      return response;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al cargar expedientes';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchCaseById = useCallback(async (caseId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const caseDetail = await casesApi.get(caseId);
      setSelectedCase(caseDetail);
      return caseDetail;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al cargar expediente';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createCase = useCallback(async (data: CaseCreateRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const newCase = await casesApi.create(data);
      return newCase;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al crear expediente';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateCase = useCallback(async (caseId: string, data: CaseUpdateRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const updated = await casesApi.update(caseId, data);
      setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
      return updated;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al actualizar expediente';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const transitionCase = useCallback(async (caseId: string, status: string, notes?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const updated = await casesApi.transition(caseId, status, notes);
      setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
      return updated;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error en transicion';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const suspendCase = useCallback(async (caseId: string, reason: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const updated = await casesApi.suspend(caseId, reason);
      setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
      return updated;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al suspender expediente';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resumeCase = useCallback(async (caseId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const updated = await casesApi.resume(caseId);
      setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
      return updated;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al reanudar expediente';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchStatistics = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const stats = await casesApi.getStatistics();
      setStatistics(stats);
      return stats;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al cargar estadisticas';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchDashboard = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await casesApi.getDashboard();
      setDashboard(data);
      return data;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error al cargar dashboard';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    cases,
    selectedCase,
    statistics,
    dashboard,
    totalItems,
    currentPage,
    pageSize,
    isLoading,
    error,

    fetchCases,
    fetchCaseById,
    createCase,
    updateCase,
    transitionCase,
    suspendCase,
    resumeCase,
    fetchStatistics,
    fetchDashboard,
    clearError,

    setSelectedCase,
  };
}
