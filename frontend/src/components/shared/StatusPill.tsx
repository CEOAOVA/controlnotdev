/**
 * StatusPill Component
 *
 * Semantic status indicator with color-coded variants
 * Used for: service status, document status, API health, etc.
 *
 * Variants:
 * - success: Green (completed, active, healthy)
 * - warning: Yellow (pending, limited, attention needed)
 * - error: Red (failed, inactive, unhealthy)
 * - info: Blue (informational, in progress)
 */

import React from 'react';
import { cn } from '@/lib/utils';

export type StatusVariant = 'success' | 'warning' | 'error' | 'info';

interface StatusPillProps {
  status: StatusVariant;
  children: React.ReactNode;
  className?: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({
  status,
  children,
  className,
}) => {
  const variantStyles: Record<StatusVariant, string> = {
    success: 'bg-success/10 text-success-700 border-success/20',
    warning: 'bg-warning/10 text-warning-700 border-warning/20',
    error: 'bg-error/10 text-error-700 border-error/20',
    info: 'bg-info/10 text-info-700 border-info/20',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5',
        'px-3 py-1 rounded-full',
        'text-xs font-medium border',
        'transition-colors duration-200',
        variantStyles[status],
        className
      )}
    >
      {children}
    </span>
  );
};

/**
 * Icon variants for common use cases
 */
export const StatusIcon: Record<StatusVariant, string> = {
  success: '✓',
  warning: '⚠',
  error: '✗',
  info: 'ℹ',
};

/**
 * Helper component with icon included
 */
interface StatusPillWithIconProps extends Omit<StatusPillProps, 'children'> {
  label: string;
  showIcon?: boolean;
}

export const StatusPillWithIcon: React.FC<StatusPillWithIconProps> = ({
  status,
  label,
  showIcon = true,
  className,
}) => {
  return (
    <StatusPill status={status} className={className}>
      {showIcon && <span>{StatusIcon[status]}</span>}
      <span>{label}</span>
    </StatusPill>
  );
};

export default StatusPill;
