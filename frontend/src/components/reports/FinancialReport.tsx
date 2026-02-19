/**
 * FinancialReport
 * Financial summary with payment breakdowns
 */

import { Card } from '@/components/ui/card';
import type { FinancialSummary } from '@/api/endpoints/reports';

interface FinancialReportProps {
  data: FinancialSummary | null;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount);
}

const TIPO_LABELS: Record<string, string> = {
  honorarios: 'Honorarios',
  impuestos: 'Impuestos',
  derechos: 'Derechos',
  gastos: 'Gastos',
  otro: 'Otro',
};

const METODO_LABELS: Record<string, string> = {
  efectivo: 'Efectivo',
  transferencia: 'Transferencia',
  cheque: 'Cheque',
  tarjeta: 'Tarjeta',
  otro: 'Otro',
};

export function FinancialReport({ data }: FinancialReportProps) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-lg font-semibold">Finanzas</h3>
        <span className="text-sm text-neutral-500">{data.count} pagos</span>
      </div>

      {/* Grand Total */}
      <Card className="p-6 text-center bg-primary-50 border-primary-200">
        <p className="text-sm text-primary-600 uppercase font-medium">Total Recaudado</p>
        <p className="text-3xl font-bold text-primary-700">{formatCurrency(data.total)}</p>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* By Type */}
        <Card className="p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Por Tipo de Pago</h4>
          <div className="space-y-2">
            {Object.entries(data.by_tipo).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-neutral-600">{TIPO_LABELS[key] || key}</span>
                <span className="text-sm font-medium">{formatCurrency(value)}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* By Method */}
        <Card className="p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Por Metodo de Pago</h4>
          <div className="space-y-2">
            {Object.entries(data.by_metodo).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-neutral-600">{METODO_LABELS[key] || key}</span>
                <span className="text-sm font-medium">{formatCurrency(value)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
