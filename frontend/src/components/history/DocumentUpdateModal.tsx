/**
 * DocumentUpdateModal Component
 * Modal to replace/update an existing document with a new file
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  FileText,
  X,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface DocumentToUpdate {
  id: string;
  name: string;
}

interface DocumentUpdateModalProps {
  document: DocumentToUpdate | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (documentId: string, file: File) => Promise<void>;
}

export function DocumentUpdateModal({
  document,
  isOpen,
  onClose,
  onUpdate,
}: DocumentUpdateModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.docx')) {
        setError('Solo se permiten archivos .docx');
        return;
      }

      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('El archivo es muy grande. Maximo 10MB.');
        return;
      }

      setSelectedFile(file);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  const handleUpdate = async () => {
    if (!document || !selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      await onUpdate(document.id, selectedFile);
      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar documento');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (isUploading) return;
    setSelectedFile(null);
    setError(null);
    setSuccess(false);
    onClose();
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!document) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Reemplazar Documento
          </DialogTitle>
          <DialogDescription>
            Sube un nuevo archivo .docx para reemplazar{' '}
            <span className="font-medium">{document.name}</span>
          </DialogDescription>
        </DialogHeader>

        {/* Success State */}
        {success && (
          <div className="py-8 text-center space-y-3">
            <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-neutral-900">
                Documento Actualizado
              </h3>
              <p className="text-neutral-600">
                El documento ha sido reemplazado exitosamente
              </p>
            </div>
          </div>
        )}

        {/* Upload State */}
        {!success && (
          <>
            {/* Error Alert */}
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Dropzone */}
            {!selectedFile && (
              <div
                {...getRootProps()}
                className={cn(
                  'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
                  isDragActive
                    ? 'border-primary bg-primary-50'
                    : 'border-neutral-300 hover:border-primary hover:bg-neutral-50',
                  isUploading && 'opacity-50 cursor-not-allowed'
                )}
              >
                <input {...getInputProps()} />
                <Upload className="w-10 h-10 text-neutral-400 mx-auto mb-3" />
                {isDragActive ? (
                  <p className="text-primary font-medium">Suelta el archivo aqui</p>
                ) : (
                  <>
                    <p className="text-neutral-600 font-medium">
                      Arrastra un archivo .docx aqui
                    </p>
                    <p className="text-sm text-neutral-500 mt-1">
                      o haz clic para seleccionar
                    </p>
                  </>
                )}
              </div>
            )}

            {/* Selected File */}
            {selectedFile && (
              <div className="border rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-neutral-900 truncate">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-neutral-500">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  {!isUploading && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={removeFile}
                      className="h-8 w-8"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>
            )}

            {/* Warning */}
            <Alert className="bg-warning-50 border-warning-200">
              <AlertTriangle className="w-4 h-4 text-warning-600" />
              <AlertDescription className="text-warning-800">
                Esta accion reemplazara el documento actual. El documento anterior
                no se podra recuperar.
              </AlertDescription>
            </Alert>
          </>
        )}

        <DialogFooter className="mt-4">
          {!success && (
            <>
              <Button variant="outline" onClick={handleClose} disabled={isUploading}>
                Cancelar
              </Button>
              <Button
                onClick={handleUpdate}
                disabled={!selectedFile || isUploading}
                className="gap-2"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Actualizando...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Reemplazar
                  </>
                )}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
