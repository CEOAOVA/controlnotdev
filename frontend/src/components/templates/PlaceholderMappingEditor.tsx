/**
 * PlaceholderMappingEditor Component
 * Allows editing the mapping between template placeholders and standard keys
 */

import { useState, useEffect, useMemo } from 'react';
import { Save, X, AlertTriangle, Check, RefreshCw, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { usePlaceholderMapping } from '@/hooks';
import type { StandardKey } from '@/api/types';

interface PlaceholderMappingEditorProps {
  templateId: string;
  templateName?: string;
  isOpen: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

// No mapping indicator
const NO_MAPPING = '__NO_MAPPING__';

export function PlaceholderMappingEditor({
  templateId,
  templateName,
  isOpen,
  onClose,
  onSaved,
}: PlaceholderMappingEditorProps) {
  const {
    mapping,
    placeholders,
    standardKeys,
    documentType,
    templateName: apiTemplateName,
    isLoading,
    isUpdating,
    mappingError,
    keysError,
    updateMapping,
    refetch,
  } = usePlaceholderMapping(templateId, { enabled: isOpen });

  // Local state for editing
  const [localMapping, setLocalMapping] = useState<Record<string, string>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterUnmapped, setFilterUnmapped] = useState(false);

  // Initialize local mapping when data loads
  useEffect(() => {
    if (mapping && Object.keys(mapping).length > 0) {
      setLocalMapping(mapping);
      setHasChanges(false);
    }
  }, [mapping]);

  // Filter placeholders based on search and filter
  const filteredPlaceholders = useMemo(() => {
    let result = [...placeholders];

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (p) =>
          p.toLowerCase().includes(term) ||
          (localMapping[p] || '').toLowerCase().includes(term)
      );
    }

    // Filter unmapped only
    if (filterUnmapped) {
      result = result.filter((p) => {
        const mappedKey = localMapping[p] || p;
        return mappedKey === p && !standardKeys.find((k) => k.key === p);
      });
    }

    return result.sort((a, b) => a.localeCompare(b));
  }, [placeholders, searchTerm, filterUnmapped, localMapping, standardKeys]);

  // Handle mapping change for a placeholder
  const handleMappingChange = (placeholder: string, newKey: string) => {
    setLocalMapping((prev) => {
      const updated = { ...prev };
      if (newKey === NO_MAPPING || newKey === placeholder) {
        // Remove explicit mapping - let it default to placeholder name
        updated[placeholder] = placeholder;
      } else {
        updated[placeholder] = newKey;
      }
      return updated;
    });
    setHasChanges(true);
    setError(null);
  };

  // Check if a placeholder is properly mapped
  const isProperlyMapped = (placeholder: string): boolean => {
    const mappedKey = localMapping[placeholder] || placeholder;
    // Properly mapped if:
    // 1. Has explicit mapping to a different standard key
    // 2. Placeholder name itself is a standard key
    if (mappedKey !== placeholder) {
      return !!standardKeys.find((k) => k.key === mappedKey);
    }
    return !!standardKeys.find((k) => k.key === placeholder);
  };

  // Get standard key info for a mapped key
  const getKeyInfo = (keyName: string): StandardKey | undefined => {
    return standardKeys.find((k) => k.key === keyName);
  };

  // Save mapping
  const handleSave = async () => {
    try {
      setError(null);
      await updateMapping(localMapping);
      setHasChanges(false);
      onSaved?.();
    } catch (err: any) {
      setError(err.message || 'Error al guardar el mapeo');
    }
  };

  // Handle close
  const handleClose = () => {
    if (!isUpdating) {
      if (hasChanges) {
        // Could add confirmation dialog here
      }
      setError(null);
      setSearchTerm('');
      setFilterUnmapped(false);
      onClose();
    }
  };

  // Calculate local stats
  const localStats = useMemo(() => {
    const total = placeholders.length;
    const mapped = placeholders.filter((p) => isProperlyMapped(p)).length;
    return {
      total,
      mapped,
      unmapped: total - mapped,
      percentage: total > 0 ? Math.round((mapped / total) * 100) : 0,
    };
  }, [placeholders, localMapping, standardKeys]);

  const displayName = templateName || apiTemplateName || 'Template';

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            Editar Mapeo de Campos
            {hasChanges && (
              <Badge variant="secondary" className="text-xs">
                Sin guardar
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            Configura la correspondencia entre los placeholders del template y
            los campos estandarizados del sistema
          </DialogDescription>
        </DialogHeader>

        {/* Template Info */}
        <div className="flex items-center justify-between py-3 px-4 bg-neutral-50 rounded-lg">
          <div>
            <p className="font-medium text-sm">{displayName}</p>
            <p className="text-xs text-neutral-500">
              Tipo: {documentType || 'No definido'}
            </p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="text-center">
              <span className="font-semibold text-lg">{localStats.total}</span>
              <p className="text-xs text-neutral-500">Placeholders</p>
            </div>
            <div className="text-center">
              <span className="font-semibold text-lg text-green-600">
                {localStats.mapped}
              </span>
              <p className="text-xs text-neutral-500">Mapeados</p>
            </div>
            {localStats.unmapped > 0 && (
              <div className="text-center">
                <span className="font-semibold text-lg text-amber-600">
                  {localStats.unmapped}
                </span>
                <p className="text-xs text-neutral-500">Por revisar</p>
              </div>
            )}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-5 h-5 animate-spin text-neutral-500" />
              <span className="text-neutral-500">Cargando mapeo...</span>
            </div>
          </div>
        )}

        {/* Error State */}
        {(mappingError || keysError) && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {mappingError || keysError}
            </AlertDescription>
          </Alert>
        )}

        {/* Content */}
        {!isLoading && !mappingError && !keysError && (
          <>
            {/* Search and Filters */}
            <div className="flex items-center gap-3 py-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <Input
                  type="text"
                  placeholder="Buscar placeholder..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button
                variant={filterUnmapped ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => setFilterUnmapped(!filterUnmapped)}
                className="gap-2"
              >
                <AlertTriangle className="w-4 h-4" />
                Solo sin mapear ({localStats.unmapped})
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetch()}
                className="gap-2"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>

            {/* Mapping Table */}
            <div className="flex-1 overflow-auto border rounded-lg">
              <Table>
                <TableHeader className="sticky top-0 bg-white">
                  <TableRow>
                    <TableHead className="w-[40%]">
                      Placeholder (template)
                    </TableHead>
                    <TableHead className="w-[45%]">
                      Mapea a (campo estandar)
                    </TableHead>
                    <TableHead className="w-[15%] text-center">
                      Estado
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPlaceholders.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={3}
                        className="text-center text-neutral-500 py-8"
                      >
                        {searchTerm || filterUnmapped
                          ? 'No se encontraron placeholders con los filtros aplicados'
                          : 'No hay placeholders en este template'}
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredPlaceholders.map((placeholder) => {
                      const currentMapping =
                        localMapping[placeholder] || placeholder;
                      const isMapped = isProperlyMapped(placeholder);
                      const keyInfo = getKeyInfo(currentMapping);

                      return (
                        <TableRow
                          key={placeholder}
                          className={!isMapped ? 'bg-amber-50/50' : ''}
                        >
                          <TableCell className="font-mono text-sm">
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className="cursor-help">
                                    {`{{${placeholder}}}`}
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Placeholder original del template</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </TableCell>
                          <TableCell>
                            <Select
                              value={currentMapping}
                              onValueChange={(value) =>
                                handleMappingChange(placeholder, value)
                              }
                            >
                              <SelectTrigger className="w-full">
                                <SelectValue placeholder="Seleccionar campo..." />
                              </SelectTrigger>
                              <SelectContent className="max-h-60">
                                <SelectItem value={placeholder}>
                                  <span className="text-neutral-500">
                                    Sin mapeo (usar: {placeholder})
                                  </span>
                                </SelectItem>
                                {standardKeys.map((key) => (
                                  <SelectItem key={key.key} value={key.key}>
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        {key.key}
                                      </span>
                                      {key.description && (
                                        <span className="text-xs text-neutral-500 truncate max-w-[250px]">
                                          {key.description}
                                        </span>
                                      )}
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            {keyInfo && (
                              <p className="text-xs text-neutral-500 mt-1 truncate">
                                {keyInfo.description}
                              </p>
                            )}
                          </TableCell>
                          <TableCell className="text-center">
                            {isMapped ? (
                              <Badge
                                variant="outline"
                                className="text-green-600 border-green-300 bg-green-50"
                              >
                                <Check className="w-3 h-3 mr-1" />
                                OK
                              </Badge>
                            ) : (
                              <Badge
                                variant="outline"
                                className="text-amber-600 border-amber-300 bg-amber-50"
                              >
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                Revisar
                              </Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </div>
          </>
        )}

        {/* Error from save */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-neutral-500">
            {hasChanges && (
              <span className="text-amber-600">
                Hay cambios sin guardar
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isUpdating}
              className="gap-2"
            >
              <X className="w-4 h-4" />
              Cancelar
            </Button>
            <Button
              onClick={handleSave}
              disabled={isUpdating || !hasChanges}
              className="gap-2"
            >
              {isUpdating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Guardar Mapeo
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
