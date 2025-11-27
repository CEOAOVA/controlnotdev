/**
 * AuthGuard Component
 * Protects routes by requiring authentication
 */

import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks';

interface AuthGuardProps {
  children: ReactNode;
  /**
   * Redirect path when user is not authenticated
   * @default "/login"
   */
  redirectTo?: string;
  /**
   * If true, shows loading state while checking authentication
   * @default true
   */
  showLoading?: boolean;
}

export function AuthGuard({
  children,
  redirectTo = '/login',
  showLoading = true,
}: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading state while checking session
  if (isLoading && showLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-neutral-600 font-medium">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the location they were trying to access
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // User is authenticated, render children
  return <>{children}</>;
}
