import axios, { AxiosError } from 'axios';
import { env } from '@/config/env';
import { API_TIMEOUT } from '@/config/constants';

/**
 * Axios client configurado para el backend FastAPI
 * 
 * Features:
 * - Base URL desde env
 * - Timeout configurable
 * - Interceptores para requests/responses
 * - Error handling global
 */
export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * Agrega headers adicionales si son necesarios
 */
apiClient.interceptors.request.use(
  (config) => {
    // Agregar auth token si existe en el futuro
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
