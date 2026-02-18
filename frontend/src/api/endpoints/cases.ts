/**
 * Cases CRM API Endpoints
 * Full CRUD + workflow for cases, parties, checklist, tramites, timeline, catalogos
 */

import { apiClient } from '../client';
import type {
  Case,
  CaseWithClient,
  CaseDetail,
  CaseListResponse,
  CaseListParams,
  CaseCreateRequest,
  CaseUpdateRequest,
  CaseStatistics,
  CaseDashboard,
  TransitionResponse,
  CaseParty,
  PartyCreateRequest,
  ChecklistItem,
  ChecklistCreateRequest,
  Tramite,
  TramiteCreateRequest,
  CaseTimeline,
  CatalogoChecklist,
} from '../types/cases-types';

// === CASES ===

export const casesApi = {
  list: async (params?: CaseListParams): Promise<CaseListResponse> => {
    const response = await apiClient.get<CaseListResponse>('/cases', { params });
    return response.data;
  },

  get: async (id: string): Promise<CaseDetail> => {
    const response = await apiClient.get<CaseDetail>(`/cases/${id}`);
    return response.data;
  },

  create: async (data: CaseCreateRequest): Promise<CaseWithClient> => {
    const response = await apiClient.post<CaseWithClient>('/cases', data);
    return response.data;
  },

  update: async (id: string, data: CaseUpdateRequest): Promise<Case> => {
    const response = await apiClient.put<Case>(`/cases/${id}`, data);
    return response.data;
  },

  transition: async (id: string, status: string, notes?: string): Promise<Case> => {
    const response = await apiClient.post<Case>(`/cases/${id}/transition`, { status, notes });
    return response.data;
  },

  suspend: async (id: string, reason: string): Promise<Case> => {
    const response = await apiClient.post<Case>(`/cases/${id}/suspend`, { reason });
    return response.data;
  },

  resume: async (id: string): Promise<Case> => {
    const response = await apiClient.post<Case>(`/cases/${id}/resume`);
    return response.data;
  },

  getTransitions: async (id: string): Promise<TransitionResponse> => {
    const response = await apiClient.get<TransitionResponse>(`/cases/${id}/transitions`);
    return response.data;
  },

  getDocuments: async (id: string): Promise<{ documents: any[]; total: number }> => {
    const response = await apiClient.get(`/cases/${id}/documents`);
    return response.data;
  },

  getStatistics: async (): Promise<CaseStatistics> => {
    const response = await apiClient.get<CaseStatistics>('/cases/statistics');
    return response.data;
  },

  getDashboard: async (): Promise<CaseDashboard> => {
    const response = await apiClient.get<CaseDashboard>('/cases/dashboard');
    return response.data;
  },
};

// === PARTIES ===

export const partiesApi = {
  list: async (caseId: string): Promise<CaseParty[]> => {
    const response = await apiClient.get<CaseParty[]>(`/cases/${caseId}/parties`);
    return response.data;
  },

  create: async (caseId: string, data: PartyCreateRequest): Promise<CaseParty> => {
    const response = await apiClient.post<CaseParty>(`/cases/${caseId}/parties`, data);
    return response.data;
  },

  update: async (caseId: string, partyId: string, data: Record<string, any>): Promise<CaseParty> => {
    const response = await apiClient.put<CaseParty>(`/cases/${caseId}/parties/${partyId}`, data);
    return response.data;
  },

  remove: async (caseId: string, partyId: string): Promise<void> => {
    await apiClient.delete(`/cases/${caseId}/parties/${partyId}`);
  },
};

// === CHECKLIST ===

export const checklistApi = {
  list: async (caseId: string): Promise<ChecklistItem[]> => {
    const response = await apiClient.get<ChecklistItem[]>(`/cases/${caseId}/checklist`);
    return response.data;
  },

  initialize: async (caseId: string, documentType?: string): Promise<ChecklistItem[]> => {
    const response = await apiClient.post<ChecklistItem[]>(`/cases/${caseId}/checklist/initialize`, {
      document_type: documentType,
    });
    return response.data;
  },

  create: async (caseId: string, data: ChecklistCreateRequest): Promise<ChecklistItem> => {
    const response = await apiClient.post<ChecklistItem>(`/cases/${caseId}/checklist`, data);
    return response.data;
  },

  updateStatus: async (caseId: string, itemId: string, status: string, notas?: string): Promise<ChecklistItem> => {
    const response = await apiClient.put<ChecklistItem>(`/cases/${caseId}/checklist/${itemId}`, { status, notas });
    return response.data;
  },

  remove: async (caseId: string, itemId: string): Promise<void> => {
    await apiClient.delete(`/cases/${caseId}/checklist/${itemId}`);
  },
};

// === TRAMITES ===

export const tramitesApi = {
  list: async (caseId: string): Promise<Tramite[]> => {
    const response = await apiClient.get<Tramite[]>(`/cases/${caseId}/tramites`);
    return response.data;
  },

  create: async (caseId: string, data: TramiteCreateRequest): Promise<Tramite> => {
    const response = await apiClient.post<Tramite>(`/cases/${caseId}/tramites`, data);
    return response.data;
  },

  update: async (caseId: string, tramiteId: string, data: Record<string, any>): Promise<Tramite> => {
    const response = await apiClient.put<Tramite>(`/cases/${caseId}/tramites/${tramiteId}`, data);
    return response.data;
  },

  complete: async (caseId: string, tramiteId: string, resultado?: string, costo?: number): Promise<Tramite> => {
    const response = await apiClient.post<Tramite>(`/cases/${caseId}/tramites/${tramiteId}/complete`, { resultado, costo });
    return response.data;
  },

  remove: async (caseId: string, tramiteId: string): Promise<void> => {
    await apiClient.delete(`/cases/${caseId}/tramites/${tramiteId}`);
  },

  getOverdue: async (): Promise<Tramite[]> => {
    const response = await apiClient.get<Tramite[]>('/tramites/overdue');
    return response.data;
  },

  getUpcoming: async (days = 7): Promise<Tramite[]> => {
    const response = await apiClient.get<Tramite[]>('/tramites/upcoming', { params: { days } });
    return response.data;
  },
};

// === TIMELINE ===

export const timelineApi = {
  get: async (caseId: string, limit = 50, offset = 0): Promise<CaseTimeline> => {
    const response = await apiClient.get<CaseTimeline>(`/cases/${caseId}/timeline`, { params: { limit, offset } });
    return response.data;
  },

  addNote: async (caseId: string, note: string): Promise<{ message: string; id: string }> => {
    const response = await apiClient.post(`/cases/${caseId}/notes`, { note });
    return response.data;
  },
};

// === CATALOGOS ===

export const catalogosApi = {
  listTemplates: async (documentType?: string): Promise<CatalogoChecklist[]> => {
    const response = await apiClient.get<CatalogoChecklist[]>('/catalogos/checklist-templates', {
      params: documentType ? { document_type: documentType } : {},
    });
    return response.data;
  },

  createTemplate: async (data: {
    document_type: string;
    nombre: string;
    categoria: string;
    obligatorio?: boolean;
    orden?: number;
  }): Promise<CatalogoChecklist> => {
    const response = await apiClient.post<CatalogoChecklist>('/catalogos/checklist-templates', data);
    return response.data;
  },

  updateTemplate: async (id: string, data: Record<string, any>): Promise<CatalogoChecklist> => {
    const response = await apiClient.put<CatalogoChecklist>(`/catalogos/checklist-templates/${id}`, data);
    return response.data;
  },

  deleteTemplate: async (id: string): Promise<void> => {
    await apiClient.delete(`/catalogos/checklist-templates/${id}`);
  },
};
