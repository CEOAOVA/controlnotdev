/**
 * ProcessPage Component
 * Main page orchestrating the document processing workflow
 * States: Upload → Edit → Complete
 */

import { useState, useEffect } from 'react';
import { ArrowRight, ArrowLeft, PlayCircle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card } from '@/components/ui/card';

// Layout
import { MainLayout } from '@/components/layout/MainLayout';

// Progress
import { ProgressIndicator, type ProcessStep } from '@/components/progress/ProgressIndicator';
import { ProcessingDetails } from '@/components/progress/ProcessingDetails';

// Upload components
import { UnifiedUploader } from '@/components/upload/UnifiedUploader';

// Editor components
import { DataEditor } from '@/components/editor/DataEditor';

// Document components
import { PreviewModal } from '@/components/document/PreviewModal';
import { DocumentPreview } from '@/components/document/DocumentPreview';
import { DownloadButton } from '@/components/document/DownloadButton';
import { EmailForm } from '@/components/document/EmailForm';

// Hooks and stores
import { useProcessDocument, useCategories } from '@/hooks';
import { useDocumentStore, useTemplateStore, useCategoryStore } from '@/store';

export function ProcessPage() {
  const [currentStep, setCurrentStep] = useState<ProcessStep>('upload');
  const [filesCount, setFilesCount] = useState(0);
  const [hasTemplate, setHasTemplate] = useState(false);
  const [generatedFilename, setGeneratedFilename] = useState<string | null>(null);
  const [generatedDocumentId, setGeneratedDocumentId] = useState<string | null>(null);

  // Hooks
  const { processFullWorkflow, isProcessing } = useProcessDocument();
  const { getTotalFilesCount, areAllCategoriesPopulated } = useCategories();

  // Stores
  const { extractedData, editedData, reset, processingStep } = useDocumentStore();
  const { selectedTemplate } = useTemplateStore();
  const { clearAll } = useCategoryStore();

  // Update states
  useEffect(() => {
    setFilesCount(getTotalFilesCount());
  }, [getTotalFilesCount]);

  useEffect(() => {
    setHasTemplate(!!selectedTemplate);
  }, [selectedTemplate]);

  // Auto-advance to edit step after processing completes
  useEffect(() => {
    if (processingStep === 'complete' && extractedData) {
      setCurrentStep('edit');
    }
  }, [processingStep, extractedData]);

  // Check if can proceed to next step
  const canProceedFromUpload = hasTemplate && filesCount > 0 && areAllCategoriesPopulated();

  // STRICT VALIDATION: All fields must be filled before proceeding
  const canProceedFromEdit = editedData && Object.values(editedData).every(value => {
    // Check that value exists and is not empty string
    if (value === null || value === undefined) return false;
    if (typeof value === 'string' && value.trim() === '') return false;
    if (typeof value === 'string' && value === 'No encontrado') return false;
    return true;
  });

  // Handle step changes
  const goToStep = (step: ProcessStep) => {
    // Proteger navegación desde "complete": solo permitir ir a "preview" o "edit"
    if (currentStep === 'complete') {
      if (step === 'upload') {
        // No permitir volver a upload desde complete (requiere reset explícito)
        return;
      }
    }
    // Proteger navegación desde "preview": no permitir saltar a upload
    if (currentStep === 'preview' && step === 'upload') {
      return;
    }
    setCurrentStep(step);
  };

  const goToNextStep = () => {
    if (currentStep === 'upload') {
      setCurrentStep('edit');
    } else if (currentStep === 'edit') {
      setCurrentStep('preview');
    } else if (currentStep === 'preview') {
      setCurrentStep('complete');
    }
  };

  const goToPreviousStep = () => {
    if (currentStep === 'complete') {
      setCurrentStep('preview');
    } else if (currentStep === 'preview') {
      setCurrentStep('edit');
    } else if (currentStep === 'edit') {
      setCurrentStep('upload');
    }
  };

  // Handle processing
  const handleStartProcessing = async () => {
    try {
      await processFullWorkflow();
    } catch (error) {
      console.error('Processing error:', error);
    }
  };

  // Handle reset
  const handleReset = () => {
    if (confirm('¿Estás seguro de que quieres reiniciar? Se perderán todos los datos.')) {
      reset();
      clearAll();
      setCurrentStep('upload');
      setGeneratedFilename(null);
      setGeneratedDocumentId(null);
    }
  };

  // Handle download success
  const handleDownloadSuccess = (filename: string) => {
    setGeneratedFilename(filename);
    // Generate a document ID from the filename (timestamp-based)
    const docId = `doc_${Date.now()}`;
    setGeneratedDocumentId(docId);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Progress indicator */}
        <ProgressIndicator
          currentStep={currentStep}
          onStepClick={goToStep}
          completedSteps={
            extractedData
              ? ([
                  'upload',
                  ...(currentStep === 'preview' || currentStep === 'complete' ? ['edit'] : []),
                  ...(currentStep === 'complete' ? ['preview'] : []),
                ] as ProcessStep[])
              : ([] as ProcessStep[])
          }
        />

        {/* Main content based on current step */}
        <div className="space-y-6">
          {/* STEP 1: UPLOAD */}
          {currentStep === 'upload' && (
            <>
              <UnifiedUploader
                onTemplateSelected={setHasTemplate}
                onFilesChange={setFilesCount}
              />

              {/* Actions */}
              <div className="flex items-center justify-between p-6 bg-muted/30 rounded-lg">
                <div className="flex-1">
                  {!hasTemplate && (
                    <Alert>
                      <AlertDescription>
                        Selecciona un template para continuar
                      </AlertDescription>
                    </Alert>
                  )}
                  {hasTemplate && filesCount === 0 && (
                    <Alert>
                      <AlertDescription>
                        Sube archivos en al menos una categoría
                      </AlertDescription>
                    </Alert>
                  )}
                  {hasTemplate && filesCount > 0 && !areAllCategoriesPopulated() && (
                    <Alert>
                      <AlertDescription>
                        Asegúrate de subir archivos en todas las categorías
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                <Button
                  size="lg"
                  onClick={handleStartProcessing}
                  disabled={!canProceedFromUpload || isProcessing}
                  className="gap-2 ml-4"
                >
                  {isProcessing ? (
                    'Procesando...'
                  ) : (
                    <>
                      <PlayCircle className="w-5 h-5" />
                      Procesar Documentos
                    </>
                  )}
                </Button>
              </div>

              {/* Processing details */}
              {isProcessing && (
                <ProcessingDetails
                  imageCount={filesCount}
                  fieldsExtracted={0}
                  totalFields={0}
                />
              )}
            </>
          )}

          {/* STEP 2: EDIT */}
          {currentStep === 'edit' && (
            <>
              <Card className="p-6">
                <DataEditor />
              </Card>

              {/* Actions */}
              <div className="flex items-center justify-between p-6 bg-muted/30 rounded-lg">
                <Button
                  variant="outline"
                  onClick={goToPreviousStep}
                  className="gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Volver
                </Button>

                <Button
                  size="lg"
                  onClick={goToNextStep}
                  disabled={!canProceedFromEdit}
                  className="gap-2"
                >
                  Continuar
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </>
          )}

          {/* STEP 3: PREVIEW */}
          {currentStep === 'preview' && selectedTemplate && editedData && (
            <DocumentPreview
              templateId={selectedTemplate.id}
              data={editedData as Record<string, string>}
              onApprove={goToNextStep}
              onEdit={goToPreviousStep}
            />
          )}

          {/* STEP 4: COMPLETE */}
          {currentStep === 'complete' && (
            <>
              {/* Preview */}
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Documento Listo</h2>
                <PreviewModal onEdit={() => setCurrentStep('edit')} />
              </div>

              {/* Download section */}
              <Card className="p-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">Descargar Documento</h3>
                    <p className="text-sm text-muted-foreground">
                      Descarga el documento Word con todos los datos completados
                    </p>
                  </div>

                  <DownloadButton onSuccess={handleDownloadSuccess} />
                </div>
              </Card>

              {/* Email section */}
              {generatedFilename && generatedDocumentId && (
                <Card className="p-6">
                  <EmailForm documentId={generatedDocumentId} documentName={generatedFilename} />
                </Card>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between p-6 bg-muted/30 rounded-lg">
                <Button
                  variant="outline"
                  onClick={goToPreviousStep}
                  className="gap-2"
                >
                  <ArrowLeft className="w-4 w-4" />
                  Volver a editar
                </Button>

                <Button
                  variant="outline"
                  onClick={handleReset}
                  className="gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Nuevo Documento
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
