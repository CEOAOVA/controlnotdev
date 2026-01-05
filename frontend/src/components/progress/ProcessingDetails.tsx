/**
 * ProcessingDetails Component
 * Shows processing status, progress bar, and statistics during OCR/AI extraction
 */

import { Loader2, FileText, Brain, CheckCircle2, AlertCircle, Eye, Shield, Zap, Sun } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { useDocumentStore } from '@/store';
import type { QualityLevel } from '@/api/types';

interface ProcessingDetailsProps {
  imageCount?: number;
  fieldsExtracted?: number;
  totalFields?: number;
}

// Helper function to get color based on score
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 40) return 'text-orange-600';
  return 'text-red-600';
}

// Helper function to get quality level badge variant
function getQualityBadgeVariant(level: QualityLevel): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (level) {
    case 'high': return 'default';
    case 'medium': return 'secondary';
    case 'low': return 'destructive';
    case 'reject': return 'destructive';
    default: return 'outline';
  }
}

// Helper function to get quality level label
function getQualityLabel(level: QualityLevel): string {
  switch (level) {
    case 'high': return 'Alta';
    case 'medium': return 'Media';
    case 'low': return 'Baja';
    case 'reject': return 'Rechazada';
    default: return level;
  }
}

export function ProcessingDetails({
  imageCount = 0,
  fieldsExtracted = 0,
  totalFields = 0,
}: ProcessingDetailsProps) {
  const {
    isProcessing,
    processingStep,
    error,
    confidence,
    qualityReport,
    validationReport,
  } = useDocumentStore();

  const progressPercentage = totalFields > 0 ? (fieldsExtracted / totalFields) * 100 : 0;

  type ProcessingStepType = 'idle' | 'ocr' | 'ai' | 'complete';

  const stepMessages: Record<ProcessingStepType, string> = {
    idle: 'Esperando...',
    ocr: 'Procesando imágenes con OCR',
    ai: 'Extrayendo datos con IA',
    complete: 'Procesamiento completado',
  };

  const stepIcons: Record<ProcessingStepType, typeof FileText> = {
    idle: FileText,
    ocr: FileText,
    ai: Brain,
    complete: CheckCircle2,
  };

  const currentStep = processingStep as ProcessingStepType;
  const Icon = stepIcons[currentStep];

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error de procesamiento</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!isProcessing && currentStep === 'idle') {
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
              <Icon className={cn('w-6 h-6', currentStep === 'complete' && 'text-green-600')} />
            )}
            <div>
              <h3 className="font-semibold">{stepMessages[currentStep]}</h3>
              <p className="text-sm text-muted-foreground">
                {isProcessing ? 'Por favor espera...' : 'Listo para continuar'}
              </p>
            </div>
          </div>

          {currentStep !== 'idle' && (
            <Badge
              variant={currentStep === 'complete' ? 'default' : 'secondary'}
              className={cn(
                currentStep === 'complete' && 'bg-green-500 hover:bg-green-600'
              )}
            >
              {currentStep === 'complete' ? 'Completo' : 'En progreso'}
            </Badge>
          )}
        </div>

        {/* Progress bar */}
        {isProcessing && (
          <Progress
            value={currentStep === 'ocr' ? 50 : currentStep === 'ai' ? 75 : 100}
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
        {confidence !== null && confidence < 70 && currentStep === 'complete' && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              La confianza de la extracción es baja ({Math.round(confidence)}%).
              Revisa cuidadosamente los datos extraídos.
            </AlertDescription>
          </Alert>
        )}

        {/* Quality Report - OCR Robusto 2025 */}
        {qualityReport && currentStep === 'complete' && (
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <Eye className="w-4 h-4" />
                Calidad del Documento
              </h4>
              <Badge variant={getQualityBadgeVariant(qualityReport.overall_level)}>
                {getQualityLabel(qualityReport.overall_level)}
              </Badge>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="text-center p-2 bg-background rounded border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Zap className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Nitidez</span>
                </div>
                <p className={cn('text-lg font-semibold', getScoreColor(qualityReport.blur_score))}>
                  {Math.round(qualityReport.blur_score)}
                </p>
              </div>
              <div className="text-center p-2 bg-background rounded border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Eye className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Contraste</span>
                </div>
                <p className={cn('text-lg font-semibold', getScoreColor(qualityReport.contrast_score))}>
                  {Math.round(qualityReport.contrast_score)}
                </p>
              </div>
              <div className="text-center p-2 bg-background rounded border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Sun className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Brillo</span>
                </div>
                <p className={cn('text-lg font-semibold', getScoreColor(qualityReport.brightness_score))}>
                  {Math.round(qualityReport.brightness_score)}
                </p>
              </div>
              <div className="text-center p-2 bg-background rounded border">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <FileText className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Resolución</span>
                </div>
                <p className={cn('text-lg font-semibold', getScoreColor(qualityReport.resolution_score))}>
                  {Math.round(qualityReport.resolution_score)}
                </p>
              </div>
            </div>
            {qualityReport.recommendations && qualityReport.recommendations.length > 0 && (
              <div className="mt-3">
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <ul className="text-sm list-disc list-inside">
                      {qualityReport.recommendations.map((rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              </div>
            )}
          </div>
        )}

        {/* Validation Report - OCR Robusto 2025 */}
        {validationReport && currentStep === 'complete' && (
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Validación de Datos
              </h4>
              <Badge variant={validationReport.overall_confidence >= 0.8 ? 'default' : 'secondary'}>
                {Math.round(validationReport.overall_confidence * 100)}% confianza
              </Badge>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-2 bg-green-50 dark:bg-green-950 rounded border border-green-200 dark:border-green-800">
                <p className="text-lg font-semibold text-green-600">{validationReport.valid_fields}</p>
                <p className="text-xs text-green-600/80">Válidos</p>
              </div>
              <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-950 rounded border border-yellow-200 dark:border-yellow-800">
                <p className="text-lg font-semibold text-yellow-600">{validationReport.suspicious_fields}</p>
                <p className="text-xs text-yellow-600/80">Sospechosos</p>
              </div>
              <div className="text-center p-2 bg-red-50 dark:bg-red-950 rounded border border-red-200 dark:border-red-800">
                <p className="text-lg font-semibold text-red-600">{validationReport.invalid_fields}</p>
                <p className="text-xs text-red-600/80">Inválidos</p>
              </div>
            </div>
            {(validationReport.suspicious_fields > 0 || validationReport.invalid_fields > 0) && (
              <Alert className="mt-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Se detectaron {validationReport.suspicious_fields + validationReport.invalid_fields} campos
                  que requieren revisión manual. Revisa los campos marcados en amarillo/rojo.
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
