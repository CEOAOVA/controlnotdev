/**
 * CategorySection Component
 * Collapsible section for a category of fields
 */

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface CategorySectionProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  fieldCount: number;
  filledCount: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function CategorySection({
  title,
  description,
  icon,
  fieldCount,
  filledCount,
  children,
  defaultOpen = true,
}: CategorySectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const completionPercentage = Math.round((filledCount / fieldCount) * 100);
  const isComplete = filledCount === fieldCount;

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Header */}
      <Button
        variant="ghost"
        className={cn(
          'w-full justify-between p-4 h-auto hover:bg-accent',
          isOpen && 'bg-accent/50'
        )}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-3 flex-1 text-left">
          {/* Icon */}
          {icon && <div className="text-2xl">{icon}</div>}

          {/* Title and description */}
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-base">{title}</div>
            {description && (
              <div className="text-sm text-muted-foreground mt-0.5">
                {description}
              </div>
            )}
          </div>

          {/* Status badges */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Badge
              variant={isComplete ? 'default' : 'secondary'}
              className={cn(
                'font-mono',
                isComplete && 'bg-green-500 hover:bg-green-600'
              )}
            >
              {filledCount}/{fieldCount}
            </Badge>

            <Badge variant="outline" className="font-mono">
              {completionPercentage}%
            </Badge>
          </div>

          {/* Expand icon */}
          {isOpen ? (
            <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
          ) : (
            <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
          )}
        </div>
      </Button>

      {/* Content */}
      {isOpen && (
        <div className="p-4 border-t bg-card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {children}
          </div>
        </div>
      )}
    </div>
  );
}
