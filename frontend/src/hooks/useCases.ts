/**
 * useCases Hook
 * Custom hook for cases/expedientes management
 */

import { useState, useCallback } from 'react';
import * as casesApi from '@/api/endpoints/cases';
import type {
  CaseBase,
  CaseDetail,
  CaseListRequest,
  CaseStatsResponse,
  CaseCreateRequest,
  CaseUpdateRequest,
} from '@/api/types';

export function useCases() {
  const [cases, setCases] = useState<CaseBase[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseDetail | null>(null);
  const [stats, setStats] = useState<CaseStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch cases list
  const fetchCases = useCallback(async (params?: CaseListRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await casesApi.listCases(params);
      setCases(response.cases);
      return response;
    } catch (err: any) {
      setError(err.message || 'Error al cargar casos');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch case by ID
  const fetchCaseById = useCallback(async (caseId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const caseDetail = await casesApi.getCaseById(caseId);
      setSelectedCase(caseDetail);
      return caseDetail;
    } catch (err: any) {
      setError(err.message || 'Error al cargar caso');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch case statistics
  const fetchStats = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const statsData = await casesApi.getCaseStats();
      setStats(statsData);
      return statsData;
    } catch (err: any) {
      setError(err.message || 'Error al cargar estadísticas');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create new case
  const createCase = useCallback(async (data: CaseCreateRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const newCase = await casesApi.createCase(data);
      setCases((prev) => [newCase, ...prev]);
      return newCase;
    } catch (err: any) {
      setError(err.message || 'Error al crear caso');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update case
  const updateCase = useCallback(
    async (caseId: string, data: CaseUpdateRequest) => {
      try {
        setIsLoading(true);
        setError(null);
        const updatedCase = await casesApi.updateCase(caseId, data);
        setCases((prev) =>
          prev.map((c) => (c.id === caseId ? updatedCase : c))
        );
        return updatedCase;
      } catch (err: any) {
        setError(err.message || 'Error al actualizar caso');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Delete case
  const deleteCase = useCallback(async (caseId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await casesApi.deleteCase(caseId);
      setCases((prev) => prev.filter((c) => c.id !== caseId));
    } catch (err: any) {
      setError(err.message || 'Error al eliminar caso');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Change case status
  const changeCaseStatus = useCallback(
    async (caseId: string, status: CaseBase['status']) => {
      try {
        setIsLoading(true);
        setError(null);
        const updatedCase = await casesApi.changeCaseStatus(caseId, status);
        setCases((prev) =>
          prev.map((c) => (c.id === caseId ? updatedCase : c))
        );
        return updatedCase;
      } catch (err: any) {
        setError(err.message || 'Error al cambiar estado del caso');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    cases,
    selectedCase,
    stats,
    isLoading,
    error,

    // Actions
    fetchCases,
    fetchCaseById,
    fetchStats,
    createCase,
    updateCase,
    deleteCase,
    changeCaseStatus,
    clearError,

    // Helpers
    setSelectedCase,
  };
}
