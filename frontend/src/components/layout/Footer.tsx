/**
 * Footer Component
 * Application footer with version and links
 */

import { Heart } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-muted/30 mt-auto">
      <div className="container py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="font-semibold mb-3">ControlNot V2</h3>
            <p className="text-sm text-muted-foreground">
              Sistema de procesamiento de documentos notariales con inteligencia
              artificial para optimizar el trabajo en notarías mexicanas.
            </p>
          </div>

          {/* Features */}
          <div>
            <h3 className="font-semibold mb-3">Características</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>OCR paralelo 10x más rápido</li>
              <li>Multi-provider AI (OpenRouter)</li>
              <li>5 tipos de documentos</li>
              <li>Generación automática Word</li>
            </ul>
          </div>

          {/* Tech */}
          <div>
            <h3 className="font-semibold mb-3">Tecnología</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>React + TypeScript</li>
              <li>FastAPI + Python</li>
              <li>Google Cloud Vision OCR</li>
              <li>OpenAI GPT-4o / Claude</li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-6 border-t text-center text-sm text-muted-foreground">
          <p className="flex items-center justify-center gap-1">
            Hecho con <Heart className="w-4 h-4 text-red-500 fill-current" /> para
            notarías mexicanas · © {currentYear}
          </p>
          <p className="mt-2 text-xs">
            v2.0.0 · Build {new Date().toISOString().split('T')[0]}
          </p>
        </div>
      </div>
    </footer>
  );
}
