/**
 * TemplateCard Component
 * Card displaying template info with selection state
 */

import { FileText, Check, Cloud, HardDrive, Upload } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TypeBadge } from './TypeBadge';
import { cn } from '@/lib/utils';
import type { TemplateInfo } from '@/store';

interface TemplateCardProps {
  template: TemplateInfo;
  isSelected?: boolean;
  onSelect: () => void;
}

const sourceIcons = {
  drive: Cloud,
  local: HardDrive,
  uploaded: Upload,
};

const sourceLabels = {
  drive: 'Google Drive',
  local: 'Local',
  uploaded: 'Subido',
};

export function TemplateCard({ template, isSelected = false, onSelect }: TemplateCardProps) {
  const SourceIcon = sourceIcons[template.source];

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md',
        isSelected && 'ring-2 ring-primary shadow-lg'
      )}
      onClick={onSelect}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2 flex-1">
            <FileText className="w-5 h-5 text-muted-foreground mt-0.5" />
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base truncate" title={template.name}>
                {template.name}
              </CardTitle>
              <CardDescription className="mt-1 flex items-center gap-1">
                <SourceIcon className="w-3 h-3" />
                <span className="text-xs">{sourceLabels[template.source]}</span>
              </CardDescription>
            </div>
          </div>

          {isSelected && (
            <div className="flex-shrink-0">
              <div className="bg-primary text-primary-foreground rounded-full p-1">
                <Check className="w-4 h-4" />
              </div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Document type */}
        {template.type && (
          <div>
            <TypeBadge type={template.type} size="sm" />
          </div>
        )}

        {/* Placeholders count */}
        {template.placeholders && template.placeholders.length > 0 && (
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {template.placeholders.length} campos
            </Badge>
          </div>
        )}

        {/* Action button */}
        <Button
          variant={isSelected ? 'default' : 'outline'}
          size="sm"
          className="w-full"
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
        >
          {isSelected ? 'Seleccionado' : 'Seleccionar'}
        </Button>
      </CardContent>
    </Card>
  );
}
