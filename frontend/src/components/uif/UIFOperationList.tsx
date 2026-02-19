/**
 * UIFOperationList
 * Table of vulnerable operations with status management
 */

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { UIFOperation } from '@/api/types/uif-types';
import {
  UIF_RIESGO_LABELS,
  UIF_RIESGO_COLORS,
  UIF_STATUS_LABELS,
} from '@/api/types/uif-types';

interface UIFOperationListProps {
  operations: UIFOperation[];
  onUpdateStatus: (operationId: string, status: string) => Promise<void>;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function UIFOperationList({ operations, onUpdateStatus }: UIFOperationListProps) {
  if (operations.length === 0) {
    return (
      <Card className="p-8">
        <div className="text-center space-y-2">
          <p className="text-neutral-600">No hay operaciones vulnerables registradas</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-neutral-600">Caso</th>
              <th className="text-left px-4 py-3 font-medium text-neutral-600">Tipo</th>
              <th className="text-right px-4 py-3 font-medium text-neutral-600">Monto</th>
              <th className="text-center px-4 py-3 font-medium text-neutral-600">Riesgo</th>
              <th className="text-center px-4 py-3 font-medium text-neutral-600">Estado</th>
              <th className="text-left px-4 py-3 font-medium text-neutral-600">Fecha</th>
              <th className="text-right px-4 py-3 font-medium text-neutral-600">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {operations.map((op) => (
              <tr key={op.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-medium">{op.case_id.substring(0, 8)}...</td>
                <td className="px-4 py-3 capitalize">{op.tipo_operacion}</td>
                <td className="px-4 py-3 text-right font-medium">{formatCurrency(op.monto_operacion)}</td>
                <td className="px-4 py-3 text-center">
                  <span className={cn('px-2 py-0.5 text-xs font-medium rounded-full', UIF_RIESGO_COLORS[op.nivel_riesgo])}>
                    {UIF_RIESGO_LABELS[op.nivel_riesgo]}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="text-xs capitalize">{UIF_STATUS_LABELS[op.status]}</span>
                </td>
                <td className="px-4 py-3 text-neutral-500">{formatDate(op.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  {op.status === 'pendiente' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onUpdateStatus(op.id, 'reportado')}
                    >
                      Marcar Reportado
                    </Button>
                  )}
                  {op.status === 'reportado' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onUpdateStatus(op.id, 'archivado')}
                    >
                      Archivar
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
