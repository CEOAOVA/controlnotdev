/**
 * Reports API Endpoints
 * Analytics and summary reports
 */

import { apiClient } from '../client';

export interface CasesSummary {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface TramitesSummary {
  total: number;
  vencidos: number;
  by_semaforo: Record<string, number>;
  by_status: Record<string, number>;
}

export interface FinancialSummary {
  total: number;
  count: number;
  by_tipo: Record<string, number>;
  by_metodo: Record<string, number>;
  top_cases: Record<string, number>;
}

export interface ProductivitySummary {
  total_cases: number;
  cerrados: number;
  abiertos: number;
  promedio_dias_cierre: number;
  tasa_cierre: number;
}

export const reportsApi = {
  casesSummary: async (dateFrom?: string, dateTo?: string): Promise<CasesSummary> => {
    const response = await apiClient.get<CasesSummary>('/reports/cases-summary', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },

  tramitesSummary: async (): Promise<TramitesSummary> => {
    const response = await apiClient.get<TramitesSummary>('/reports/tramites-summary');
    return response.data;
  },

  financialSummary: async (dateFrom?: string, dateTo?: string): Promise<FinancialSummary> => {
    const response = await apiClient.get<FinancialSummary>('/reports/financial-summary', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },

  productivity: async (dateFrom?: string, dateTo?: string): Promise<ProductivitySummary> => {
    const response = await apiClient.get<ProductivitySummary>('/reports/productivity', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },
};
