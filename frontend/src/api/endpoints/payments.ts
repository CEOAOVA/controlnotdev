/**
 * Payments API Endpoints
 * CRUD for case payments
 */

import { apiClient } from '../client';
import type {
  CasePayment,
  PaymentListResponse,
  PaymentCreateRequest,
  PaymentUpdateRequest,
} from '../types/payments-types';

export const paymentsApi = {
  list: async (caseId: string, limit = 50, offset = 0): Promise<PaymentListResponse> => {
    const response = await apiClient.get<PaymentListResponse>(
      `/cases/${caseId}/payments`,
      { params: { limit, offset } }
    );
    return response.data;
  },

  create: async (caseId: string, data: PaymentCreateRequest): Promise<CasePayment> => {
    const response = await apiClient.post(`/cases/${caseId}/payments`, data);
    return response.data.payment;
  },

  update: async (caseId: string, paymentId: string, data: PaymentUpdateRequest): Promise<CasePayment> => {
    const response = await apiClient.patch(`/cases/${caseId}/payments/${paymentId}`, data);
    return response.data.payment;
  },

  remove: async (caseId: string, paymentId: string): Promise<void> => {
    await apiClient.delete(`/cases/${caseId}/payments/${paymentId}`);
  },
};
