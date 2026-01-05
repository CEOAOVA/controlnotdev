/**
 * DocumentPreview Component
 * Shows HTML preview of the document with data filled in
 * Displays completion statistics and warnings
 */

import { useState, useEffect } from 'react';
import { Eye, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { documentsApi } from '@/api/endpoints/documents';
import type { DocumentPreviewResponse } from '@/api/types/documents-types';

interface DocumentPreviewProps {
  templateId: string;
  data: Record<string, string>;
  sessionId?: string;
  onApprove: () => void;
  onEdit: () => void;
}

export function DocumentPreview({
  templateId,
  data,
  sessionId,
  onApprove,
  onEdit,
}: DocumentPreviewProps) {
  const [preview, setPreview] = useState<DocumentPreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPreview = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await documentsApi.preview({
          template_id: templateId,
          data,
          session_id: sessionId,
        });
        setPreview(response);
      } catch (err) {
        console.error('Error fetching preview:', err);
        setError('No se pudo cargar la vista previa del documento');
      } finally {
        setLoading(false);
      }
    };

    if (templateId && Object.keys(data).length > 0) {
      fetchPreview();
    }
  }, [templateId, data, sessionId]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Generando vista previa...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!preview) {
    return null;
  }

  const completionColor =
    preview.fill_percentage >= 90
      ? 'text-green-600'
      : preview.fill_percentage >= 70
        ? 'text-yellow-600'
        : 'text-red-600';

  return (
    <div className="space-y-6">
      {/* Statistics Header */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Vista Previa del Documento
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Campos completados</span>
              <span className={completionColor}>
                {preview.filled_placeholders} de {preview.total_placeholders} (
                {preview.fill_percentage.toFixed(1)}%)
              </span>
            </div>
            <Progress value={preview.fill_percentage} className="h-2" />
          </div>

          {/* Stats Badges */}
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary" className="gap-1">
              <CheckCircle className="w-3 h-3 text-green-500" />
              {preview.filled_placeholders} completados
            </Badge>
            {preview.missing_placeholders.length > 0 && (
              <Badge variant="destructive" className="gap-1">
                <XCircle className="w-3 h-3" />
                {preview.missing_placeholders.length} faltantes
              </Badge>
            )}
            {preview.warnings.length > 0 && (
              <Badge variant="outline" className="gap-1 text-yellow-600 border-yellow-600">
                <AlertTriangle className="w-3 h-3" />
                {preview.warnings.length} advertencias
              </Badge>
            )}
          </div>

          {/* Warnings */}
          {preview.warnings.length > 0 && (
            <Alert className="border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertTitle className="text-yellow-800">Advertencias</AlertTitle>
              <AlertDescription>
                <ul className="list-disc list-inside text-sm text-yellow-700 mt-2">
                  {preview.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* Missing Placeholders */}
          {preview.missing_placeholders.length > 0 && (
            <Alert className="border-red-200 bg-red-50">
              <XCircle className="h-4 w-4 text-red-600" />
              <AlertTitle className="text-red-800">Campos sin completar</AlertTitle>
              <AlertDescription>
                <div className="flex flex-wrap gap-1 mt-2">
                  {preview.missing_placeholders.slice(0, 10).map((placeholder) => (
                    <Badge key={placeholder} variant="outline" className="text-xs">
                      {placeholder.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                  {preview.missing_placeholders.length > 10 && (
                    <Badge variant="outline" className="text-xs">
                      +{preview.missing_placeholders.length - 10} mas
                    </Badge>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Document Preview */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Documento</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[60vh] sm:h-[400px] w-full rounded-md border p-2 sm:p-4 bg-white">
            <div
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: preview.html_content }}
            />
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between gap-4 p-4 bg-muted/30 rounded-lg">
        <Button variant="outline" onClick={onEdit} className="gap-2">
          Volver a Editar
        </Button>

        <div className="flex gap-2">
          {preview.fill_percentage < 100 && (
            <p className="text-sm text-muted-foreground self-center mr-2">
              Algunos campos estan incompletos
            </p>
          )}
          <Button
            onClick={onApprove}
            className="gap-2"
            variant={preview.fill_percentage >= 90 ? 'default' : 'secondary'}
          >
            <CheckCircle className="w-4 h-4" />
            {preview.fill_percentage >= 90 ? 'Aprobar y Generar' : 'Generar de todos modos'}
          </Button>
        </div>
      </div>
    </div>
  );
}
