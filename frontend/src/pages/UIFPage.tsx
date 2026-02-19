/**
 * UIFPage
 * Panel for managing vulnerable operations (UIF/PLD)
 */

import { useState, useEffect } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { UIFOperationList } from '@/components/uif/UIFOperationList';
import { uifApi } from '@/api/endpoints/uif';
import { useToast } from '@/hooks';
import type { UIFOperation, UIFSummary } from '@/api/types/uif-types';
import { UIF_RIESGO_COLORS, UIF_RIESGO_LABELS } from '@/api/types/uif-types';
import { cn } from '@/lib/utils';

export function UIFPage() {
  const toast = useToast();
  const [operations, setOperations] = useState<UIFOperation[]>([]);
  const [summary, setSummary] = useState<UIFSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const loadData = async () => {
    setIsLoading(true);
    try {
      const result = await uifApi.list({ status: statusFilter });
      setOperations(result.operations);
      setSummary(result.summary);
    } catch (err) {
      console.error('Error loading UIF data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleUpdateStatus = async (operationId: string, status: string) => {
    try {
      await uifApi.update(operationId, { status });
      toast.success(`Operacion marcada como ${status}`);
      loadData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al actualizar');
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-orange-600" />
            <h1 className="text-2xl font-bold text-neutral-900">UIF / PLD</h1>
            <span className="text-sm text-neutral-500">Actividades Vulnerables</span>
          </div>
          <Button variant="outline" onClick={loadData} disabled={isLoading} className="gap-2">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <Card className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">Total</p>
              <p className="text-2xl font-bold">{summary.total}</p>
            </Card>
            <Card className="p-4 text-center border-orange-200 bg-orange-50">
              <p className="text-xs text-orange-600 uppercase">Vulnerables</p>
              <p className="text-2xl font-bold text-orange-700">{summary.vulnerables}</p>
            </Card>
            {Object.entries(summary.by_riesgo).map(([riesgo, count]) => (
              <Card key={riesgo} className={cn('p-4 text-center', UIF_RIESGO_COLORS[riesgo as keyof typeof UIF_RIESGO_COLORS]?.split(' ')[0])}>
                <p className="text-xs uppercase">{UIF_RIESGO_LABELS[riesgo as keyof typeof UIF_RIESGO_LABELS] || riesgo}</p>
                <p className="text-2xl font-bold">{count}</p>
              </Card>
            ))}
          </div>
        )}

        {/* Status Filter */}
        <div className="flex gap-2">
          <Button
            variant={!statusFilter ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter(undefined)}
          >
            Todos
          </Button>
          {['pendiente', 'reportado', 'archivado'].map((st) => (
            <Button
              key={st}
              variant={statusFilter === st ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter(st)}
              className="capitalize"
            >
              {st}
            </Button>
          ))}
        </div>

        {/* Operations List */}
        {isLoading && operations.length === 0 ? (
          <div className="h-48 bg-neutral-200 rounded animate-pulse" />
        ) : (
          <UIFOperationList
            operations={operations}
            onUpdateStatus={handleUpdateStatus}
          />
        )}
      </div>
    </MainLayout>
  );
}
