/**
 * FieldGroup Component
 * Group of related form fields with label, input, and validation
 */

import { HelpCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
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
}: FieldGroupProps) {
  const displayValue = value?.toString() || '';

  return (
    <div className="space-y-2">
      {/* Label with help */}
      <div className="flex items-center justify-between">
        <Label htmlFor={fieldName} className={cn(required && 'after:content-["*"] after:ml-0.5 after:text-destructive')}>
          {label}
        </Label>

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
