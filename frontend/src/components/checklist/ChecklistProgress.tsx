import { Progress } from '@/components/ui/progress';

interface ChecklistProgressProps {
  total: number;
  completed: number;
  pct: number;
}

export function ChecklistProgress({ total, completed, pct }: ChecklistProgressProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-neutral-600">
          {completed}/{total} obligatorios
        </span>
        <span className="font-medium text-neutral-900">{Math.round(pct)}%</span>
      </div>
      <Progress value={pct} className="h-2" />
    </div>
  );
}
