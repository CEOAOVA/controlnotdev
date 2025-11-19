/**
 * MainLayout Component
 * Main application layout with header, content, and footer
 */

import { Header } from './Header';
import { Footer } from './Footer';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        <div className="container py-8">
          {children}
        </div>
      </main>

      <Footer />
    </div>
  );
}
