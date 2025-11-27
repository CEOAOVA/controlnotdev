/**
 * RequiredDocsList Component
 *
 * Displays a collapsible list of required documents for each category.
 * Changes based on document type (compraventa, poder, etc.)
 *
 * Example categories:
 * - Compraventa: Vendedor/Comprador/Inmueble
 * - Poder: Poderdante/Apoderado/Documentos
 * - Sociedad: Socios/Capital/Administración
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DocumentType } from '@/store/documentStore';

interface RequiredDocsListProps {
  documentType: DocumentType;
  category: 'parte_a' | 'parte_b' | 'otros';
  className?: string;
}

// Define required documents per document type and category
const REQUIRED_DOCS: Record<
  DocumentType,
  Record<string, { name: string; icon: string; docs: string[] }>
> = {
  compraventa: {
    parte_a: {
      name: 'Vendedor',
      icon: '👤',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Escritura anterior del inmueble',
        'Comprobante de domicilio',
        'Boleta predial actualizada',
      ],
    },
    parte_b: {
      name: 'Comprador',
      icon: '👥',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Comprobante de domicilio',
        'Estado de cuenta (para crédito)',
      ],
    },
    otros: {
      name: 'Inmueble',
      icon: '🏠',
      docs: [
        'Certificado de libertad de gravamen',
        'Avalúo catastral',
        'Boleta de agua actualizada',
        'Planos autorizados (si aplica)',
        'Constancia de no adeudo predial',
      ],
    },
  },
  donacion: {
    parte_a: {
      name: 'Donante',
      icon: '🎁',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Escritura del bien a donar',
        'Comprobante de domicilio',
      ],
    },
    parte_b: {
      name: 'Donatario',
      icon: '👥',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Comprobante de domicilio',
      ],
    },
    otros: {
      name: 'Documentos Adicionales',
      icon: '📄',
      docs: [
        'Certificado de libertad de gravamen',
        'Avalúo del bien',
        'Constancia de no adeudo predial',
      ],
    },
  },
  testamento: {
    parte_a: {
      name: 'Testador',
      icon: '📜',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Acta de nacimiento',
        'Comprobante de domicilio',
      ],
    },
    parte_b: {
      name: 'Herederos',
      icon: '👨\u200d👩\u200d👧\u200d👦',
      docs: [
        'Identificaciones de herederos',
        'Actas de nacimiento de herederos',
        'CURP de herederos',
      ],
    },
    otros: {
      name: 'Bienes y Documentos',
      icon: '💼',
      docs: [
        'Escrituras de propiedades',
        'Estados de cuenta bancarios',
        'Certificados de inversiones',
      ],
    },
  },
  poder: {
    parte_a: {
      name: 'Poderdante',
      icon: '👤',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Acta de nacimiento',
        'Comprobante de domicilio',
      ],
    },
    parte_b: {
      name: 'Apoderado',
      icon: '🤝',
      docs: [
        'INE o Pasaporte vigente',
        'RFC',
        'CURP',
        'Comprobante de domicilio',
      ],
    },
    otros: {
      name: 'Documentos del Poder',
      icon: '📋',
      docs: [
        'Descripción de facultades',
        'Documentos relacionados al acto',
        'Limitaciones del poder (si aplica)',
      ],
    },
  },
  sociedad: {
    parte_a: {
      name: 'Socios',
      icon: '👔',
      docs: [
        'INE o Pasaporte de cada socio',
        'RFC de cada socio',
        'CURP de cada socio',
        'Comprobantes de domicilio',
      ],
    },
    parte_b: {
      name: 'Capital Social',
      icon: '💰',
      docs: [
        'Comprobantes de aportación',
        'Estados de cuenta',
        'Avalúo de bienes aportados',
      ],
    },
    otros: {
      name: 'Administración',
      icon: '⚖️',
      docs: [
        'Estatutos sociales',
        'Designación de administradores',
        'Poderes especiales (si aplica)',
      ],
    },
  },
};

export const RequiredDocsList: React.FC<RequiredDocsListProps> = ({
  documentType,
  category,
  className,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const categoryInfo = REQUIRED_DOCS[documentType]?.[category];

  if (!categoryInfo) {
    return null;
  }

  const { name, icon, docs } = categoryInfo;

  return (
    <div className={cn('border border-neutral-200 rounded-lg overflow-hidden', className)}>
      {/* Header - Clickable */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 bg-neutral-50 hover:bg-neutral-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <span className="text-sm font-medium text-neutral-900">
            Documentos requeridos para {name}
          </span>
          <span className="text-xs text-neutral-500">
            ({docs.length} documentos)
          </span>
        </div>

        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-neutral-600" />
        ) : (
          <ChevronRight className="w-4 h-4 text-neutral-600" />
        )}
      </button>

      {/* List - Collapsible */}
      {isExpanded && (
        <div className="p-3 bg-white space-y-2">
          {docs.map((doc, index) => (
            <div
              key={index}
              className="flex items-start gap-2 text-sm text-neutral-700"
            >
              <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
              <span>{doc}</span>
            </div>
          ))}

          <div className="mt-4 pt-3 border-t border-neutral-200">
            <p className="text-xs text-neutral-500">
              💡 <strong>Tip:</strong> Asegúrate de que todos los documentos sean legibles y
              estén actualizados para una mejor extracción de datos.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RequiredDocsList;
