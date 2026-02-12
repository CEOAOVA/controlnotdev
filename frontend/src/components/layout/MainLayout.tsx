/**
 * MainLayout Component
 * Main application layout with sidebar, topbar, content, and footer
 * Responsive: Sidebar hidden on mobile, hamburger menu in Topbar
 */

import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Footer } from './Footer';
import { useSidebarStore } from '@/store';

interface MainLayoutProps {
  children: React.ReactNode;
  /**
   * If true, hides sidebar and uses full width
   * @default false
   */
  fullWidth?: boolean;
}

export function MainLayout({ children, fullWidth = false }: MainLayoutProps) {
  const { isOpen, close, isCollapsed } = useSidebarStore();

  return (
    <div className="flex min-h-screen bg-neutral-50">
      {/* Sidebar - hidden on mobile, visible on md+ */}
      {!fullWidth && <Sidebar isOpen={isOpen} onClose={close} />}

      {/* Main Content Area - responsive margin */}
      <div className={`flex-1 flex flex-col transition-[margin] duration-300 ${!fullWidth ? (isCollapsed ? 'md:ml-20' : 'md:ml-64') : ''}`}>
        {/* Topbar */}
        <Topbar />

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="container py-4 sm:py-8 px-4 sm:px-6 max-w-7xl">
            {children}
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
