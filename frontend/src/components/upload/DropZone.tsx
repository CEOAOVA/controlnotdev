/**
 * DropZone Component
 * Drag & drop file upload area with validation
 */

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileImage } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropZoneProps {
  onFilesAdded: (files: File[]) => void;
  maxFiles?: number;
  maxSizeMB?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

export function DropZone({
  onFilesAdded,
  maxFiles = 20,
  maxSizeMB = 10,
  // acceptedTypes ahora se define directamente en el objeto accept
  disabled = false,
}: DropZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFilesAdded(acceptedFiles);
    },
    [onFilesAdded]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
    },
    maxFiles,
    maxSize: maxSizeMB * 1024 * 1024,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all',
        'hover:border-primary hover:bg-accent/50',
        isDragActive && 'border-primary bg-accent',
        isDragReject && 'border-destructive bg-destructive/10',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center justify-center gap-4">
        {isDragActive ? (
          <>
            <Upload className="w-12 h-12 text-primary animate-bounce" />
            <p className="text-lg font-medium text-primary">
              Suelta los archivos aquí...
            </p>
          </>
        ) : (
          <>
            <FileImage className="w-12 h-12 text-muted-foreground" />
            <div className="space-y-2">
              <p className="text-lg font-medium">
                Arrastra archivos aquí o haz click para seleccionar
              </p>
              <p className="text-sm text-muted-foreground">
                Formatos: JPG, PNG, PDF (máx. {maxSizeMB}MB cada uno)
              </p>
              <p className="text-xs text-muted-foreground">
                Máximo {maxFiles} archivos
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
