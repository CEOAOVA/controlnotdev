/**
 * Topbar Component
 * Top navigation bar with breadcrumbs and actions
 */

import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, Bell, Search, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { useSidebarStore } from '@/store';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

const routeMap: Record<string, string> = {
  '/': 'Dashboard',
  '/generate': 'Generar Documento',
  '/templates': 'Templates',
  '/history': 'Historial',
  '/settings': 'Configuración',
};

export function Topbar() {
  const location = useLocation();
  const { toggle } = useSidebarStore();

  // Generate breadcrumbs from current path
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Inicio', path: '/' },
  ];

  const currentPath = location.pathname;
  if (currentPath !== '/') {
    const label = routeMap[currentPath] || 'Página';
    breadcrumbs.push({ label });
  }

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-neutral-200">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left: Hamburger + Breadcrumbs */}
        <div className="flex items-center gap-2">
          {/* Mobile hamburger menu */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggle}
            className="md:hidden"
            aria-label="Abrir menú"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <nav className="flex items-center gap-2">
            {breadcrumbs.map((crumb, index) => (
              <div key={index} className="flex items-center gap-2">
                {index > 0 && (
                  <ChevronRight className="w-4 h-4 text-neutral-400" />
                )}
                {crumb.path && index < breadcrumbs.length - 1 ? (
                  <Link
                    to={crumb.path}
                    className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors"
                  >
                    {crumb.label}
                  </Link>
                ) : (
                  <span
                    className={cn(
                      'text-sm font-medium',
                      index === breadcrumbs.length - 1
                        ? 'text-neutral-900'
                        : 'text-neutral-600'
                    )}
                  >
                    {crumb.label}
                  </span>
                )}
              </div>
            ))}
          </nav>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <Input
              type="search"
              placeholder="Buscar..."
              className="w-64 pl-9 pr-4"
            />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full" />
          </Button>
        </div>
      </div>
    </header>
  );
}
