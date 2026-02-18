import { Badge } from '@/components/ui/badge';
import { STATUS_LABELS, STATUS_COLORS } from '@/api/types/cases-types';
import type { CaseStatus } from '@/api/types/cases-types';

interface CaseStatusBadgeProps {
  status: CaseStatus;
  className?: string;
}

export function CaseStatusBadge({ status, className }: CaseStatusBadgeProps) {
  return (
    <Badge className={`${STATUS_COLORS[status]} ${className || ''}`}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}
