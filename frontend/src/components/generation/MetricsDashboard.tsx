/**
 * MetricsDashboard Component
 *
 * Displays 4 key metrics for document generation:
 * - Total fields in template
 * - Fields found by extraction
 * - Empty fields requiring attention
 * - Completion rate percentage
 *
 * Layout: 2x2 grid on mobile, 4 columns on desktop
 */

import React from 'react';
import { Card } from '@/components/ui/card';

interface MetricsDashboardProps {
  totalFields: number;
  foundFields: number;
  emptyFields: number;
  completionRate: number;
  optionalMissing?: number;
}

interface MetricCardProps {
  value: number | string;
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'info';
}

const MetricCard: React.FC<MetricCardProps> = ({ value, label, variant = 'default' }) => {
  const variantStyles = {
    default: 'text-primary-500',
    success: 'text-success',
    warning: 'text-warning',
    info: 'text-info',
  };

  return (
    <Card className="p-4 text-center shadow-card hover:shadow-card-hover transition-shadow">
      <div className={`text-3xl md:text-4xl font-bold ${variantStyles[variant]} mb-1`}>
        {value}
      </div>
      <div className="text-sm md:text-base text-neutral-600 font-medium">
        {label}
      </div>
    </Card>
  );
};

export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({
  totalFields,
  foundFields,
  emptyFields,
  completionRate,
  optionalMissing = 0,
}) => {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-neutral-900 mb-4">
        📊 Estadísticas de Extracción
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          value={totalFields}
          label="Total Campos"
          variant="default"
        />

        <MetricCard
          value={foundFields}
          label="Encontrados"
          variant="success"
        />

        <MetricCard
          value={emptyFields}
          label="Vacíos"
          variant={emptyFields > 0 ? 'warning' : 'success'}
        />

        <MetricCard
          value={`${completionRate}%`}
          label="Completado"
          variant={
            completionRate === 100
              ? 'success'
              : completionRate >= 70
              ? 'info'
              : 'warning'
          }
        />
      </div>

      {emptyFields > 0 && (
        <div className="mt-4 p-3 bg-warning/10 border border-warning/20 rounded-lg">
          <p className="text-sm text-warning-700 font-medium">
            Faltan {emptyFields} campo{emptyFields !== 1 ? 's requeridos' : ' requerido'} por completar
          </p>
          <p className="text-xs text-warning-600 mt-1">
            Todos los campos requeridos deben estar llenos antes de generar el documento.
          </p>
        </div>
      )}

      {emptyFields === 0 && optionalMissing > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700 font-medium">
            Todos los campos requeridos completos. {optionalMissing} campo{optionalMissing !== 1 ? 's opcionales' : ' opcional'} sin datos de documentos ausentes.
          </p>
        </div>
      )}
    </div>
  );
};

export default MetricsDashboard;
