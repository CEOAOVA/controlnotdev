import { cn } from '@/lib/utils';
import type { TramiteSemaforo } from '@/api/types/cases-types';

const SEMAFORO_COLORS: Record<TramiteSemaforo, string> = {
  verde: 'bg-green-500',
  amarillo: 'bg-yellow-500',
  rojo: 'bg-red-500',
  gris: 'bg-gray-400',
};

const SEMAFORO_LABELS: Record<TramiteSemaforo, string> = {
  verde: 'En tiempo',
  amarillo: 'Por vencer',
  rojo: 'Vencido',
  gris: 'Sin fecha',
};

interface TramiteSemaforoPillProps {
  semaforo: TramiteSemaforo;
  showLabel?: boolean;
  className?: string;
}

export function TramiteSemaforoPill({ semaforo, showLabel = false, className }: TramiteSemaforoPillProps) {
  return (
    <div className={cn('flex items-center gap-1.5', className)}>
      <div className={cn('w-3 h-3 rounded-full', SEMAFORO_COLORS[semaforo])} />
      {showLabel && (
        <span className="text-xs text-neutral-600">{SEMAFORO_LABELS[semaforo]}</span>
      )}
    </div>
  );
}
