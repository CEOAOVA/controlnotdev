/**
 * PreviewModal Component
 * Modal to preview final document data before generation
 */

import { Eye } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { TypeBadge } from '@/components/template/TypeBadge';
import { useDocumentStore } from '@/store';

interface PreviewModalProps {
  onEdit?: () => void;
  onApprove?: () => void;
  showApproveButton?: boolean;
}

export function PreviewModal({ onEdit, onApprove, showApproveButton = false }: PreviewModalProps) {
  const { editedData, documentType, setPreviewApproved } = useDocumentStore();

  const handleApprove = () => {
    setPreviewApproved(true);
    if (onApprove) {
      onApprove();
    }
  };

  if (!editedData || !documentType) {
    return null;
  }

  // Group data by category (simplified)
  const categories = {
    'Datos Generales': [
      'Numero_Escritura',
      'Fecha_Firma',
      'Notaria_Numero',
      'Nombre_Notario',
      'Ciudad_Notaria',
    ],
    'Parte Vendedora': Object.keys(editedData).filter((k) =>
      k.startsWith('Parte_Vendedora')
    ),
    'Parte Compradora': Object.keys(editedData).filter((k) =>
      k.startsWith('Parte_Compradora')
    ),
    Inmueble: Object.keys(editedData).filter((k) => k.startsWith('Inmueble')),
  };

  // Format field name for display
  const formatFieldName = (name: string): string => {
    return name.replace(/_/g, ' ').replace(/Parte (Vendedora|Compradora) /, '');
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Eye className="w-4 h-4" />
          Vista Previa
        </Button>
      </DialogTrigger>

      <DialogContent className="w-full h-[100dvh] sm:w-auto sm:h-auto sm:max-w-4xl sm:max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 sm:gap-3 text-base sm:text-lg">
            Vista Previa del Documento
            <TypeBadge type={documentType} size="sm" />
          </DialogTitle>
          <DialogDescription className="text-xs sm:text-sm">
            Revisa los datos que se incluirán en el documento final
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 h-[70vh] sm:h-[500px] pr-4">
          <div className="space-y-6">
            {Object.entries(categories).map(([category, fields]) => {
              // Filter only fields that have values
              const filledFields = fields.filter((field) => {
                const value = editedData[field];
                return value !== null && value !== undefined && value !== '';
              });

              if (filledFields.length === 0) return null;

              return (
                <div key={category} className="space-y-3">
                  <div className="flex items-center gap-2 pb-2 border-b">
                    <h3 className="font-semibold">{category}</h3>
                    <Badge variant="secondary">{filledFields.length} campos</Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filledFields.map((field) => {
                      const value = editedData[field];
                      return (
                        <div key={field} className="space-y-1">
                          <p className="text-sm font-medium text-muted-foreground">
                            {formatFieldName(field)}
                          </p>
                          <p className="text-sm">{value?.toString() || '-'}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>

        <div className="pt-4 border-t space-y-3">
          {showApproveButton && (
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <p className="text-sm text-primary-900 font-medium mb-3">
                ⚠️ <strong>Revisar antes de generar</strong>
              </p>
              <p className="text-xs text-primary-700 mb-4">
                Verifica que todos los datos sean correctos. Una vez aprobado, se generará el documento final.
              </p>
              <Button
                onClick={handleApprove}
                className="w-full bg-primary-500 hover:bg-primary-600 text-white"
              >
                ✓ Aprobar y Continuar
              </Button>
            </div>
          )}

          {onEdit && (
            <Button onClick={onEdit} variant="outline" className="w-full">
              ← Editar Datos
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
