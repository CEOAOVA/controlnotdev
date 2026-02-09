/**
 * DataEditor Component
 * Main editor for reviewing and editing extracted document data
 *
 * Now uses dynamic field metadata from API instead of hardcoded values
 */

import { useEffect, useMemo, useState } from 'react';
import { Search, RotateCcw, Save, Loader2, Shield, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CategorySection } from './CategorySection';
import { FieldGroup } from './FieldGroup';
import { useDocumentStore } from '@/store';
import { useFieldMetadata } from '@/hooks';
import { MetricsDashboard } from '@/components/generation/MetricsDashboard';
import type { FieldMetadata } from '@/api/types';

export function DataEditor() {
  const {
    extractedData,
    editedData,
    updateField,
    setEditedData,
    documentType,
    validationReport,
    perFieldConfidence,
    perFieldValidation,
  } = useDocumentStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch field metadata dynamically from API
  const {
    fields: fieldMetadata,
    isLoading: isLoadingFields,
    isError,
    error,
    getFieldsByCategory,
  } = useFieldMetadata(documentType);

  // Group fields by category
  const fieldsByCategory = useMemo(() => {
    if (!fieldMetadata || fieldMetadata.length === 0) {
      return {};
    }
    return getFieldsByCategory();
  }, [fieldMetadata, getFieldsByCategory]);

  // Filter fields by search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return fieldsByCategory;

    const query = searchQuery.toLowerCase();
    const filtered: Record<string, FieldMetadata[]> = {};

    Object.entries(fieldsByCategory).forEach(([category, fields]) => {
      const matchingFields = fields.filter(
        (field) =>
          field.label.toLowerCase().includes(query) ||
          field.name.toLowerCase().includes(query) ||
          (field.help && field.help.toLowerCase().includes(query))
      );

      if (matchingFields.length > 0) {
        filtered[category] = matchingFields;
      }
    });

    return filtered;
  }, [fieldsByCategory, searchQuery]);

  // Helper function to check if a field value is actually filled
  // Excludes null, undefined, empty strings, and "NO ENCONTRADO" markers
  const isFieldFilled = (value: unknown): boolean => {
    if (value === null || value === undefined || value === '') return false;
    if (typeof value === 'string' && value.toUpperCase().includes('NO ENCONTRADO')) return false;
    return true;
  };

  // Calculate statistics (separating required vs optional)
  const stats = useMemo(() => {
    if (!editedData || !fieldMetadata) return { total: 0, filled: 0, empty: 0, percentage: 0, optionalMissing: 0 };

    const requiredFields = fieldMetadata.filter(f => !f.optional);
    const optionalFields = fieldMetadata.filter(f => f.optional);

    const requiredFilled = requiredFields.filter(f => isFieldFilled(editedData[f.name])).length;
    const optionalFilled = optionalFields.filter(f => isFieldFilled(editedData[f.name])).length;

    const total = requiredFields.length;
    const filled = requiredFilled;
    const empty = total - filled;
    const optionalMissing = optionalFields.length - optionalFilled;

    return {
      total,
      filled,
      empty,
      percentage: total > 0 ? Math.round((filled / total) * 100) : 0,
      optionalMissing,
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

  // Loading state
  if (isLoadingFields) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Cargando campos del documento...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Error al cargar los campos: {error?.message || 'Error desconocido'}
        </AlertDescription>
      </Alert>
    );
  }

  // No data state
  if (!editedData || !documentType) {
    return (
      <Alert>
        <AlertDescription>
          No hay datos para editar. Primero procesa un documento.
        </AlertDescription>
      </Alert>
    );
  }

  // No fields found
  if (fieldMetadata.length === 0) {
    return (
      <Alert>
        <AlertDescription>
          No se encontraron campos para el tipo de documento "{documentType}".
          Verifica que el tipo sea correcto.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Editar Datos Extraidos</h2>
        <p className="text-muted-foreground mt-1">
          Revisa y corrige los datos extraidos por la IA
        </p>
      </div>

      {/* Statistics Dashboard */}
      <MetricsDashboard
        totalFields={stats.total}
        foundFields={stats.filled}
        emptyFields={stats.empty}
        completionRate={stats.percentage}
        optionalMissing={stats.optionalMissing}
      />

      {/* OCR Robusto 2025: Validation Summary */}
      {validationReport && (
        <div className="bg-muted/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Validación de Datos
            </h3>
            <Badge variant={validationReport.overall_confidence >= 0.8 ? 'default' : 'secondary'}>
              {Math.round(validationReport.overall_confidence * 100)}% confianza general
            </Badge>
          </div>
          <div className="grid grid-cols-1 xs:grid-cols-3 gap-2 sm:gap-3">
            <div className="flex items-center gap-2 p-2 bg-background rounded border">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
              <div>
                <p className="text-lg font-semibold">{validationReport.valid_fields}</p>
                <p className="text-xs text-muted-foreground">Válidos</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-background rounded border">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
              <div>
                <p className="text-lg font-semibold">{validationReport.suspicious_fields}</p>
                <p className="text-xs text-muted-foreground">Sospechosos</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-background rounded border">
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <div>
                <p className="text-lg font-semibold">{validationReport.invalid_fields}</p>
                <p className="text-xs text-muted-foreground">Inválidos</p>
              </div>
            </div>
          </div>
          {(validationReport.suspicious_fields > 0 || validationReport.invalid_fields > 0) && (
            <p className="text-sm text-muted-foreground mt-3">
              Revisa los campos marcados en amarillo/rojo antes de generar el documento.
            </p>
          )}
        </div>
      )}

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
          const categoryRequiredFields = fields.filter(f => !f.optional);
          const categoryFilledCount = categoryRequiredFields.filter(f => isFieldFilled(editedData[f.name])).length;
          const categoryOptionalMissing = fields.filter(f => f.optional && !isFieldFilled(editedData[f.name])).length;

          return (
            <CategorySection
              key={category}
              title={category}
              fieldCount={categoryRequiredFields.length}
              filledCount={categoryFilledCount}
              optionalMissing={categoryOptionalMissing}
            >
              {fields.map((field) => {
                const value = editedData[field.name];
                // Convert boolean values to string for FieldGroup
                const fieldValue = typeof value === 'boolean' ? String(value) : value;

                // Map 'date' type to 'text' (dates are in words in notarial docs)
                const inputType = field.type === 'date' ? 'text' : field.type;

                // OCR Robusto 2025: Get per-field confidence and validation
                const fieldConfidence = perFieldConfidence[field.name];
                const fieldValidation = perFieldValidation[field.name];

                return (
                  <FieldGroup
                    key={field.name}
                    fieldName={field.name}
                    label={field.label}
                    value={fieldValue}
                    onChange={(value) => updateField(field.name, value)}
                    description={field.help}
                    type={inputType}
                    required={field.required}
                    optional={field.optional}
                    source={field.source}
                    confidence={fieldConfidence}
                    validationStatus={fieldValidation?.status}
                    validationIssues={fieldValidation?.issues}
                  />
                );
              })}
            </CategorySection>
          );
        })}

        {Object.keys(filteredCategories).length === 0 && searchQuery && (
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
