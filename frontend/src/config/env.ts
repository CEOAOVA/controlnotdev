/**
 * Environment configuration
 * Centraliza todas las variables de entorno
 */

export const env = {
  // API
  apiUrl: (() => {
    const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    // Force HTTPS for non-localhost URLs (production safety net)
    if (!url.includes('localhost') && url.startsWith('http://')) {
      return url.replace('http://', 'https://');
    }
    return url;
  })(),
  
  // App
  appName: import.meta.env.VITE_APP_NAME || 'ControlNot v2',
  appVersion: import.meta.env.VITE_APP_VERSION || '2.0.0',
  environment: import.meta.env.VITE_ENV || 'development',
  
  // Features
  enableDrive: import.meta.env.VITE_ENABLE_DRIVE === 'true',
  enableEmail: import.meta.env.VITE_ENABLE_EMAIL === 'true',
  
  // Helpers
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;
