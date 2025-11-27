/**
 * TemplateUpload Component
 * Upload new template with file selection and metadata
 */

import { useState } from 'react';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';
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
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { DocumentType } from '@/store';

interface TemplateUploadProps {
  onUpload: (file: File, name: string, type: DocumentType) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

const documentTypes: { value: DocumentType; label: string }[] = [
  { value: 'compraventa', label: 'Compraventa' },
  { value: 'donacion', label: 'Donación' },
  { value: 'testamento', label: 'Testamento' },
  { value: 'poder', label: 'Poder' },
  { value: 'sociedad', label: 'Sociedad' },
];

export function TemplateUpload({ onUpload, onCancel, isLoading }: TemplateUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [templateType, setTemplateType] = useState<DocumentType | ''>('');
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (selectedFile: File | null) => {
    if (!selectedFile) return;

    // Validate file type
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
    ];

    if (!validTypes.includes(selectedFile.type)) {
      setError('Solo se permiten archivos .docx o .doc');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selectedFile.size > maxSize) {
      setError('El archivo debe ser menor a 10MB');
      return;
    }

    setFile(selectedFile);
    setError(null);

    // Auto-fill template name from filename if empty
    if (!templateName) {
      const nameWithoutExt = selectedFile.name.replace(/\.(docx?|DOCX?)$/, '');
      setTemplateName(nameWithoutExt);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Por favor selecciona un archivo');
      return;
    }

    if (!templateName.trim()) {
      setError('Por favor ingresa un nombre para el template');
      return;
    }

    if (!templateType) {
      setError('Por favor selecciona un tipo de documento');
      return;
    }

    try {
      await onUpload(file, templateName, templateType);
      // Reset form on success
      setFile(null);
      setTemplateName('');
      setTemplateType('');
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error al subir template');
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Area */}
        <div>
          <Label>Archivo del Template</Label>
          <div
            className={cn(
              'mt-2 border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              isDragging
                ? 'border-primary-500 bg-primary-50'
                : 'border-neutral-300 hover:border-neutral-400',
              file && 'border-success bg-success/5'
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            {!file ? (
              <>
                <Upload className="w-12 h-12 mx-auto mb-4 text-neutral-400" />
                <div className="space-y-2">
                  <p className="text-sm font-medium text-neutral-900">
                    Arrastra tu archivo aquí o haz click para seleccionar
                  </p>
                  <p className="text-xs text-neutral-500">
                    Solo archivos .docx o .doc (máx. 10MB)
                  </p>
                </div>
                <input
                  type="file"
                  accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
                  className="hidden"
                  id="file-upload"
                  disabled={isLoading}
                />
                <Label htmlFor="file-upload">
                  <Button
                    type="button"
                    variant="outline"
                    className="mt-4"
                    disabled={isLoading}
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    Seleccionar Archivo
                  </Button>
                </Label>
              </>
            ) : (
              <div className="flex items-center justify-between bg-white rounded-lg p-4 border border-neutral-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-success/10 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-success-600" />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-neutral-900">
                      {file.name}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={removeFile}
                  disabled={isLoading}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Template Name */}
        <div>
          <Label htmlFor="template-name">Nombre del Template</Label>
          <Input
            id="template-name"
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
          <Label htmlFor="template-type">Tipo de Documento</Label>
          <Select
            value={templateType}
            onValueChange={(value) => setTemplateType(value as DocumentType)}
            disabled={isLoading}
          >
            <SelectTrigger className="mt-2">
              <SelectValue placeholder="Selecciona un tipo" />
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

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={isLoading || !file} className="gap-2">
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Subir Template
              </>
            )}
          </Button>
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancelar
            </Button>
          )}
        </div>
      </form>
    </Card>
  );
}
