/**
 * UIF/PLD API Endpoints
 * Vulnerable operations management
 */

import { apiClient } from '../client';
import type {
  UIFOperation,
  UIFListResponse,
  UIFCheckResponse,
} from '../types/uif-types';

export const uifApi = {
  list: async (params?: {
    status?: string;
    nivel_riesgo?: string;
    limit?: number;
    offset?: number;
  }): Promise<UIFListResponse> => {
    const response = await apiClient.get<UIFListResponse>('/uif', { params });
    return response.data;
  },

  check: async (caseId: string): Promise<UIFCheckResponse> => {
    const response = await apiClient.get<UIFCheckResponse>(`/uif/check/${caseId}`);
    return response.data;
  },

  flag: async (data: {
    case_id: string;
    tipo_operacion: string;
    monto_operacion: number;
    notas?: string;
  }): Promise<UIFOperation> => {
    const response = await apiClient.post('/uif/flag', data);
    return response.data.operation;
  },

  update: async (operationId: string, data: {
    status?: string;
    numero_aviso?: string;
    fecha_aviso?: string;
    notas?: string;
  }): Promise<UIFOperation> => {
    const response = await apiClient.patch(`/uif/${operationId}`, data);
    return response.data.operation;
  },

  evaluate: async (tipo_operacion: string, monto: number): Promise<{
    es_vulnerable: boolean;
    nivel_riesgo: string;
    umbral_aplicado: number;
    requiere_aviso: boolean;
  }> => {
    const response = await apiClient.get('/uif/evaluate', {
      params: { tipo_operacion, monto },
    });
    return response.data;
  },
};
