/**
 * UnifiedUploader Component
 * Combined uploader for templates (.docx) and categorized documents (images/PDF)
 */

import { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  FileImage,
  Loader2,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

// Existing components
import { TemplateCard } from '@/components/template/TemplateCard';
import { TypeBadge } from '@/components/template/TypeBadge';
import { CategoryTab } from './CategoryTab';

// Hooks and stores
import { useTemplates, useCategories, useToast } from '@/hooks';
import { useDocumentStore } from '@/store';
import type { DocumentType } from '@/store';

interface UnifiedUploaderProps {
  onTemplateSelected?: (hasTemplate: boolean) => void;
  onFilesChange?: (totalFiles: number) => void;
}

export function UnifiedUploader({ onTemplateSelected, onFilesChange }: UnifiedUploaderProps) {
  const [filterType, setFilterType] = useState<DocumentType | 'all'>('all');
  const toast = useToast();

  // Template hooks
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

  // Category/documents hooks
  const {
    categories,
    files,
    addFilesWithValidation,
    removeFile,
    clearCategory,
    getTotalFilesCount,
    isLoadingCategories,
  } = useCategories();

  const { documentType } = useDocumentStore();

  // Template dropzone
  const templateDropzone = useDropzone({
    onDrop: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file) return;

      if (!file.name.endsWith('.docx')) {
        toast.error('Por favor selecciona un archivo Word (.docx)');
        return;
      }

      try {
        await uploadCustomTemplate(file);
        onTemplateSelected?.(true);
      } catch (error) {
        console.error('Error uploading template:', error);
        toast.error('Error al subir el template');
      }
    },
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  // Filter templates by type
  const filteredTemplates = templates.filter((t) => {
    if (filterType === 'all') return true;
    return t.type === filterType;
  });

  // Notify parent when files change
  useEffect(() => {
    onFilesChange?.(getTotalFilesCount());
  }, [files, getTotalFilesCount, onFilesChange]);

  return (
    <div className="space-y-6">
      {/* ========== SECCION 1: TEMPLATE ========== */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">1. Plantilla Word</h3>
                <p className="text-sm text-muted-foreground">
                  Sube o selecciona tu plantilla .docx
                </p>
              </div>
            </div>

            {/* Selected template indicator */}
            {selectedTemplate && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <AlertTitle className="text-green-800">Plantilla seleccionada</AlertTitle>
                <AlertDescription className="flex items-center gap-2 mt-1">
                  <span className="font-medium text-green-700">{selectedTemplate.name}</span>
                  {selectedTemplate.type && <TypeBadge type={selectedTemplate.type} size="sm" />}
                  {confidenceScore !== null && (
                    <Badge variant={confidenceScore >= 0.7 ? 'default' : 'secondary'}>
                      {Math.round(confidenceScore * 100)}% confianza
                    </Badge>
                  )}
                </AlertDescription>
              </Alert>
            )}

            {/* Low confidence warning */}
            {requiresConfirmation && selectedTemplate && (
              <Alert variant="destructive" className="border-yellow-500 bg-yellow-50">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                <AlertTitle className="text-yellow-800">Verificar tipo de documento</AlertTitle>
                <AlertDescription className="text-yellow-700">
                  La deteccion automatica tiene baja confianza. Verifica que el tipo "
                  {selectedTemplate.type}" sea correcto.
                </AlertDescription>
              </Alert>
            )}

            {/* Template dropzone */}
            <div
              {...templateDropzone.getRootProps()}
              className={cn(
                'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all',
                'hover:border-blue-400 hover:bg-blue-50/50',
                templateDropzone.isDragActive && 'border-blue-500 bg-blue-50',
                isUploading && 'opacity-50 cursor-not-allowed'
              )}
            >
              <input {...templateDropzone.getInputProps()} />

              <div className="flex flex-col items-center gap-2">
                {isUploading ? (
                  <>
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    <p className="text-sm text-muted-foreground">Subiendo plantilla...</p>
                  </>
                ) : (
                  <>
                    <Upload className="w-8 h-8 text-blue-500" />
                    <p className="font-medium">
                      {templateDropzone.isDragActive
                        ? 'Suelta la plantilla aqui...'
                        : 'Arrastra tu plantilla Word o haz click'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Formato: .docx con placeholders {'{{campo}}'}
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Available templates */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  O selecciona una plantilla existente:
                </p>
                <Select
                  value={filterType}
                  onValueChange={(value) => setFilterType(value as DocumentType | 'all')}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filtrar por tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="compraventa">Compraventa</SelectItem>
                    <SelectItem value="donacion">Donacion</SelectItem>
                    <SelectItem value="testamento">Testamento</SelectItem>
                    <SelectItem value="poder">Poder</SelectItem>
                    <SelectItem value="sociedad">Sociedad</SelectItem>
                    <SelectItem value="cancelacion">Cancelacion</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {isLoadingTemplates ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                </div>
              ) : filteredTemplates.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No hay plantillas disponibles
                </p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {filteredTemplates.slice(0, 8).map((template) => (
                    <TemplateCard
                      key={template.id}
                      template={template}
                      isSelected={selectedTemplate?.id === template.id}
                      onSelect={async () => {
                        await selectTemplate(template);
                        onTemplateSelected?.(true);
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ========== SECCION 2: DOCUMENTOS ========== */}
      {documentType && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <FileImage className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">2. Documentos</h3>
                  <p className="text-sm text-muted-foreground">
                    Sube imagenes y PDFs organizados por categoria
                  </p>
                </div>
                {getTotalFilesCount() > 0 && (
                  <Badge variant="secondary">
                    {getTotalFilesCount()} {getTotalFilesCount() === 1 ? 'archivo' : 'archivos'}
                  </Badge>
                )}
              </div>

              {/* Loading state */}
              {isLoadingCategories ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center space-y-2">
                    <Loader2 className="w-6 h-6 animate-spin text-muted-foreground mx-auto" />
                    <p className="text-sm text-muted-foreground">Cargando categorias...</p>
                  </div>
                </div>
              ) : categories.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Selecciona una plantilla primero para ver las categorias disponibles.
                  </AlertDescription>
                </Alert>
              ) : (
                <Tabs defaultValue={categories[0]?.name} className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    {categories.map((category) => {
                      const count = files[category.name]?.length || 0;
                      return (
                        <TabsTrigger key={category.name} value={category.name} className="gap-2">
                          <span>{category.icon}</span>
                          <span>{category.name}</span>
                          {count > 0 && (
                            <Badge variant="secondary" className="ml-1 px-1.5 py-0.5 text-xs">
                              {count}
                            </Badge>
                          )}
                        </TabsTrigger>
                      );
                    })}
                  </TabsList>

                  {categories.map((category) => (
                    <TabsContent key={category.name} value={category.name} className="mt-4">
                      <CategoryTab
                        category={category}
                        files={files[category.name] || []}
                        onFilesAdded={(newFiles) => {
                          const result = addFilesWithValidation(category.name, newFiles);
                          if (result.errors.length > 0) {
                            result.errors.forEach((error) => toast.error(error));
                          } else if (result.validFiles.length > 0) {
                            toast.success(
                              `${result.validFiles.length} archivo(s) agregado(s) a ${category.name}`
                            );
                          }
                        }}
                        onFileRemove={(fileId) => removeFile(category.name, fileId)}
                        onClearAll={() => clearCategory(category.name)}
                      />
                    </TabsContent>
                  ))}
                </Tabs>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
