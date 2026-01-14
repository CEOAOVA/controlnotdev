/**
 * DownloadButton Component
 * Button to generate and download the final Word document
 */

import { useState } from 'react';
import { Download, Loader2, FileText, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useProcessDocument } from '@/hooks';
import { useDocumentStore, useTemplateStore } from '@/store';
import { downloadBlob } from '@/lib/utils';
import { documentsApi } from '@/api/endpoints/documents';

interface DownloadButtonProps {
  onSuccess?: (filename: string) => void;
}

export function DownloadButton({ onSuccess }: DownloadButtonProps) {
  const [downloadStatus, setDownloadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { generateDocument, isGenerating } = useProcessDocument();
  const { editedData, documentType } = useDocumentStore();
  const { selectedTemplate } = useTemplateStore();

  const handleDownload = async () => {
    if (!editedData || !documentType) {
      setErrorMessage('No hay datos para generar documento');
      setDownloadStatus('error');
      return;
    }

    try {
      setDownloadStatus('idle');
      setErrorMessage(null);

      const templateId = selectedTemplate?.id || selectedTemplate?.name || 'default';
      const result = await generateDocument(templateId);

      if (result?.success && result.document_id) {
        // Download the blob using document_id (uses correct endpoint /documents/download/{doc_id})
        const blob = await documentsApi.downloadByDocId(result.document_id);

        // Use filename from response or generate one
        const filename = result.filename || `documento_${documentType}_${new Date().toISOString().split('T')[0]}.docx`;

        // Download the file
        downloadBlob(blob, filename);

        setDownloadStatus('success');
        if (onSuccess) {
          onSuccess(filename);
        }

        // Reset status after 3 seconds
        setTimeout(() => setDownloadStatus('idle'), 3000);
      } else if (result && !result.success) {
        throw new Error(result.message || 'Error al generar documento');
      }
    } catch (error: any) {
      console.error('Error generating document:', error);
      setErrorMessage(error?.message || 'Error al generar documento');
      setDownloadStatus('error');
    }
  };

  return (
    <div className="space-y-4">
      <Button
        onClick={handleDownload}
        disabled={isGenerating || !editedData}
        size="lg"
        className="w-full gap-2"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generando documento...
          </>
        ) : downloadStatus === 'success' ? (
          <>
            <CheckCircle2 className="w-5 h-5" />
            Descargado exitosamente
          </>
        ) : (
          <>
            <Download className="w-5 h-5" />
            Descargar Documento Word
          </>
        )}
      </Button>

      {downloadStatus === 'success' && (
        <Alert className="border-green-500/50 bg-green-500/10">
          <FileText className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            El documento se ha descargado correctamente.
          </AlertDescription>
        </Alert>
      )}

      {downloadStatus === 'error' && errorMessage && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {!editedData && (
        <Alert>
          <AlertDescription>
            Primero debes procesar un documento y editar los datos.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
