/**
 * VersionHistory Component
 * Displays template version history with rollback capability
 */

import { useState } from 'react';
import { History, RotateCcw, Check, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

export interface TemplateVersion {
  id: string;
  template_id: string;
  version_number: number;
  storage_path: string;
  placeholders: string[];
  placeholder_mapping: Record<string, string>;
  es_activa: boolean;
  created_at: string;
  created_by?: string;
  notas?: string;
}

interface VersionHistoryProps {
  templateId: string;
  templateName: string;
  versions: TemplateVersion[];
  onActivate?: (version: TemplateVersion) => Promise<void>;
  onCompare?: (v1: TemplateVersion, v2: TemplateVersion) => void;
  isLoading?: boolean;
}

export function VersionHistory({
  templateName,
  versions,
  onActivate,
  isLoading = false,
}: Omit<VersionHistoryProps, 'templateId' | 'onCompare'>) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [confirmVersion, setConfirmVersion] = useState<TemplateVersion | null>(null);
  const [isActivating, setIsActivating] = useState(false);

  const handleActivate = async () => {
    if (!confirmVersion || !onActivate) return;

    setIsActivating(true);
    try {
      await onActivate(confirmVersion);
      setConfirmVersion(null);
    } catch (error) {
      console.error('Error activating version:', error);
    } finally {
      setIsActivating(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-MX', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-neutral-200 rounded w-1/3" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-neutral-200 rounded" />
          ))}
        </div>
      </Card>
    );
  }

  if (versions.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
            <History className="w-6 h-6 text-neutral-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">
              Sin historial de versiones
            </h3>
            <p className="text-neutral-600 mt-1">
              Este template no tiene versiones registradas
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className="overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-neutral-100 bg-neutral-50">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-neutral-600" />
            <h3 className="font-semibold text-neutral-900">
              Historial de Versiones
            </h3>
            <Badge variant="secondary">{versions.length}</Badge>
          </div>
          <p className="text-sm text-neutral-600 mt-1">{templateName}</p>
        </div>

        {/* Version List */}
        <div className="divide-y divide-neutral-100">
          {versions.map((version) => (
            <div
              key={version.id}
              className={cn(
                'p-4 transition-colors',
                version.es_activa && 'bg-success-50 border-l-4 border-l-success-500'
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold',
                      version.es_activa
                        ? 'bg-success-100 text-success-700'
                        : 'bg-neutral-100 text-neutral-600'
                    )}
                  >
                    v{version.version_number}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-neutral-900">
                        Version {version.version_number}
                      </span>
                      {version.es_activa && (
                        <Badge className="bg-success-100 text-success-700 hover:bg-success-100">
                          <Check className="w-3 h-3 mr-1" />
                          Activa
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-sm text-neutral-500 mt-0.5">
                      <Clock className="w-3 h-3" />
                      {formatDate(version.created_at)}
                    </div>

                    {version.notas && (
                      <p className="text-sm text-neutral-600 mt-1">
                        {version.notas}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {!version.es_activa && onActivate && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setConfirmVersion(version)}
                    >
                      <RotateCcw className="w-4 h-4 mr-1" />
                      Activar
                    </Button>
                  )}

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      setExpandedId(expandedId === version.id ? null : version.id)
                    }
                  >
                    {expandedId === version.id ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedId === version.id && (
                <div className="mt-4 pt-4 border-t border-neutral-100 space-y-3">
                  <div>
                    <span className="text-sm font-medium text-neutral-700">
                      Placeholders ({version.placeholders?.length || 0})
                    </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {version.placeholders?.slice(0, 10).map((ph) => (
                        <Badge key={ph} variant="secondary" className="text-xs">
                          {ph}
                        </Badge>
                      ))}
                      {version.placeholders?.length > 10 && (
                        <Badge variant="secondary" className="text-xs">
                          +{version.placeholders.length - 10} mas
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="text-xs text-neutral-500">
                    Storage: {version.storage_path}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={!!confirmVersion} onOpenChange={() => setConfirmVersion(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Activar Version {confirmVersion?.version_number}</DialogTitle>
            <DialogDescription>
              Esta accion hara que la version {confirmVersion?.version_number} sea la
              version activa del template. La version actual sera desactivada.
            </DialogDescription>
          </DialogHeader>

          {confirmVersion?.notas && (
            <div className="bg-neutral-50 p-3 rounded-lg">
              <span className="text-sm font-medium">Notas de la version:</span>
              <p className="text-sm text-neutral-600 mt-1">{confirmVersion.notas}</p>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmVersion(null)}
              disabled={isActivating}
            >
              Cancelar
            </Button>
            <Button onClick={handleActivate} disabled={isActivating}>
              {isActivating ? 'Activando...' : 'Confirmar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
