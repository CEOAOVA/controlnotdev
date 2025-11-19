/**
 * Header Component
 * Application header with logo and navigation
 */

import { FileText, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo and title */}
        <div className="flex items-center gap-3">
          <div className="bg-primary rounded-lg p-2">
            <FileText className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-bold">ControlNot V2</h1>
            <p className="text-xs text-muted-foreground">
              Procesamiento notarial con IA
            </p>
          </div>
        </div>

        {/* Navigation/actions */}
        <nav className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <a
              href="https://github.com/your-repo"
              target="_blank"
              rel="noopener noreferrer"
              className="gap-2"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </Button>
        </nav>
      </div>
    </header>
  );
}
