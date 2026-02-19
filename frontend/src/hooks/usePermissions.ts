/**
 * usePermissions Hook
 * Reads user role and returns permission flags
 *
 * Roles: admin, notario, abogado, asistente, mesa_control, pagos, folios_protocolo, archivo
 */

import { useAuth } from './useAuth';

// Permission matrix: role -> allowed modules
const ROLE_PERMISSIONS: Record<string, string[]> = {
  admin: ['*'], // All access
  notario: ['*'],
  abogado: ['cases', 'calendar', 'reports', 'documents', 'whatsapp'],
  asistente: ['cases', 'calendar', 'documents'],
  mesa_control: ['cases', 'calendar', 'tramites', 'checklist'],
  pagos: ['cases', 'payments', 'reports'],
  folios_protocolo: ['cases', 'documents'],
  archivo: ['cases', 'documents', 'history'],
};

export function usePermissions() {
  const { userRole } = useAuth();

  const permissions = ROLE_PERMISSIONS[userRole] || ROLE_PERMISSIONS.asistente;
  const hasFullAccess = permissions.includes('*');

  const canAccess = (module: string): boolean => {
    return hasFullAccess || permissions.includes(module);
  };

  return {
    userRole,
    canAccess,
    hasFullAccess,

    // Convenience flags
    canAccessUIF: hasFullAccess,
    canAccessReports: canAccess('reports'),
    canAccessWhatsApp: canAccess('whatsapp'),
    canAccessPayments: canAccess('payments') || hasFullAccess,
    canAccessCalendar: canAccess('calendar') || hasFullAccess,
    canAccessSettings: userRole === 'admin' || userRole === 'notario',
  };
}
