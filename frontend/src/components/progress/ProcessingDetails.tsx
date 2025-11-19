/**
 * ProcessingDetails Component
 * Shows processing status, progress bar, and statistics during OCR/AI extraction
 */

import { Loader2, FileText, Brain, CheckCircle2, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { useDocumentStore } from '@/store';

interface ProcessingDetailsProps {
  imageCount?: number;
  fieldsExtracted?: number;
  totalFields?: number;
}

export function ProcessingDetails({
  imageCount = 0,
  fieldsExtracted = 0,
  totalFields = 0,
}: ProcessingDetailsProps) {
  const { isProcessing, processingStep, error, confidence } = useDocumentStore();

  const progressPercentage = totalFields > 0 ? (fieldsExtracted / totalFields) * 100 : 0;

  const stepMessages = {
    idle: 'Esperando...',
    ocr: 'Procesando imágenes con OCR',
    ai: 'Extrayendo datos con IA',
    complete: 'Procesamiento completado',
  };

  const stepIcons = {
    idle: FileText,
    ocr: FileText,
    ai: Brain,
    complete: CheckCircle2,
  };

  const Icon = stepIcons[processingStep];

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error de procesamiento</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!isProcessing && processingStep === 'idle') {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Main status card */}
      <div className="bg-muted/50 rounded-lg p-6 space-y-4">
        {/* Status header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isProcessing ? (
              <Loader2 className="w-6 h-6 text-primary animate-spin" />
            ) : (
              <Icon className={cn('w-6 h-6', processingStep === 'complete' && 'text-green-600')} />
            )}
            <div>
              <h3 className="font-semibold">{stepMessages[processingStep]}</h3>
              <p className="text-sm text-muted-foreground">
                {isProcessing ? 'Por favor espera...' : 'Listo para continuar'}
              </p>
            </div>
          </div>

          {processingStep !== 'idle' && (
            <Badge
              variant={processingStep === 'complete' ? 'default' : 'secondary'}
              className={cn(
                processingStep === 'complete' && 'bg-green-500 hover:bg-green-600'
              )}
            >
              {processingStep === 'complete' ? 'Completo' : 'En progreso'}
            </Badge>
          )}
        </div>

        {/* Progress bar */}
        {isProcessing && (
          <Progress
            value={processingStep === 'ocr' ? 50 : processingStep === 'ai' ? 75 : 100}
            className="h-2"
          />
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
          {imageCount > 0 && (
            <div className="text-center p-3 bg-background rounded-lg border">
              <p className="text-2xl font-bold text-primary">{imageCount}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {imageCount === 1 ? 'Imagen' : 'Imágenes'}
              </p>
            </div>
          )}

          {fieldsExtracted > 0 && (
            <div className="text-center p-3 bg-background rounded-lg border">
              <p className="text-2xl font-bold text-primary">
                {fieldsExtracted}
                {totalFields > 0 && `/${totalFields}`}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Campos extraídos</p>
            </div>
          )}

          {progressPercentage > 0 && (
            <div className="text-center p-3 bg-background rounded-lg border">
              <p className="text-2xl font-bold text-primary">
                {Math.round(progressPercentage)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">Completitud</p>
            </div>
          )}

          {confidence !== null && confidence > 0 && (
            <div className="text-center p-3 bg-background rounded-lg border">
              <p
                className={cn(
                  'text-2xl font-bold',
                  confidence >= 80 && 'text-green-600',
                  confidence >= 60 && confidence < 80 && 'text-yellow-600',
                  confidence < 60 && 'text-orange-600'
                )}
              >
                {Math.round(confidence)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">Confianza IA</p>
            </div>
          )}
        </div>

        {/* Confidence warning */}
        {confidence !== null && confidence < 70 && processingStep === 'complete' && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              La confianza de la extracción es baja ({Math.round(confidence)}%).
              Revisa cuidadosamente los datos extraídos.
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}
