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

export interface WhatsAppSummary {
  messages: {
    total: number;
    by_sender_type: Record<string, number>;
    by_message_type: Record<string, number>;
    by_status: Record<string, number>;
    failed_count: number;
  };
  conversations: {
    total: number;
    by_status: Record<string, number>;
    total_unread: number;
  };
  extractions: {
    total: number;
    by_document_type: Record<string, number>;
    by_status: Record<string, number>;
    avg_confidence: number;
  };
  commands: {
    total: number;
    top_commands: Record<string, number>;
    by_staff: Record<string, number>;
  };
}

export interface TemplatesSummaryItem {
  id: string;
  nombre: string;
  tipo_documento: string;
  total_placeholders: number;
  documents_generated: number;
  last_used_at: string | null;
  created_at: string;
}

export interface TemplatesSummary {
  templates: {
    total: number;
    by_document_type: Record<string, number>;
    list: TemplatesSummaryItem[];
  };
  documents: {
    total_generated: number;
    by_status: Record<string, number>;
    avg_confidence: number;
  };
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

  whatsappSummary: async (dateFrom?: string, dateTo?: string): Promise<WhatsAppSummary> => {
    const response = await apiClient.get<WhatsAppSummary>('/reports/whatsapp-summary', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },

  templatesSummary: async (): Promise<TemplatesSummary> => {
    const response = await apiClient.get<TemplatesSummary>('/reports/templates-summary');
    return response.data;
  },
};
