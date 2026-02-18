/**
 * Cases CRM API Types
 * Types for cases/expedientes management with 14-status workflow
 */

import type { DocumentType } from '@/types';

// ===========================
// STATUS & WORKFLOW
// ===========================

export const CASE_STATUSES = [
  'borrador', 'en_revision', 'checklist_pendiente', 'presupuesto',
  'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
  'inscripcion', 'facturacion', 'entrega', 'cerrado', 'cancelado', 'suspendido'
] as const;

export type CaseStatus = typeof CASE_STATUSES[number];

export const STATUS_LABELS: Record<CaseStatus, string> = {
  borrador: 'Borrador',
  en_revision: 'En Revision',
  checklist_pendiente: 'Checklist Pendiente',
  presupuesto: 'Presupuesto',
  calculo_impuestos: 'Calculo de Impuestos',
  en_firma: 'En Firma',
  postfirma: 'Post-Firma',
  tramites_gobierno: 'Tramites de Gobierno',
  inscripcion: 'Inscripcion',
  facturacion: 'Facturacion',
  entrega: 'Entrega',
  cerrado: 'Cerrado',
  cancelado: 'Cancelado',
  suspendido: 'Suspendido',
};

export const STATUS_COLORS: Record<CaseStatus, string> = {
  borrador: 'bg-gray-100 text-gray-700',
  en_revision: 'bg-blue-100 text-blue-700',
  checklist_pendiente: 'bg-yellow-100 text-yellow-700',
  presupuesto: 'bg-purple-100 text-purple-700',
  calculo_impuestos: 'bg-orange-100 text-orange-700',
  en_firma: 'bg-indigo-100 text-indigo-700',
  postfirma: 'bg-teal-100 text-teal-700',
  tramites_gobierno: 'bg-cyan-100 text-cyan-700',
  inscripcion: 'bg-lime-100 text-lime-700',
  facturacion: 'bg-amber-100 text-amber-700',
  entrega: 'bg-emerald-100 text-emerald-700',
  cerrado: 'bg-green-100 text-green-700',
  cancelado: 'bg-red-100 text-red-700',
  suspendido: 'bg-rose-100 text-rose-700',
};

export type CasePriority = 'baja' | 'normal' | 'alta' | 'urgente';
export type ChecklistStatus = 'pendiente' | 'solicitado' | 'recibido' | 'aprobado' | 'rechazado' | 'no_aplica';
export type ChecklistCategoria = 'parte_a' | 'parte_b' | 'inmueble' | 'fiscal' | 'gobierno' | 'general';
export type TramiteSemaforo = 'verde' | 'amarillo' | 'rojo' | 'gris';

// ===========================
// CASE
// ===========================

export interface Case {
  id: string;
  tenant_id: string;
  client_id: string;
  case_number: string;
  document_type: DocumentType;
  status: CaseStatus;
  parties: Record<string, any>[];
  description?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  assigned_to?: string;
  priority?: CasePriority;
  escritura_number?: string;
  volumen?: string;
  folio_real?: string;
  valor_operacion?: number;
  fecha_firma?: string;
  fecha_cierre?: string;
  notas?: string;
  tags?: string[];
}

export interface CaseWithClient extends Case {
  client?: Record<string, any>;
}

export interface CaseDetail extends CaseWithClient {
  case_parties: CaseParty[];
  checklist_summary?: ChecklistSummary;
  tramites_summary?: SemaforoSummary;
  available_transitions: Transition[];
}

export interface CaseListResponse {
  cases: Case[];
  total: number;
  page: number;
  page_size: number;
}

// ===========================
// PARTIES
// ===========================

export interface CaseParty {
  id: string;
  tenant_id: string;
  case_id: string;
  client_id?: string;
  role: string;
  nombre: string;
  rfc?: string;
  tipo_persona?: 'fisica' | 'moral';
  email?: string;
  telefono?: string;
  representante_legal?: string;
  poder_notarial?: string;
  orden: number;
  created_at: string;
  updated_at: string;
}

// ===========================
// CHECKLIST
// ===========================

export interface ChecklistItem {
  id: string;
  tenant_id: string;
  case_id: string;
  nombre: string;
  categoria: ChecklistCategoria;
  status: ChecklistStatus;
  obligatorio: boolean;
  uploaded_file_id?: string;
  storage_path?: string;
  fecha_solicitud?: string;
  fecha_recepcion?: string;
  fecha_vencimiento?: string;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface ChecklistSummary {
  total: number;
  by_status: Record<ChecklistStatus, number>;
  obligatorios: number;
  obligatorios_completados: number;
  completion_pct: number;
  all_required_complete: boolean;
}

// ===========================
// TRAMITES
// ===========================

export interface Tramite {
  id: string;
  tenant_id: string;
  case_id: string;
  assigned_to?: string;
  tipo: string;
  nombre: string;
  status: string;
  fecha_inicio?: string;
  fecha_limite?: string;
  fecha_completado?: string;
  resultado?: string;
  costo?: number;
  depende_de?: string;
  notas?: string;
  semaforo?: TramiteSemaforo;
  created_at: string;
  updated_at: string;
}

export interface SemaforoSummary {
  verde: number;
  amarillo: number;
  rojo: number;
  gris: number;
  total: number;
}

// ===========================
// WORKFLOW & ACTIVITY
// ===========================

export interface Transition {
  status: CaseStatus;
  label: string;
}

export interface TransitionResponse {
  current_status: CaseStatus;
  current_label: string;
  transitions: Transition[];
}

export interface CaseTimeline {
  case_id: string;
  events: Record<string, any>[];
  total: number;
  limit: number;
  offset: number;
}

// ===========================
// DASHBOARD
// ===========================

export interface CaseDashboard {
  total_cases: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  semaforo_global: SemaforoSummary;
  overdue_tramites: number;
  upcoming_tramites: number;
}

export interface CaseStatistics {
  total_cases: number;
  by_status: Record<string, number>;
  by_document_type: Record<string, number>;
}

// ===========================
// CATALOGO
// ===========================

export interface CatalogoChecklist {
  id: string;
  tenant_id?: string;
  document_type: string;
  nombre: string;
  categoria: ChecklistCategoria;
  obligatorio: boolean;
  orden: number;
  created_at: string;
  updated_at: string;
}

// ===========================
// REQUEST TYPES
// ===========================

export interface CaseListParams {
  status?: CaseStatus;
  document_type?: string;
  priority?: CasePriority;
  assigned_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface CaseCreateRequest {
  client_id: string;
  case_number: string;
  document_type: string;
  description?: string;
  priority?: CasePriority;
  assigned_to?: string;
  valor_operacion?: number;
  fecha_firma?: string;
  notas?: string;
  tags?: string[];
}

export interface CaseUpdateRequest {
  description?: string;
  priority?: CasePriority;
  assigned_to?: string;
  escritura_number?: string;
  volumen?: string;
  folio_real?: string;
  valor_operacion?: number;
  fecha_firma?: string;
  fecha_cierre?: string;
  notas?: string;
  tags?: string[];
}

export interface PartyCreateRequest {
  role: string;
  nombre: string;
  client_id?: string;
  rfc?: string;
  tipo_persona?: 'fisica' | 'moral';
  email?: string;
  telefono?: string;
  representante_legal?: string;
  poder_notarial?: string;
  orden?: number;
}

export interface TramiteCreateRequest {
  tipo: string;
  nombre: string;
  assigned_to?: string;
  fecha_limite?: string;
  costo?: number;
  depende_de?: string;
  notas?: string;
}

export interface ChecklistCreateRequest {
  nombre: string;
  categoria: ChecklistCategoria;
  obligatorio?: boolean;
  notas?: string;
}
