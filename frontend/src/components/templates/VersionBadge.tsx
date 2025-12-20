/**
 * VersionBadge Component
 * Visual indicator for template version status
 */

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { History, CheckCircle2, Clock } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface VersionBadgeProps {
  versionNumber: number;
  isActive?: boolean;
  totalVersions?: number;
  showTooltip?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function VersionBadge({
  versionNumber,
  isActive = false,
  totalVersions,
  showTooltip = true,
  size = 'md',
  className,
}: VersionBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-0.5',
    lg: 'text-base px-2.5 py-1',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  const badge = (
    <Badge
      variant={isActive ? 'default' : 'secondary'}
      className={cn(
        'font-mono gap-1',
        sizeClasses[size],
        isActive
          ? 'bg-success-100 text-success-700 hover:bg-success-100 border-success-200'
          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-100',
        className
      )}
    >
      {isActive ? (
        <CheckCircle2 className={iconSizes[size]} />
      ) : (
        <History className={iconSizes[size]} />
      )}
      v{versionNumber}
      {totalVersions && totalVersions > 1 && !isActive && (
        <span className="text-neutral-400">/{totalVersions}</span>
      )}
    </Badge>
  );

  if (!showTooltip) {
    return badge;
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent>
          <div className="text-sm">
            {isActive ? (
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-success-500" />
                <span>Version activa</span>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>Version {versionNumber} de {totalVersions || versionNumber}</span>
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * VersionIndicator - Compact inline version indicator
 */
interface VersionIndicatorProps {
  versionNumber: number;
  isActive?: boolean;
  className?: string;
}

export function VersionIndicator({
  versionNumber,
  isActive = false,
  className,
}: VersionIndicatorProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-0.5 text-xs font-mono',
        isActive ? 'text-success-600' : 'text-neutral-500',
        className
      )}
    >
      {isActive && <CheckCircle2 className="w-3 h-3" />}
      v{versionNumber}
    </span>
  );
}

/**
 * VersionDot - Minimal dot indicator for version status
 */
interface VersionDotProps {
  isActive?: boolean;
  hasMultipleVersions?: boolean;
  className?: string;
}

export function VersionDot({
  isActive = false,
  hasMultipleVersions = false,
  className,
}: VersionDotProps) {
  if (!hasMultipleVersions) {
    return null;
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span
            className={cn(
              'inline-block w-2 h-2 rounded-full',
              isActive ? 'bg-success-500' : 'bg-neutral-300',
              className
            )}
          />
        </TooltipTrigger>
        <TooltipContent>
          {isActive ? 'Version activa' : 'Tiene versiones anteriores'}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
