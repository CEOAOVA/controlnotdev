/**
 * Health API types
 * Match backend schemas from: backend/app/schemas/response_schemas.py
 */

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  services: Record<string, 'ok' | 'not_configured' | 'error'>;
}

export interface ServicesStatusResponse {
  services: {
    ai_provider: {
      name: string;
      model: string;
      configured: boolean;
    };
    ocr: {
      provider: string;
      max_concurrent: number;
    };
    storage: {
      templates_dir: string | null;
      output_dir: string | null;
    };
    email: {
      smtp_server: string | null;
      smtp_port: number | null;
    };
  };
  environment: string;
}
