/**
 * FieldGroup Component
 * Group of related form fields with label, input, and validation
 */

import { HelpCircle, Info, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import type { ValidationStatus } from '@/api/types';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface FieldGroupProps {
  fieldName: string;
  label: string;
  value: string | number | null | undefined;
  onChange: (value: string) => void;
  description?: string;
  type?: 'text' | 'textarea' | 'number';
  required?: boolean;
  placeholder?: string;
  error?: string;
  /** Campo opcional - no se muestra como error si no se encuentra */
  optional?: boolean;
  /** Fuente del dato opcional */
  source?: string | null;
  /** OCR Robusto 2025: Confidence score (0.0 - 1.0) */
  confidence?: number;
  /** OCR Robusto 2025: Validation status */
  validationStatus?: ValidationStatus;
  /** OCR Robusto 2025: Issues found during validation */
  validationIssues?: string[];
}

// Helper function to get validation status icon
function ValidationIcon({ status }: { status: ValidationStatus }) {
  switch (status) {
    case 'valid':
      return <CheckCircle2 className="w-4 h-4 text-green-600" />;
    case 'suspicious':
      return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
    case 'invalid':
      return <XCircle className="w-4 h-4 text-red-600" />;
    default:
      return null;
  }
}

// Helper function to get confidence color
function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return 'bg-green-100 text-green-800 border-green-200';
  if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  if (confidence >= 0.5) return 'bg-orange-100 text-orange-800 border-orange-200';
  return 'bg-red-100 text-red-800 border-red-200';
}

// Helper function to get input border class based on validation
function getInputBorderClass(validationStatus?: ValidationStatus): string {
  switch (validationStatus) {
    case 'suspicious':
      return 'border-yellow-400 focus-visible:ring-yellow-400';
    case 'invalid':
      return 'border-red-400 focus-visible:ring-red-400';
    default:
      return '';
  }
}

export function FieldGroup({
  fieldName,
  label,
  value,
  onChange,
  description,
  type = 'text',
  required = false,
  placeholder,
  error,
  optional = false,
  source,
  confidence,
  validationStatus,
  validationIssues,
}: FieldGroupProps) {
  const displayValue = value?.toString() || '';

  // Mensaje para campos opcionales
  const optionalTooltip = source === 'boleta_rpp'
    ? 'Este campo es opcional - solo disponible si se incluye la Boleta del RPP'
    : 'Este campo es opcional - no es obligatorio completarlo';

  return (
    <div className="space-y-2">
      {/* Label with help */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Label htmlFor={fieldName} className={cn(required && 'after:content-["*"] after:ml-0.5 after:text-destructive')}>
            {label}
          </Label>

          {/* Indicador de campo opcional */}
          {optional && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge variant="outline" className="text-xs px-1.5 py-0 h-5 gap-1 text-muted-foreground border-muted-foreground/30">
                    <Info className="w-3 h-3" />
                    Opcional
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-sm">{optionalTooltip}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          {/* OCR Robusto 2025: Confidence badge */}
          {confidence !== undefined && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge
                    variant="outline"
                    className={cn('text-xs px-1.5 py-0 h-5', getConfidenceColor(confidence))}
                  >
                    {Math.round(confidence * 100)}%
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-sm">Confianza de extracción: {Math.round(confidence * 100)}%</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          {/* OCR Robusto 2025: Validation indicator */}
          {validationStatus && validationStatus !== 'not_validated' && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-help">
                    <ValidationIcon status={validationStatus} />
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="text-sm">
                    <p className="font-medium mb-1">
                      {validationStatus === 'valid' && 'Campo válido'}
                      {validationStatus === 'suspicious' && 'Campo sospechoso'}
                      {validationStatus === 'invalid' && 'Campo inválido'}
                    </p>
                    {validationIssues && validationIssues.length > 0 && (
                      <ul className="list-disc list-inside text-xs">
                        {validationIssues.map((issue, idx) => (
                          <li key={idx}>{issue}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>

        {description && (
          <Dialog>
            <DialogTrigger asChild>
              <button
                type="button"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <HelpCircle className="w-4 h-4" />
              </button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{label}</DialogTitle>
                <DialogDescription className="pt-4">
                  {description}
                </DialogDescription>
              </DialogHeader>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Input field */}
      {type === 'textarea' ? (
        <Textarea
          id={fieldName}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || `Ingresa ${label.toLowerCase()}`}
          rows={3}
          className={cn(
            error && 'border-destructive focus-visible:ring-destructive',
            !error && getInputBorderClass(validationStatus)
          )}
        />
      ) : (
        <Input
          id={fieldName}
          type={type}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || `Ingresa ${label.toLowerCase()}`}
          className={cn(
            error && 'border-destructive focus-visible:ring-destructive',
            !error && getInputBorderClass(validationStatus)
          )}
        />
      )}

      {/* Error message */}
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {/* Helper text */}
      {!error && description && (
        <p className="text-xs text-muted-foreground line-clamp-1">
          {description}
        </p>
      )}
    </div>
  );
}
