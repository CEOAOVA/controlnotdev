/**
 * CasesReport
 * Shows cases breakdown by status, type, and priority
 */

import { Card } from '@/components/ui/card';
import type { CasesSummary } from '@/api/endpoints/reports';

interface CasesReportProps {
  data: CasesSummary | null;
}

function BreakdownTable({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);

  return (
    <Card className="p-4">
      <h4 className="text-sm font-semibold text-neutral-700 mb-3">{title}</h4>
      <div className="space-y-2">
        {entries.map(([key, value]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm text-neutral-600 capitalize">{key.replace(/_/g, ' ')}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-neutral-200 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full"
                  style={{ width: `${total > 0 ? (value / total) * 100 : 0}%` }}
                />
              </div>
              <span className="text-sm font-medium w-8 text-right">{value}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function CasesReport({ data }: CasesReportProps) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-lg font-semibold">Expedientes</h3>
        <span className="text-sm text-neutral-500">Total: {data.total}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <BreakdownTable title="Por Estado" data={data.by_status} />
        <BreakdownTable title="Por Tipo" data={data.by_type} />
        <BreakdownTable title="Por Prioridad" data={data.by_priority} />
      </div>
    </div>
  );
}
