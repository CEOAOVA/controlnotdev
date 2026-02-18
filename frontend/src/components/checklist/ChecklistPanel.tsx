import { useState } from 'react';
import { RotateCcw, ClipboardCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChecklistItemRow } from './ChecklistItemRow';
import { ChecklistProgress } from './ChecklistProgress';
import type { ChecklistItem, ChecklistSummary, ChecklistStatus, ChecklistCategoria } from '@/api/types/cases-types';

const CATEGORY_LABELS: Record<ChecklistCategoria, string> = {
  parte_a: 'Parte A',
  parte_b: 'Parte B',
  inmueble: 'Inmueble',
  fiscal: 'Fiscal',
  gobierno: 'Gobierno',
  general: 'General',
};

interface ChecklistPanelProps {
  items: ChecklistItem[];
  summary?: ChecklistSummary;
  onInitialize: () => Promise<void>;
  onStatusChange: (itemId: string, status: ChecklistStatus) => Promise<void>;
  onRemove: (itemId: string) => Promise<void>;
}

export function ChecklistPanel({ items, summary, onInitialize, onStatusChange, onRemove }: ChecklistPanelProps) {
  const [initializing, setInitializing] = useState(false);

  const handleInitialize = async () => {
    setInitializing(true);
    try {
      await onInitialize();
    } finally {
      setInitializing(false);
    }
  };

  // Group items by category
  const grouped = items.reduce<Record<string, ChecklistItem[]>>((acc, item) => {
    const cat = item.categoria || 'general';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">
          Checklist ({items.length} items)
        </h3>
        <div className="flex gap-2">
          {items.length === 0 && (
            <Button size="sm" className="gap-1" onClick={handleInitialize} disabled={initializing}>
              <RotateCcw className="w-4 h-4" />
              {initializing ? 'Inicializando...' : 'Inicializar desde Catalogo'}
            </Button>
          )}
        </div>
      </div>

      {summary && (
        <ChecklistProgress
          total={summary.obligatorios}
          completed={summary.obligatorios_completados}
          pct={summary.completion_pct}
        />
      )}

      {items.length === 0 ? (
        <Card className="p-8">
          <div className="text-center space-y-2">
            <ClipboardCheck className="w-10 h-10 text-neutral-400 mx-auto" />
            <p className="text-neutral-600">No hay items en el checklist</p>
            <p className="text-sm text-neutral-500">
              Haz clic en "Inicializar desde Catalogo" para crear items automaticamente
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {Object.entries(grouped).map(([category, categoryItems]) => (
            <Card key={category} className="p-4">
              <h4 className="text-sm font-semibold text-neutral-700 mb-2">
                {CATEGORY_LABELS[category as ChecklistCategoria] || category}
              </h4>
              <div className="space-y-1">
                {categoryItems.map((item) => (
                  <ChecklistItemRow
                    key={item.id}
                    item={item}
                    onStatusChange={(id, status) => onStatusChange(id, status)}
                    onRemove={onRemove}
                  />
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
