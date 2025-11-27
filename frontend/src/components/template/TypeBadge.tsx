/**
 * TypeBadge Component
 * Badge with color and icon for document type
 */

import { FileText, Heart, Scale, ScrollText, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DocumentType } from '@/store';

interface TypeBadgeProps {
  type: DocumentType;
  size?: 'sm' | 'default' | 'lg';
  showIcon?: boolean;
}

const typeConfig: Record<
  DocumentType,
  { label: string; color: string; icon: typeof FileText }
> = {
  compraventa: {
    label: 'Compraventa',
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    icon: Scale,
  },
  donacion: {
    label: 'Donación',
    color: 'bg-pink-100 text-pink-700 border-pink-200',
    icon: Heart,
  },
  testamento: {
    label: 'Testamento',
    color: 'bg-purple-100 text-purple-700 border-purple-200',
    icon: ScrollText,
  },
  poder: {
    label: 'Poder',
    color: 'bg-green-100 text-green-700 border-green-200',
    icon: FileText,
  },
  sociedad: {
    label: 'Sociedad',
    color: 'bg-orange-100 text-orange-700 border-orange-200',
    icon: Building2,
  },
};

export function TypeBadge({ type, size = 'default', showIcon = true }: TypeBadgeProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    default: 'text-sm px-2.5 py-0.5',
    lg: 'text-base px-3 py-1',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-semibold border',
        config.color,
        sizeClasses[size]
      )}
    >
      {showIcon && <Icon className="w-3 h-3" />}
      <span>{config.label}</span>
    </span>
  );
}
