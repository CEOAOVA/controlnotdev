/**
 * DataEditor Component
 * Main editor for reviewing and editing extracted document data
 */

import { useEffect, useMemo, useState } from 'react';
import { Search, RotateCcw, Save } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CategorySection } from './CategorySection';
import { FieldGroup } from './FieldGroup';
import { useDocumentStore } from '@/store';
import { MetricsDashboard } from '@/components/generation/MetricsDashboard';

// Field metadata type
interface FieldMetadata {
  name: string;
  label: string;
  description?: string;
  category: string;
  required?: boolean;
  type?: 'text' | 'textarea' | 'number';
}

export function DataEditor() {
  const { extractedData, editedData, updateField, setEditedData, documentType } =
    useDocumentStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  // Get field metadata based on document type
  const fieldMetadata = useMemo<FieldMetadata[]>(() => {
    if (!documentType) return [];

    // Define field metadata for each document type
    // This should ideally come from an API or config file
    const metadataMap: Record<string, FieldMetadata[]> = {
      compraventa: [
        // Datos comunes
        {
          name: 'Numero_Escritura',
          label: 'Número de Escritura',
          category: 'Datos Generales',
          required: true,
        },
        {
          name: 'Fecha_Firma',
          label: 'Fecha de Firma',
          category: 'Datos Generales',
          required: true,
        },
        {
          name: 'Notaria_Numero',
          label: 'Número de Notaría',
          category: 'Datos Generales',
        },
        {
          name: 'Nombre_Notario',
          label: 'Nombre del Notario',
          category: 'Datos Generales',
          required: true,
        },
        {
          name: 'Ciudad_Notaria',
          label: 'Ciudad de la Notaría',
          category: 'Datos Generales',
        },

        // Parte vendedora
        {
          name: 'Parte_Vendedora_Nombre_Completo',
          label: 'Nombre Completo Vendedor',
          category: 'Parte Vendedora',
          required: true,
        },
        {
          name: 'Parte_Vendedora_Edad',
          label: 'Edad',
          category: 'Parte Vendedora',
          type: 'number',
        },
        {
          name: 'Parte_Vendedora_Nacionalidad',
          label: 'Nacionalidad',
          category: 'Parte Vendedora',
        },
        {
          name: 'Parte_Vendedora_Estado_Civil',
          label: 'Estado Civil',
          category: 'Parte Vendedora',
        },
        {
          name: 'Parte_Vendedora_RFC',
          label: 'RFC',
          category: 'Parte Vendedora',
        },
        {
          name: 'Parte_Vendedora_CURP',
          label: 'CURP',
          category: 'Parte Vendedora',
        },
        {
          name: 'Parte_Vendedora_INE',
          label: 'Clave INE',
          category: 'Parte Vendedora',
        },
        {
          name: 'Parte_Vendedora_Domicilio',
          label: 'Domicilio',
          category: 'Parte Vendedora',
          type: 'textarea',
        },

        // Parte compradora
        {
          name: 'Parte_Compradora_Nombre_Completo',
          label: 'Nombre Completo Comprador',
          category: 'Parte Compradora',
          required: true,
        },
        {
          name: 'Parte_Compradora_Edad',
          label: 'Edad',
          category: 'Parte Compradora',
          type: 'number',
        },
        {
          name: 'Parte_Compradora_Nacionalidad',
          label: 'Nacionalidad',
          category: 'Parte Compradora',
        },
        {
          name: 'Parte_Compradora_Estado_Civil',
          label: 'Estado Civil',
          category: 'Parte Compradora',
        },
        {
          name: 'Parte_Compradora_RFC',
          label: 'RFC',
          category: 'Parte Compradora',
        },
        {
          name: 'Parte_Compradora_CURP',
          label: 'CURP',
          category: 'Parte Compradora',
        },
        {
          name: 'Parte_Compradora_INE',
          label: 'Clave INE',
          category: 'Parte Compradora',
        },
        {
          name: 'Parte_Compradora_Domicilio',
          label: 'Domicilio',
          category: 'Parte Compradora',
          type: 'textarea',
        },

        // Inmueble
        {
          name: 'Inmueble_Direccion',
          label: 'Dirección del Inmueble',
          category: 'Inmueble',
          type: 'textarea',
          required: true,
        },
        {
          name: 'Inmueble_Superficie_Terreno',
          label: 'Superficie del Terreno',
          category: 'Inmueble',
        },
        {
          name: 'Inmueble_Superficie_Construccion',
          label: 'Superficie de Construcción',
          category: 'Inmueble',
        },
        {
          name: 'Inmueble_Precio',
          label: 'Precio de Venta',
          category: 'Inmueble',
          type: 'number',
          required: true,
        },
      ],
      // Add more document types as needed
    };

    return metadataMap[documentType] || [];
  }, [documentType]);

  // Group fields by category
  const fieldsByCategory = useMemo(() => {
    const grouped: Record<string, FieldMetadata[]> = {};

    fieldMetadata.forEach((field) => {
      if (!grouped[field.category]) {
        grouped[field.category] = [];
      }
      grouped[field.category].push(field);
    });

    return grouped;
  }, [fieldMetadata]);

  // Filter fields by search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return fieldsByCategory;

    const query = searchQuery.toLowerCase();
    const filtered: Record<string, FieldMetadata[]> = {};

    Object.entries(fieldsByCategory).forEach(([category, fields]) => {
      const matchingFields = fields.filter(
        (field) =>
          field.label.toLowerCase().includes(query) ||
          field.name.toLowerCase().includes(query)
      );

      if (matchingFields.length > 0) {
        filtered[category] = matchingFields;
      }
    });

    return filtered;
  }, [fieldsByCategory, searchQuery]);

  // Calculate statistics
  const stats = useMemo(() => {
    if (!editedData) return { total: 0, filled: 0, empty: 0, percentage: 0 };

    const total = fieldMetadata.length;
    const filled = fieldMetadata.filter((field) => {
      const value = editedData[field.name];
      return value !== null && value !== undefined && value !== '';
    }).length;
    const empty = total - filled;

    return {
      total,
      filled,
      empty,
      percentage: total > 0 ? Math.round((filled / total) * 100) : 0,
    };
  }, [editedData, fieldMetadata]);

  // Track changes
  useEffect(() => {
    if (!extractedData || !editedData) return;

    const changed = JSON.stringify(extractedData) !== JSON.stringify(editedData);
    setHasChanges(changed);
  }, [extractedData, editedData]);

  // Reset to extracted data
  const handleReset = () => {
    if (extractedData) {
      setEditedData(extractedData);
      setHasChanges(false);
    }
  };

  if (!editedData || !documentType) {
    return (
      <Alert>
        <AlertDescription>
          No hay datos para editar. Primero procesa un documento.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Editar Datos Extraídos</h2>
        <p className="text-muted-foreground mt-1">
          Revisa y corrige los datos extraídos por la IA
        </p>
      </div>

      {/* Statistics Dashboard */}
      <MetricsDashboard
        totalFields={stats.total}
        foundFields={stats.filled}
        emptyFields={stats.empty}
        completionRate={stats.percentage}
      />

      {/* Save Changes Indicator */}
      {hasChanges && (
        <div className="flex items-center justify-end gap-4">
          <Badge variant="secondary" className="gap-1">
            <Save className="w-3 h-3" />
            Cambios sin guardar
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            className="gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Resetear
          </Button>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar campos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Categories and fields */}
      <div className="space-y-4">
        {Object.entries(filteredCategories).map(([category, fields]) => {
          const categoryFilledCount = fields.filter((field) => {
            const value = editedData[field.name];
            return value !== null && value !== undefined && value !== '';
          }).length;

          return (
            <CategorySection
              key={category}
              title={category}
              fieldCount={fields.length}
              filledCount={categoryFilledCount}
            >
              {fields.map((field) => {
                const value = editedData[field.name];
                // Convert boolean values to string for FieldGroup
                const fieldValue = typeof value === 'boolean' ? String(value) : value;

                return (
                  <FieldGroup
                    key={field.name}
                    fieldName={field.name}
                    label={field.label}
                    value={fieldValue}
                    onChange={(value) => updateField(field.name, value)}
                    description={field.description}
                    type={field.type}
                    required={field.required}
                  />
                );
              })}
            </CategorySection>
          );
        })}

        {Object.keys(filteredCategories).length === 0 && (
          <Alert>
            <AlertDescription>
              No se encontraron campos que coincidan con "{searchQuery}"
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}
