/**
 * TramitesReport
 * Tramites semaforo and expiration summary
 */

import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { TramitesSummary } from '@/api/endpoints/reports';

interface TramitesReportProps {
  data: TramitesSummary | null;
}

const SEMAFORO_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  verde: { bg: 'bg-green-100', text: 'text-green-700', label: 'Al dia' },
  amarillo: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Por vencer' },
  rojo: { bg: 'bg-red-100', text: 'text-red-700', label: 'Vencido' },
  gris: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Sin fecha' },
};

export function TramitesReport({ data }: TramitesReportProps) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-lg font-semibold">Tramites</h3>
        <span className="text-sm text-neutral-500">Total: {data.total}</span>
        {data.vencidos > 0 && (
          <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded-full">
            {data.vencidos} vencidos
          </span>
        )}
      </div>

      {/* Semaforo Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(SEMAFORO_COLORS).map(([key, style]) => {
          const count = data.by_semaforo[key] || 0;
          return (
            <Card key={key} className={cn('p-4 text-center', style.bg)}>
              <p className={cn('text-2xl font-bold', style.text)}>{count}</p>
              <p className={cn('text-xs font-medium', style.text)}>{style.label}</p>
            </Card>
          );
        })}
      </div>

      {/* By Status */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold text-neutral-700 mb-3">Por Estado</h4>
        <div className="space-y-2">
          {Object.entries(data.by_status).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm text-neutral-600 capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="text-sm font-medium">{value}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
