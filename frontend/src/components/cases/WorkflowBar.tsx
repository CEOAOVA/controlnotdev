import { cn } from '@/lib/utils';
import { STATUS_LABELS } from '@/api/types/cases-types';
import type { CaseStatus } from '@/api/types/cases-types';

const WORKFLOW_STEPS: CaseStatus[] = [
  'borrador', 'en_revision', 'checklist_pendiente', 'presupuesto',
  'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
  'inscripcion', 'facturacion', 'entrega', 'cerrado',
];

interface WorkflowBarProps {
  currentStatus: CaseStatus;
}

export function WorkflowBar({ currentStatus }: WorkflowBarProps) {
  if (currentStatus === 'cancelado' || currentStatus === 'suspendido') {
    return (
      <div className="flex items-center gap-2 p-3 rounded-lg bg-neutral-50">
        <div className={cn(
          'w-3 h-3 rounded-full',
          currentStatus === 'cancelado' ? 'bg-red-500' : 'bg-rose-500'
        )} />
        <span className="text-sm font-medium text-neutral-700">
          {STATUS_LABELS[currentStatus]}
        </span>
      </div>
    );
  }

  const currentIndex = WORKFLOW_STEPS.indexOf(currentStatus);

  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-center gap-1 min-w-[600px] p-2">
        {WORKFLOW_STEPS.map((step, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium border-2',
                    isCompleted && 'bg-green-500 border-green-500 text-white',
                    isCurrent && 'bg-blue-500 border-blue-500 text-white',
                    !isCompleted && !isCurrent && 'bg-white border-neutral-300 text-neutral-400',
                  )}
                >
                  {isCompleted ? '\u2713' : index + 1}
                </div>
                <span
                  className={cn(
                    'text-[10px] mt-1 text-center leading-tight whitespace-nowrap',
                    isCurrent && 'font-semibold text-blue-700',
                    isCompleted && 'text-green-700',
                    !isCompleted && !isCurrent && 'text-neutral-400',
                  )}
                >
                  {STATUS_LABELS[step]}
                </span>
              </div>
              {index < WORKFLOW_STEPS.length - 1 && (
                <div
                  className={cn(
                    'h-0.5 flex-1 min-w-2',
                    index < currentIndex ? 'bg-green-500' : 'bg-neutral-200',
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
