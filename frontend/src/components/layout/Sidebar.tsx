/**
 * Sidebar Component
 * Main navigation sidebar with links to all pages
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  FolderOpen,
  History,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks';

interface NavItem {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  badge?: string;
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
  },
  {
    label: 'Generar Documento',
    icon: FileText,
    path: '/generate',
  },
  {
    label: 'Templates',
    icon: FolderOpen,
    path: '/templates',
  },
  {
    label: 'Historial',
    icon: History,
    path: '/history',
  },
  {
    label: 'Configuración',
    icon: Settings,
    path: '/settings',
  },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { signOut, userName, userEmail, tenantName } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-neutral-900 text-white transition-all duration-300 z-40 flex flex-col',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-neutral-800">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h1 className="font-bold text-sm">ControlNot</h1>
                <p className="text-xs text-neutral-400">v2.0</p>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-white hover:bg-neutral-800"
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* User Info */}
      {!isCollapsed && (
        <div className="p-4 border-b border-neutral-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center text-white font-semibold">
              {userName.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{userName}</p>
              <p className="text-xs text-neutral-400 truncate">{userEmail}</p>
              {tenantName && (
                <p className="text-xs text-primary-400 truncate">{tenantName}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                    'hover:bg-neutral-800',
                    isActive && 'bg-primary-500 text-white',
                    !isActive && 'text-neutral-300',
                    isCollapsed && 'justify-center'
                  )
                }
                title={isCollapsed ? item.label : undefined}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!isCollapsed && (
                  <span className="text-sm font-medium">{item.label}</span>
                )}
                {!isCollapsed && item.badge && (
                  <span className="ml-auto px-2 py-0.5 text-xs bg-primary-500 rounded-full">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Sign Out Button */}
      <div className="p-4 border-t border-neutral-800">
        <Button
          variant="ghost"
          onClick={handleSignOut}
          className={cn(
            'w-full justify-start text-neutral-300 hover:bg-neutral-800 hover:text-white',
            isCollapsed && 'justify-center'
          )}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && <span className="ml-3">Cerrar Sesión</span>}
        </Button>
      </div>

      {/* Collapsed Tooltip Info */}
      {isCollapsed && (
        <div className="absolute left-20 top-20 bg-neutral-800 rounded-lg p-2 opacity-0 pointer-events-none">
          <p className="text-xs text-white whitespace-nowrap">{userName}</p>
        </div>
      )}
    </aside>
  );
}
