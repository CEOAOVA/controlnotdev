/**
 * DocumentPreviewModal Component
 * Modal to preview document details before downloading
 */

import { useState } from 'react';
import { format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { TypeBadge } from '@/components/template/TypeBadge';
import {
  Download,
  Mail,
  FileText,
  Calendar,
  User,
  CheckCircle2,
  Clock,
  XCircle,
  Edit,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DocumentType } from '@/store';

export interface DocumentDetails {
  id: string;
  name: string;
  type: DocumentType;
  status: 'completed' | 'processing' | 'error';
  createdAt: string;
  updatedAt?: string;
  createdBy?: string;
  storagePath?: string;
  extractedData?: Record<string, string>;
  metadata?: Record<string, unknown>;
}

interface DocumentPreviewModalProps {
  document: DocumentDetails | null;
  isOpen: boolean;
  onClose: () => void;
  onDownload?: (doc: DocumentDetails) => void;
  onEmail?: (doc: DocumentDetails) => void;
  onReplace?: (doc: DocumentDetails) => void;
}

export function DocumentPreviewModal({
  document,
  isOpen,
  onClose,
  onDownload,
  onEmail,
  onReplace,
}: DocumentPreviewModalProps) {
  const [activeTab, setActiveTab] = useState<'details' | 'data'>('details');

  if (!document) return null;

  const getStatusIcon = (status: DocumentDetails['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-success" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-warning" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-error" />;
    }
  };

  const getStatusLabel = (status: DocumentDetails['status']) => {
    switch (status) {
      case 'completed':
        return 'Completado';
      case 'processing':
        return 'Procesando';
      case 'error':
        return 'Error';
    }
  };

  const getStatusColor = (status: DocumentDetails['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-success/10 text-success-700 border-success/20';
      case 'processing':
        return 'bg-warning/10 text-warning-700 border-warning/20';
      case 'error':
        return 'bg-error/10 text-error-700 border-error/20';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">{document.name}</h2>
              <p className="text-sm text-neutral-500 font-normal">
                ID: {document.id.substring(0, 12)}...
              </p>
            </div>
          </DialogTitle>
        </DialogHeader>

        {/* Tabs */}
        <div className="flex gap-2 mt-4">
          <Button
            variant={activeTab === 'details' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('details')}
          >
            Detalles
          </Button>
          <Button
            variant={activeTab === 'data' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('data')}
          >
            Datos Extraidos
          </Button>
        </div>

        <Separator className="my-4" />

        {/* Content */}
        {activeTab === 'details' && (
          <div className="space-y-4">
            {/* Status and Type */}
            <div className="flex items-center gap-4">
              <TypeBadge type={document.type} />
              <Badge className={cn('gap-1', getStatusColor(document.status))}>
                {getStatusIcon(document.status)}
                {getStatusLabel(document.status)}
              </Badge>
            </div>

            {/* Info Grid */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-neutral-400" />
                <div>
                  <p className="text-xs text-neutral-500">Creado</p>
                  <p className="text-sm font-medium">
                    {format(new Date(document.createdAt), 'dd/MM/yyyy HH:mm')}
                  </p>
                </div>
              </div>

              {document.updatedAt && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-neutral-400" />
                  <div>
                    <p className="text-xs text-neutral-500">Actualizado</p>
                    <p className="text-sm font-medium">
                      {format(new Date(document.updatedAt), 'dd/MM/yyyy HH:mm')}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-neutral-400" />
                <div>
                  <p className="text-xs text-neutral-500">Creado por</p>
                  <p className="text-sm font-medium">{document.createdBy || 'Sistema'}</p>
                </div>
              </div>

              {document.storagePath && (
                <div className="flex items-center gap-2">
                  <ExternalLink className="w-4 h-4 text-neutral-400" />
                  <div>
                    <p className="text-xs text-neutral-500">Storage</p>
                    <p className="text-sm font-medium truncate max-w-[150px]">
                      {document.storagePath.split('/').pop()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'data' && (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {document.extractedData && Object.keys(document.extractedData).length > 0 ? (
              <div className="grid gap-2">
                {Object.entries(document.extractedData).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex justify-between items-start p-3 bg-neutral-50 rounded-lg"
                  >
                    <span className="text-sm font-medium text-neutral-600 min-w-[140px]">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm text-neutral-900 text-right flex-1">
                      {value || <span className="text-neutral-400 italic">No disponible</span>}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-neutral-500">
                No hay datos extraidos disponibles
              </div>
            )}
          </div>
        )}

        <DialogFooter className="mt-6">
          <div className="flex items-center gap-2 w-full justify-between">
            <Button variant="outline" onClick={onClose}>
              Cerrar
            </Button>

            <div className="flex items-center gap-2">
              {onReplace && document.status === 'completed' && (
                <Button
                  variant="outline"
                  onClick={() => onReplace(document)}
                  className="gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Reemplazar
                </Button>
              )}

              {onEmail && document.status === 'completed' && (
                <Button
                  variant="outline"
                  onClick={() => onEmail(document)}
                  className="gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Enviar
                </Button>
              )}

              {onDownload && document.status === 'completed' && (
                <Button onClick={() => onDownload(document)} className="gap-2">
                  <Download className="w-4 h-4" />
                  Descargar
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
