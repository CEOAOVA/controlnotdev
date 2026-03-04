/**
 * ServiceStatus Component
 *
 * Displays real-time status of backend services:
 * - Google Vision API (OCR processing)
 * - Google Drive API (template storage)
 * - OpenAI/OpenRouter (AI extraction)
 * - Supabase (database & auth)
 *
 * Updates every 30 seconds or on mount
 */

import React, { useEffect, useState } from 'react';
import { StatusPillWithIcon, StatusVariant } from '@/components/shared/StatusPill';
import { Card } from '@/components/ui/card';
import { env } from '@/config/env';

interface Service {
  name: string;
  status: 'healthy' | 'degraded' | 'down' | 'unknown';
  message?: string;
}

interface ServiceStatusResponse {
  vision: Service;
  drive: Service;
  ai: Service;
  supabase: Service;
}

const getStatusVariant = (status: Service['status']): StatusVariant => {
  switch (status) {
    case 'healthy':
      return 'success';
    case 'degraded':
      return 'warning';
    case 'down':
      return 'error';
    default:
      return 'info';
  }
};

const getStatusLabel = (service: Service): string => {
  const baseLabel = service.name;

  if (service.status === 'degraded' && service.message) {
    return `${baseLabel} (${service.message})`;
  }

  return baseLabel;
};

export const ServiceStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatusResponse>({
    vision: { name: 'Google Vision API', status: 'unknown' },
    drive: { name: 'Google Drive', status: 'unknown' },
    ai: { name: 'OpenAI GPT-4', status: 'unknown' },
    supabase: { name: 'Supabase', status: 'unknown' },
  });

  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const checkServiceStatus = async () => {
    try {
      setIsLoading(true);

      const response = await fetch(`${env.apiUrl}/api/health`);
      const data = await response.json();

      // Map backend response to frontend ServiceStatusResponse
      // Backend returns: { status, version, services: { openrouter/openai, google_vision, google_drive, smtp } }
      const svcMap = data.services || {};

      const mapStatus = (key: string): Service['status'] => {
        const val = svcMap[key];
        if (val === 'ok') return 'healthy';
        if (val === 'not_configured') return 'degraded';
        if (val === 'error') return 'down';
        return 'unknown';
      };

      // Determine AI provider name
      const aiKey = svcMap.openrouter !== undefined ? 'openrouter' : 'openai';
      const aiName = aiKey === 'openrouter' ? 'OpenRouter AI' : 'OpenAI GPT-4';

      const mapped: ServiceStatusResponse = {
        vision: {
          name: 'Google Vision API',
          status: mapStatus('google_vision'),
          message: svcMap.google_vision === 'not_configured' ? 'No configurado' : undefined,
        },
        drive: {
          name: 'Google Drive',
          status: mapStatus('google_drive'),
          message: svcMap.google_drive === 'not_configured' ? 'No configurado' : undefined,
        },
        ai: {
          name: aiName,
          status: mapStatus(aiKey),
          message: svcMap[aiKey] === 'not_configured' ? 'No configurado' : undefined,
        },
        supabase: {
          name: 'Email SMTP',
          status: mapStatus('smtp'),
          message: svcMap.smtp === 'not_configured' ? 'No configurado' : undefined,
        },
      };

      setServices(mapped);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error checking service status:', error);

      setServices({
        vision: { name: 'Google Vision API', status: 'down' },
        drive: { name: 'Google Drive', status: 'down' },
        ai: { name: 'AI Provider', status: 'down' },
        supabase: { name: 'Email SMTP', status: 'down' },
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Check on mount
    checkServiceStatus();

    // Check every 30 seconds
    const interval = setInterval(checkServiceStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="p-4 bg-neutral-50 border-neutral-200">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-neutral-700">
          Estado de Servicios
        </h4>
        <button
          onClick={checkServiceStatus}
          disabled={isLoading}
          className="text-xs text-primary-500 hover:text-primary-600 font-medium transition-colors disabled:opacity-50"
          title="Actualizar estado"
        >
          {isLoading ? '⟳' : '🔄'}
        </button>
      </div>

      <div className="space-y-2">
        <StatusPillWithIcon
          status={getStatusVariant(services.vision.status)}
          label={getStatusLabel(services.vision)}
        />

        <StatusPillWithIcon
          status={getStatusVariant(services.drive.status)}
          label={getStatusLabel(services.drive)}
        />

        <StatusPillWithIcon
          status={getStatusVariant(services.ai.status)}
          label={getStatusLabel(services.ai)}
        />

        <StatusPillWithIcon
          status={getStatusVariant(services.supabase.status)}
          label={getStatusLabel(services.supabase)}
        />
      </div>

      {lastUpdate && (
        <p className="text-xs text-neutral-500 mt-3">
          Última actualización: {lastUpdate.toLocaleTimeString('es-MX')}
        </p>
      )}

      <div className="mt-4 pt-3 border-t border-neutral-200">
        <p className="text-xs text-neutral-600">
          💡 <strong>Sistema listo</strong> para procesar documentos notariales
        </p>
      </div>
    </Card>
  );
};

export default ServiceStatus;
