import { Badge } from '@/components/ui/badge';
import type { CasePriority } from '@/api/types/cases-types';

const PRIORITY_LABELS: Record<CasePriority, string> = {
  baja: 'Baja',
  normal: 'Normal',
  alta: 'Alta',
  urgente: 'Urgente',
};

const PRIORITY_COLORS: Record<CasePriority, string> = {
  baja: 'bg-gray-100 text-gray-600',
  normal: 'bg-blue-100 text-blue-700',
  alta: 'bg-orange-100 text-orange-700',
  urgente: 'bg-red-100 text-red-700',
};

interface CasePriorityBadgeProps {
  priority: CasePriority;
  className?: string;
}

export function CasePriorityBadge({ priority, className }: CasePriorityBadgeProps) {
  return (
    <Badge className={`${PRIORITY_COLORS[priority]} ${className || ''}`}>
      {PRIORITY_LABELS[priority]}
    </Badge>
  );
}
