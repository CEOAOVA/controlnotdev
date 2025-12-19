import axios, { AxiosError } from 'axios';
import { env } from '@/config/env';
import { API_TIMEOUT } from '@/config/constants';
import { supabase } from '@/lib/supabase';

/**
 * Axios client configurado para el backend FastAPI
 *
 * Features:
 * - Base URL desde env + /api prefix
 * - Timeout configurable
 * - Interceptores para requests/responses
 * - Error handling global
 */
export const apiClient = axios.create({
  baseURL: env.apiUrl + '/api',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * Agrega Authorization header con token de Supabase
 */
apiClient.interceptors.request.use(
  async (config) => {
    // Obtener token de sesión de Supabase
    const { data: { session } } = await supabase.auth.getSession();

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * Maneja errores globalmente con logging detallado
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    // Log detailed error information for debugging
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      statusText: error.response?.statusText,
      detail: error.response?.data?.detail || error.response?.data?.message,
      timeout: error.code === 'ECONNABORTED',
    };

    console.error('[API Error]', errorInfo);

    // Handle specific error cases
    if (error.response?.status === 401) {
      console.error('[Auth] Session expired or unauthorized');
      // Could trigger logout or redirect here
    } else if (error.response?.status === 422) {
      console.error('[Validation] Request validation failed:', error.response?.data);
    } else if (error.response?.status === 500) {
      console.error('[Server] Internal server error');
    } else if (error.code === 'ECONNABORTED') {
      console.error('[Timeout] Request timed out after', error.config?.timeout, 'ms');
    } else if (!error.response) {
      console.error('[Network] No response from server - check if backend is running');
    }

    return Promise.reject(error);
  }
);

/**
 * Helper para convertir AxiosError a mensaje legible
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message;
  }
  return error instanceof Error ? error.message : 'Error desconocido';
}
