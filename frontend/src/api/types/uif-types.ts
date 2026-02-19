/**
 * UIF/PLD Types
 * Types for vulnerable operations tracking
 */

export type UIFTipoOperacion = 'compraventa' | 'donacion' | 'fideicomiso' | 'poder' | 'otro';
export type UIFNivelRiesgo = 'bajo' | 'medio' | 'alto' | 'critico';
export type UIFStatus = 'pendiente' | 'reportado' | 'archivado';

export const UIF_RIESGO_LABELS: Record<UIFNivelRiesgo, string> = {
  bajo: 'Bajo',
  medio: 'Medio',
  alto: 'Alto',
  critico: 'Critico',
};

export const UIF_RIESGO_COLORS: Record<UIFNivelRiesgo, string> = {
  bajo: 'bg-green-100 text-green-700',
  medio: 'bg-yellow-100 text-yellow-700',
  alto: 'bg-orange-100 text-orange-700',
  critico: 'bg-red-100 text-red-700',
};

export const UIF_STATUS_LABELS: Record<UIFStatus, string> = {
  pendiente: 'Pendiente',
  reportado: 'Reportado',
  archivado: 'Archivado',
};

export interface UIFOperation {
  id: string;
  tenant_id: string;
  case_id: string;
  tipo_operacion: UIFTipoOperacion;
  monto_operacion: number;
  nivel_riesgo: UIFNivelRiesgo;
  es_vulnerable: boolean;
  umbral_aplicado: number;
  requiere_aviso: boolean;
  fecha_aviso?: string;
  numero_aviso?: string;
  status: UIFStatus;
  responsable_id?: string;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface UIFSummary {
  total: number;
  vulnerables: number;
  by_status: Record<string, number>;
  by_riesgo: Record<string, number>;
}

export interface UIFListResponse {
  operations: UIFOperation[];
  summary: UIFSummary;
}

export interface UIFCheckResponse {
  flagged: boolean;
  operation: UIFOperation | null;
}
