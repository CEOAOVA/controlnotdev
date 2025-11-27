/**
 * CategoryTab Component
 * Single tab for a document category with file upload
 */

import { FileUp, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DropZone } from './DropZone';
import { ImagePreview } from './ImagePreview';
import { RequiredDocsList } from './RequiredDocsList';
import { useDocumentStore } from '@/store';
import type { CategoryName, UploadedFile } from '@/store';

interface CategoryTabProps {
  category: {
    name: CategoryName;
    description: string;
    icon?: string;
  };
  files: UploadedFile[];
  onFilesAdded: (files: File[]) => void;
  onFileRemove: (fileId: string) => void;
  onClearAll?: () => void;
}

export function CategoryTab({
  category,
  files,
  onFilesAdded,
  onFileRemove,
  onClearAll,
}: CategoryTabProps) {
  const fileCount = files.length;
  const { documentType } = useDocumentStore();

  // Map CategoryName to RequiredDocsList category prop
  const getRequiredDocsCategory = (categoryName: CategoryName): 'parte_a' | 'parte_b' | 'otros' => {
    if (categoryName === 'Parte A') return 'parte_a';
    if (categoryName === 'Parte B') return 'parte_b';
    return 'otros';
  };

  return (
    <div className="space-y-4">
      {/* Category header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{category.icon || '📁'}</span>
          <div>
            <h3 className="font-semibold">{category.name}</h3>
            <p className="text-sm text-muted-foreground">
              {category.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="secondary">
            {fileCount} {fileCount === 1 ? 'archivo' : 'archivos'}
          </Badge>

          {fileCount > 0 && onClearAll && (
            <Button
              variant="outline"
              size="sm"
              onClick={onClearAll}
              className="gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Limpiar
            </Button>
          )}
        </div>
      </div>

      {/* Required documents list */}
      {documentType && (
        <RequiredDocsList
          documentType={documentType}
          category={getRequiredDocsCategory(category.name)}
        />
      )}

      {/* Drop zone */}
      <DropZone onFilesAdded={onFilesAdded} />

      {/* File previews */}
      {fileCount > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">
              Archivos subidos ({fileCount})
            </h4>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {files.map((uploadedFile) => (
              <ImagePreview
                key={uploadedFile.id}
                uploadedFile={uploadedFile}
                onRemove={() => onFileRemove(uploadedFile.id)}
              />
            ))}
          </div>
        </div>
      )}

      {fileCount === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <FileUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No hay archivos en esta categoría</p>
          <p className="text-xs mt-1">
            Arrastra archivos o haz click en el área de arriba
          </p>
        </div>
      )}
    </div>
  );
}
