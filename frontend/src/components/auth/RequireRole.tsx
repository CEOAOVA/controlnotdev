/**
 * RequireRole
 * Wrapper component that hides content based on user role
 */

import { usePermissions } from '@/hooks/usePermissions';

interface RequireRoleProps {
  /** Module name to check permission for */
  module?: string;
  /** Specific roles allowed (alternative to module) */
  roles?: string[];
  /** Content to show if allowed */
  children: React.ReactNode;
  /** Optional fallback when access denied */
  fallback?: React.ReactNode;
}

export function RequireRole({ module, roles, children, fallback = null }: RequireRoleProps) {
  const { canAccess, userRole, hasFullAccess } = usePermissions();

  // Check by specific roles
  if (roles) {
    if (!roles.includes(userRole) && !hasFullAccess) {
      return <>{fallback}</>;
    }
    return <>{children}</>;
  }

  // Check by module
  if (module) {
    if (!canAccess(module)) {
      return <>{fallback}</>;
    }
    return <>{children}</>;
  }

  // No restriction specified
  return <>{children}</>;
}
