/**
 * TemplateSelector Component
 * Main component for selecting or uploading Word templates
 */

import { useState, useRef } from 'react';
import { Upload, FileText, Loader2, AlertCircle, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { TemplateCard } from './TemplateCard';
import { TypeBadge } from './TypeBadge';
import { useTemplates } from '@/hooks';
import type { DocumentType } from '@/store';

interface TemplateSelectorProps {
  onTemplateSelected?: (hasTemplate: boolean) => void;
}

export function TemplateSelector({ onTemplateSelected }: TemplateSelectorProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [filterType, setFilterType] = useState<DocumentType | 'all'>('all');

  const {
    templates,
    selectedTemplate,
    selectTemplate,
    uploadCustomTemplate,
    isLoadingTemplates,
    isUploading,
    confidenceScore,
    requiresConfirmation,
  } = useTemplates();

  // Filter templates by type
  const filteredTemplates = templates.filter((t) => {
    if (filterType === 'all') return true;
    return t.type === filterType;
  });

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.docx')) {
      alert('Por favor selecciona un archivo Word (.docx)');
      return;
    }

    try {
      await uploadCustomTemplate(file);
      if (onTemplateSelected) {
        onTemplateSelected(true);
      }
    } catch (error) {
      console.error('Error uploading template:', error);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (isLoadingTemplates) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center space-y-2">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Cargando templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Selecciona un Template</h2>
        <p className="text-muted-foreground mt-1">
          Elige un template existente o sube tu propio archivo Word
        </p>
      </div>

      {/* Selected template banner */}
      {selectedTemplate && (
        <Alert className="border-primary/50 bg-primary/5">
          <FileText className="h-4 w-4" />
          <AlertTitle>Template seleccionado</AlertTitle>
          <AlertDescription className="flex items-center gap-2 mt-2">
            <span className="font-medium">{selectedTemplate.name}</span>
            {selectedTemplate.type && <TypeBadge type={selectedTemplate.type} size="sm" />}
            {confidenceScore !== null && (
              <span className={`text-xs px-2 py-0.5 rounded ${
                confidenceScore >= 0.7
                  ? 'bg-green-100 text-green-700'
                  : 'bg-yellow-100 text-yellow-700'
              }`}>
                {Math.round(confidenceScore * 100)}% confianza
              </span>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Low confidence warning */}
      {requiresConfirmation && selectedTemplate && (
        <Alert variant="destructive" className="border-yellow-500 bg-yellow-50 text-yellow-800">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertTitle className="text-yellow-800">Verificar tipo de documento</AlertTitle>
          <AlertDescription className="text-yellow-700">
            La detección automática tiene baja confianza ({Math.round((confidenceScore || 0) * 100)}%).
            Por favor verifica que el tipo "{selectedTemplate.type}" sea correcto o selecciona otro
            template del tipo adecuado.
          </AlertDescription>
        </Alert>
      )}

      {/* Upload custom template */}
      <div className="bg-muted/50 rounded-lg p-6 border-2 border-dashed">
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="p-3 bg-primary/10 rounded-full">
            <Upload className="w-6 h-6 text-primary" />
          </div>

          <div>
            <h3 className="font-semibold">Sube tu propio template</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Archivo Word (.docx) con placeholders en formato {`{{campo}}`}
            </p>
          </div>

          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="gap-2"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Seleccionar archivo
              </>
            )}
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".docx"
            className="hidden"
            onChange={handleFileUpload}
          />
        </div>
      </div>

      {/* Templates list */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Templates disponibles</h3>

          {/* Filter by type */}
          <Select
            value={filterType}
            onValueChange={(value) => setFilterType(value as DocumentType | 'all')}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrar por tipo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los tipos</SelectItem>
              <SelectItem value="compraventa">Compraventa</SelectItem>
              <SelectItem value="donacion">Donación</SelectItem>
              <SelectItem value="testamento">Testamento</SelectItem>
              <SelectItem value="poder">Poder</SelectItem>
              <SelectItem value="sociedad">Sociedad</SelectItem>
              <SelectItem value="cancelacion">Cancelación</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {filteredTemplates.length === 0 ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No hay templates disponibles
              {filterType !== 'all' && ' para este tipo de documento'}.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                isSelected={selectedTemplate?.id === template.id}
                onSelect={async () => {
                  await selectTemplate(template);
                  if (onTemplateSelected) {
                    onTemplateSelected(true);
                  }
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
