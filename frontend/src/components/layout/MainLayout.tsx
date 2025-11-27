/**
 * MainLayout Component
 * Main application layout with sidebar, topbar, content, and footer
 */

import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Footer } from './Footer';

interface MainLayoutProps {
  children: React.ReactNode;
  /**
   * If true, hides sidebar and uses full width
   * @default false
   */
  fullWidth?: boolean;
}

export function MainLayout({ children, fullWidth = false }: MainLayoutProps) {
  return (
    <div className="flex min-h-screen bg-neutral-50">
      {/* Sidebar */}
      {!fullWidth && <Sidebar />}

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col ${!fullWidth ? 'ml-64' : ''}`}>
        {/* Topbar */}
        <Topbar />

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="container py-8 max-w-7xl">
            {children}
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
