/**
 * TemplateEditor Component
 * Edit template metadata and settings
 */

import { useState, useEffect } from 'react';
import { Save, X, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { DocumentType, TemplateInfo } from '@/store';

interface TemplateEditorProps {
  template: TemplateInfo | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, name: string, type: DocumentType) => Promise<void>;
  isLoading?: boolean;
}

const documentTypes: { value: DocumentType; label: string }[] = [
  { value: 'compraventa', label: 'Compraventa' },
  { value: 'donacion', label: 'Donación' },
  { value: 'testamento', label: 'Testamento' },
  { value: 'poder', label: 'Poder' },
  { value: 'sociedad', label: 'Sociedad' },
];

export function TemplateEditor({
  template,
  isOpen,
  onClose,
  onSave,
  isLoading,
}: TemplateEditorProps) {
  const [templateName, setTemplateName] = useState('');
  const [templateType, setTemplateType] = useState<DocumentType>('compraventa');
  const [error, setError] = useState<string | null>(null);

  // Reset form when template changes
  useEffect(() => {
    if (template) {
      setTemplateName(template.name);
      setTemplateType(template.type || 'compraventa');
      setError(null);
    }
  }, [template]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!template) return;

    if (!templateName.trim()) {
      setError('Por favor ingresa un nombre para el template');
      return;
    }

    try {
      await onSave(template.id, templateName, templateType);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error al actualizar template');
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      setError(null);
      onClose();
    }
  };

  if (!template) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Editar Template</DialogTitle>
          <DialogDescription>
            Actualiza el nombre y tipo del template
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Template Name */}
          <div>
            <Label htmlFor="edit-template-name">Nombre del Template</Label>
            <Input
              id="edit-template-name"
              type="text"
              placeholder="Ej: Escritura Compraventa 2024"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              disabled={isLoading}
              className="mt-2"
            />
          </div>

          {/* Document Type */}
          <div>
            <Label htmlFor="edit-template-type">Tipo de Documento</Label>
            <Select
              value={templateType}
              onValueChange={(value) => setTemplateType(value as DocumentType)}
              disabled={isLoading}
            >
              <SelectTrigger className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {documentTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Template ID (read-only) */}
          <div>
            <Label>ID del Template</Label>
            <Input
              type="text"
              value={template.id}
              disabled
              className="mt-2 bg-neutral-50"
            />
            <p className="text-xs text-neutral-500 mt-1">
              Este ID es único y no se puede modificar
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4">
            <Button type="submit" disabled={isLoading} className="gap-2">
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Guardar Cambios
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
              className="gap-2"
            >
              <X className="w-4 h-4" />
              Cancelar
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
