import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ChecklistItem, ChecklistStatus } from '@/api/types/cases-types';

const STATUS_OPTIONS: { value: ChecklistStatus; label: string }[] = [
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'solicitado', label: 'Solicitado' },
  { value: 'recibido', label: 'Recibido' },
  { value: 'aprobado', label: 'Aprobado' },
  { value: 'rechazado', label: 'Rechazado' },
  { value: 'no_aplica', label: 'No Aplica' },
];

const STATUS_BADGE_COLORS: Record<ChecklistStatus, string> = {
  pendiente: 'bg-gray-100 text-gray-700',
  solicitado: 'bg-blue-100 text-blue-700',
  recibido: 'bg-teal-100 text-teal-700',
  aprobado: 'bg-green-100 text-green-700',
  rechazado: 'bg-red-100 text-red-700',
  no_aplica: 'bg-neutral-100 text-neutral-500',
};

interface ChecklistItemRowProps {
  item: ChecklistItem;
  onStatusChange: (itemId: string, status: ChecklistStatus) => void;
  onRemove: (itemId: string) => void;
}

export function ChecklistItemRow({ item, onStatusChange, onRemove }: ChecklistItemRowProps) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 hover:bg-neutral-50 rounded-lg">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={cn('text-sm', item.obligatorio && 'font-medium')}>{item.nombre}</span>
          {item.obligatorio && (
            <Badge variant="outline" className="text-[10px] px-1 py-0">Obligatorio</Badge>
          )}
        </div>
        {item.notas && <p className="text-xs text-neutral-500 truncate">{item.notas}</p>}
      </div>

      <Badge className={STATUS_BADGE_COLORS[item.status] || 'bg-gray-100 text-gray-700'} >
        <span className="hidden sm:inline">{STATUS_OPTIONS.find(s => s.value === item.status)?.label}</span>
      </Badge>

      <Select
        value={item.status}
        onValueChange={(v) => onStatusChange(item.id, v as ChecklistStatus)}
      >
        <SelectTrigger className="w-[130px] h-8 text-xs">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {STATUS_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-red-600" onClick={() => onRemove(item.id)}>
        <Trash2 className="w-4 h-4" />
      </Button>
    </div>
  );
}
