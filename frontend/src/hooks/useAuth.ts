/**
 * useAuth Hook
 * Custom hook for authentication operations and state
 */

import { useEffect } from 'react';
import { useAuthStore } from '@/store';

export function useAuth() {
  const {
    user,
    profile,
    session,
    isAuthenticated,
    isLoading,
    error,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile,
    checkSession,
    refreshSession,
    setError,
  } = useAuthStore();

  // NOTE: No llamamos checkSession() aquí porque el listener onAuthStateChange
  // en useAuthStore.ts ya maneja la inicialización de sesión automáticamente.
  // Llamarlo aquí causaba un loop infinito.

  // Setup session refresh interval (every 30 minutes)
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      refreshSession();
    }, 30 * 60 * 1000); // 30 minutes

    return () => clearInterval(interval);
  }, [isAuthenticated, refreshSession]);

  return {
    // State
    user,
    profile,
    session,
    isAuthenticated,
    isLoading,
    error,

    // Auth operations
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile,

    // Helpers
    checkSession,
    refreshSession,
    clearError: () => setError(null),

    // Computed properties
    tenantId: profile?.tenant_id || null,
    tenantName: profile?.tenant_name || null,
    notaryNumber: profile?.notary_number || null,
    userEmail: user?.email || null,
    userName: profile?.full_name || user?.email?.split('@')[0] || 'Usuario',
    userAvatar: profile?.avatar_url || null,
    userRole: profile?.rol || 'asistente',
  };
}
