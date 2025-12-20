/**
 * Notary Profile API endpoints
 * Connects to: /api/notary-profile/*
 */

import { apiClient } from '../client';
import type {
  NotaryProfileResponse,
  NotaryProfileUpdate,
  IncrementInstrumentResponse,
} from '../types/notary-profile-types';

export const notaryProfileApi = {
  /**
   * GET /api/notary-profile
   * Get the current notary profile
   */
  getProfile: async (): Promise<NotaryProfileResponse> => {
    const { data } = await apiClient.get<NotaryProfileResponse>(
      '/notary-profile'
    );
    return data;
  },

  /**
   * PUT /api/notary-profile
   * Update the notary profile
   */
  updateProfile: async (
    update: NotaryProfileUpdate
  ): Promise<NotaryProfileResponse> => {
    const { data } = await apiClient.put<NotaryProfileResponse>(
      '/notary-profile',
      update
    );
    return data;
  },

  /**
   * POST /api/notary-profile/increment-instrument
   * Increment the instrument number and get the new value
   */
  incrementInstrument: async (): Promise<IncrementInstrumentResponse> => {
    const { data } = await apiClient.post<IncrementInstrumentResponse>(
      '/notary-profile/increment-instrument'
    );
    return data;
  },
};
