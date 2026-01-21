/**
 * TemplateGrid Component
 * Grid display of template cards with actions
 */

import { useState } from 'react';
import { FileText, MoreVertical, Edit, Trash2, Download, Copy, Link } from 'lucide-react';
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
import type { TemplateInfo } from '@/store';

interface TemplateGridProps {
  templates: TemplateInfo[];
  onEdit?: (template: TemplateInfo) => void;
  onEditMapping?: (template: TemplateInfo) => void;
  onDelete?: (template: TemplateInfo) => void;
  onDownload?: (template: TemplateInfo) => void;
  onDuplicate?: (template: TemplateInfo) => void;
  onSelect?: (template: TemplateInfo) => void;
  isLoading?: boolean;
}

export function TemplateGrid({
  templates,
  onEdit,
  onEditMapping,
  onDelete,
  onDownload,
  onDuplicate,
  onSelect,
  isLoading = false,
}: TemplateGridProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (template: TemplateInfo) => {
    setSelectedId(template.id);
    if (onSelect) {
      onSelect(template);
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="p-6 animate-pulse">
            <div className="space-y-4">
              <div className="h-12 w-12 bg-neutral-200 rounded-lg" />
              <div className="space-y-2">
                <div className="h-4 bg-neutral-200 rounded w-3/4" />
                <div className="h-3 bg-neutral-200 rounded w-1/2" />
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
            <FileText className="w-8 h-8 text-neutral-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">
              No hay templates
            </h3>
            <p className="text-neutral-600 mt-1">
              Sube tu primer template para comenzar
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {templates.map((template) => (
        <Card
          key={template.id}
          className={cn(
            'p-6 cursor-pointer transition-all hover:shadow-lg',
            selectedId === template.id && 'ring-2 ring-primary-500'
          )}
          onClick={() => handleSelect(template)}
        >
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  {template.type && <TypeBadge type={template.type} size="sm" />}
                </div>
              </div>

              {/* Actions Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {onEdit && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit(template);
                      }}
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Editar
                    </DropdownMenuItem>
                  )}
                  {onEditMapping && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onEditMapping(template);
                      }}
                    >
                      <Link className="w-4 h-4 mr-2" />
                      Editar Mapeo
                    </DropdownMenuItem>
                  )}
                  {onDuplicate && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onDuplicate(template);
                      }}
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Duplicar
                    </DropdownMenuItem>
                  )}
                  {onDownload && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onDownload(template);
                      }}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Descargar
                    </DropdownMenuItem>
                  )}
                  {onDelete && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(template);
                      }}
                      className="text-error hover:text-error"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Eliminar
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Content */}
            <div>
              <h3 className="font-semibold text-neutral-900 truncate">
                {template.name}
              </h3>
              <p className="text-sm text-neutral-600 mt-1 line-clamp-2">
                Template para {template.type}
              </p>
            </div>

            {/* Footer */}
            <div className="flex items-center gap-2 pt-2 border-t border-neutral-100">
              <Badge variant="secondary" className="text-xs">
                {template.id.substring(0, 8)}
              </Badge>
              {template.createdAt && (
                <span className="text-xs text-neutral-500">
                  {new Date(template.createdAt).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
