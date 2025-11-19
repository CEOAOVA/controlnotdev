/**
 * ProgressIndicator Component
 * Stepper showing current step in document processing workflow
 */

import { Upload, Edit, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ProcessStep = 'upload' | 'edit' | 'complete';

interface ProgressIndicatorProps {
  currentStep: ProcessStep;
  onStepClick?: (step: ProcessStep) => void;
  completedSteps?: ProcessStep[];
}

const steps: {
  id: ProcessStep;
  label: string;
  icon: typeof Upload;
  description: string;
}[] = [
  {
    id: 'upload',
    label: 'Subir Documentos',
    icon: Upload,
    description: 'Selecciona template y sube archivos',
  },
  {
    id: 'edit',
    label: 'Editar Datos',
    icon: Edit,
    description: 'Revisa y corrige la información',
  },
  {
    id: 'complete',
    label: 'Completar',
    icon: CheckCircle,
    description: 'Descarga o envía el documento',
  },
];

const stepOrder: ProcessStep[] = ['upload', 'edit', 'complete'];

export function ProgressIndicator({
  currentStep,
  onStepClick,
  completedSteps = [],
}: ProgressIndicatorProps) {
  const currentIndex = stepOrder.indexOf(currentStep);

  const isStepCompleted = (step: ProcessStep) => completedSteps.includes(step);
  const isStepCurrent = (step: ProcessStep) => step === currentStep;
  const isStepAccessible = (step: ProcessStep) => {
    const stepIndex = stepOrder.indexOf(step);
    return stepIndex <= currentIndex || isStepCompleted(step);
  };

  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between relative">
        {/* Progress line */}
        <div className="absolute top-5 left-0 w-full h-0.5 bg-muted -z-10">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{
              width: `${(currentIndex / (steps.length - 1)) * 100}%`,
            }}
          />
        </div>

        {/* Steps */}
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = isStepCompleted(step.id);
          const isCurrent = isStepCurrent(step.id);
          const isAccessible = isStepAccessible(step.id);

          return (
            <div key={step.id} className="flex flex-col items-center flex-1">
              {/* Icon circle */}
              <button
                onClick={() => isAccessible && onStepClick?.(step.id)}
                disabled={!isAccessible}
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                  'border-2 relative z-10',
                  isCurrent &&
                    'bg-primary border-primary text-primary-foreground scale-110 shadow-lg',
                  isCompleted &&
                    !isCurrent &&
                    'bg-primary/10 border-primary text-primary',
                  !isCurrent &&
                    !isCompleted &&
                    'bg-background border-muted-foreground/30 text-muted-foreground',
                  isAccessible && 'cursor-pointer hover:scale-105',
                  !isAccessible && 'cursor-not-allowed opacity-50'
                )}
              >
                <Icon className="w-5 h-5" />
              </button>

              {/* Label */}
              <div className="mt-3 text-center max-w-[120px]">
                <p
                  className={cn(
                    'text-sm font-medium transition-colors',
                    isCurrent && 'text-primary font-semibold',
                    !isCurrent && 'text-muted-foreground'
                  )}
                >
                  {step.label}
                </p>
                <p
                  className={cn(
                    'text-xs mt-0.5 transition-colors',
                    isCurrent && 'text-foreground',
                    !isCurrent && 'text-muted-foreground'
                  )}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
