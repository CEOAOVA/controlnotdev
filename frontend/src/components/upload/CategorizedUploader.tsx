/**
 * CategorizedUploader Component
 * Main component for uploading files by category with tabs
 */

import { useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CategoryTab } from './CategoryTab';
import { useCategories, useToast } from '@/hooks';

interface CategorizedUploaderProps {
  onFilesChange?: (totalFiles: number) => void;
}

export function CategorizedUploader({ onFilesChange }: CategorizedUploaderProps) {
  const {
    categories,
    files,
    addFilesWithValidation,
    removeFile,
    clearCategory,
    getTotalFilesCount,
    isLoadingCategories,
  } = useCategories();
  const toast = useToast();

  // Notify parent when files change
  useEffect(() => {
    if (onFilesChange) {
      onFilesChange(getTotalFilesCount());
    }
  }, [files, getTotalFilesCount, onFilesChange]);

  if (isLoadingCategories) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Cargando categorías...</p>
        </div>
      </div>
    );
  }

  if (categories.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Primero selecciona un template para ver las categorías disponibles.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {/* Info header */}
      <div className="bg-muted/50 rounded-lg p-4">
        <h3 className="font-semibold mb-2">Organiza tus documentos por categoría</h3>
        <p className="text-sm text-muted-foreground">
          Sube los documentos en las pestañas correspondientes. Esto ayuda a la IA a
          identificar mejor la información.
        </p>
      </div>

      {/* Tabs for categories */}
      <Tabs defaultValue={categories[0]?.name} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {categories.map((category) => {
            const count = files[category.name]?.length || 0;
            return (
              <TabsTrigger key={category.name} value={category.name} className="gap-2">
                <span>{category.icon}</span>
                <span>{category.name}</span>
                {count > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                    {count}
                  </span>
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

                // Show success or errors
                if (result.errors.length > 0) {
                  result.errors.forEach((error) => {
                    toast.error(error);
                  });
                } else if (result.validFiles.length > 0) {
                  toast.success(
                    `${result.validFiles.length} ${
                      result.validFiles.length === 1 ? 'archivo agregado' : 'archivos agregados'
                    } a ${category.name}`
                  );
                }
              }}
              onFileRemove={(fileId) => removeFile(category.name, fileId)}
              onClearAll={() => clearCategory(category.name)}
            />
          </TabsContent>
        ))}
      </Tabs>

      {/* Summary */}
      {getTotalFilesCount() > 0 && (
        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
          <p className="text-sm font-medium">
            Total: {getTotalFilesCount()}{' '}
            {getTotalFilesCount() === 1 ? 'archivo subido' : 'archivos subidos'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Los archivos están listos para ser procesados
          </p>
        </div>
      )}
    </div>
  );
}
