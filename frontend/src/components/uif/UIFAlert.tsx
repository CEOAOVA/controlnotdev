/**
 * UIFAlert
 * Inline alert shown in CaseDetailPage when case is vulnerable
 */

import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { uifApi } from '@/api/endpoints/uif';
import type { UIFOperation } from '@/api/types/uif-types';
import { UIF_RIESGO_LABELS, UIF_RIESGO_COLORS } from '@/api/types/uif-types';

interface UIFAlertProps {
  caseId: string;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount);
}

export function UIFAlert({ caseId }: UIFAlertProps) {
  const [operation, setOperation] = useState<UIFOperation | null>(null);

  useEffect(() => {
    uifApi.check(caseId).then((r) => {
      if (r.flagged && r.operation) {
        setOperation(r.operation);
      }
    }).catch(() => {});
  }, [caseId]);

  if (!operation || !operation.es_vulnerable) return null;

  const riesgoColor = UIF_RIESGO_COLORS[operation.nivel_riesgo] || 'bg-gray-100 text-gray-700';

  return (
    <Alert className="border-orange-300 bg-orange-50">
      <AlertTriangle className="h-4 w-4 text-orange-600" />
      <AlertDescription className="flex items-center gap-2 flex-wrap">
        <span className="font-medium text-orange-800">Operacion Vulnerable UIF/PLD</span>
        <span className={cn('px-2 py-0.5 text-xs font-medium rounded-full', riesgoColor)}>
          Riesgo: {UIF_RIESGO_LABELS[operation.nivel_riesgo]}
        </span>
        <span className="text-sm text-orange-700">
          Monto: {formatCurrency(operation.monto_operacion)} |
          Umbral: {formatCurrency(operation.umbral_aplicado)} |
          Estado: {operation.status}
        </span>
        {operation.requiere_aviso && (
          <span className="text-xs text-red-600 font-medium">Requiere aviso a UIF</span>
        )}
      </AlertDescription>
    </Alert>
  );
}
