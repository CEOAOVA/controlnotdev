/**
 * FieldGroup Component
 * Group of related form fields with label, input, and validation
 */

import { HelpCircle, Info } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
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
          className={cn(error && 'border-destructive focus-visible:ring-destructive')}
        />
      ) : (
        <Input
          id={fieldName}
          type={type}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || `Ingresa ${label.toLowerCase()}`}
          className={cn(error && 'border-destructive focus-visible:ring-destructive')}
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
