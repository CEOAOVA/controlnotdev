/**
 * DocumentTable Component
 * Table display of document history with actions
 */

import { useState } from 'react';
import { format } from 'date-fns';
import {
  MoreVertical,
  Download,
  Eye,
  Mail,
  FileText,
  CheckCircle2,
  Clock,
  XCircle,
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { TypeBadge } from '@/components/template/TypeBadge';
import { cn } from '@/lib/utils';
import type { DocumentType } from '@/store';

export interface DocumentRecord {
  id: string;
  name: string;
  type: DocumentType;
  status: 'completed' | 'processing' | 'error';
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
  fileUrl?: string;
}

interface DocumentTableProps {
  documents: DocumentRecord[];
  onView?: (doc: DocumentRecord) => void;
  onDownload?: (doc: DocumentRecord) => void;
  onEmail?: (doc: DocumentRecord) => void;
  isLoading?: boolean;
}

export function DocumentTable({
  documents,
  onView,
  onDownload,
  onEmail,
  isLoading = false,
}: DocumentTableProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const getStatusIcon = (status: DocumentRecord['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-success" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-warning" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-error" />;
    }
  };

  const getStatusLabel = (status: DocumentRecord['status']) => {
    switch (status) {
      case 'completed':
        return 'Completado';
      case 'processing':
        return 'Procesando';
      case 'error':
        return 'Error';
    }
  };

  const getStatusColor = (status: DocumentRecord['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-success/10 text-success-700 border-success/20';
      case 'processing':
        return 'bg-warning/10 text-warning-700 border-warning/20';
      case 'error':
        return 'bg-error/10 text-error-700 border-error/20';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <div className="divide-y divide-neutral-200">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-4 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-neutral-200 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-neutral-200 rounded w-1/3" />
                  <div className="h-3 bg-neutral-200 rounded w-1/4" />
                </div>
                <div className="w-20 h-6 bg-neutral-200 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (documents.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
            <FileText className="w-8 h-8 text-neutral-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">
              No hay documentos
            </h3>
            <p className="text-neutral-600 mt-1">
              Los documentos generados aparecerán aquí
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Documento
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Tipo
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Estado
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Fecha
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Creado por
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className={cn(
                  'hover:bg-neutral-50 transition-colors',
                  selectedId === doc.id && 'bg-primary-50'
                )}
                onClick={() => setSelectedId(doc.id)}
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">{doc.name}</p>
                      <p className="text-xs text-neutral-500">{doc.id.substring(0, 8)}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <TypeBadge type={doc.type} size="sm" />
                </td>
                <td className="px-6 py-4">
                  <Badge className={cn('gap-1', getStatusColor(doc.status))}>
                    {getStatusIcon(doc.status)}
                    {getStatusLabel(doc.status)}
                  </Badge>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-neutral-900">
                    {format(new Date(doc.createdAt), 'dd/MM/yyyy')}
                  </div>
                  <div className="text-xs text-neutral-500">
                    {format(new Date(doc.createdAt), 'HH:mm')}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <p className="text-sm text-neutral-700">
                    {doc.createdBy || 'Sistema'}
                  </p>
                </td>
                <td className="px-6 py-4 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {onView && (
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onView(doc);
                          }}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Ver Detalles
                        </DropdownMenuItem>
                      )}
                      {onDownload && doc.status === 'completed' && (
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onDownload(doc);
                          }}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Descargar
                        </DropdownMenuItem>
                      )}
                      {onEmail && doc.status === 'completed' && (
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onEmail(doc);
                          }}
                        >
                          <Mail className="w-4 h-4 mr-2" />
                          Enviar por Email
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile List */}
      <div className="md:hidden divide-y divide-neutral-200">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className={cn(
              'p-4 hover:bg-neutral-50 transition-colors',
              selectedId === doc.id && 'bg-primary-50'
            )}
            onClick={() => setSelectedId(doc.id)}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 flex-1">
                <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-neutral-900 truncate">
                    {doc.name}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <TypeBadge type={doc.type} size="sm" />
                    <Badge className={cn('gap-1', getStatusColor(doc.status))}>
                      {getStatusIcon(doc.status)}
                      {getStatusLabel(doc.status)}
                    </Badge>
                  </div>
                  <p className="text-xs text-neutral-500 mt-2">
                    {format(new Date(doc.createdAt), 'dd/MM/yyyy HH:mm')}
                  </p>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {onView && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onView(doc);
                      }}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Ver Detalles
                    </DropdownMenuItem>
                  )}
                  {onDownload && doc.status === 'completed' && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onDownload(doc);
                      }}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Descargar
                    </DropdownMenuItem>
                  )}
                  {onEmail && doc.status === 'completed' && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onEmail(doc);
                      }}
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Enviar por Email
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
