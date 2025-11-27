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
 * Maneja errores globalmente
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login if auth fails
      console.error('Unauthorized');
    } else if (error.response?.status === 500) {
      console.error('Server error');
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
