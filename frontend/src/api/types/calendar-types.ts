/**
 * Calendar Types
 * Types for calendar events
 */

export type EventTipo = 'vencimiento' | 'firma' | 'cita' | 'audiencia' | 'otro';

export const EVENT_TIPO_LABELS: Record<EventTipo, string> = {
  vencimiento: 'Vencimiento',
  firma: 'Firma',
  cita: 'Cita',
  audiencia: 'Audiencia',
  otro: 'Otro',
};

export const EVENT_TIPO_COLORS: Record<EventTipo, string> = {
  vencimiento: '#ef4444',
  firma: '#22c55e',
  cita: '#3b82f6',
  audiencia: '#a855f7',
  otro: '#6b7280',
};

export interface CalendarEvent {
  id: string;
  tenant_id: string;
  case_id?: string;
  titulo: string;
  descripcion?: string;
  tipo: EventTipo;
  fecha_inicio: string;
  fecha_fin?: string;
  todo_el_dia: boolean;
  recordatorio_minutos: number;
  color: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface EventCreateRequest {
  titulo: string;
  tipo?: EventTipo;
  descripcion?: string;
  case_id?: string;
  fecha_inicio: string;
  fecha_fin?: string;
  todo_el_dia?: boolean;
  recordatorio_minutos?: number;
  color?: string;
}

export interface EventUpdateRequest {
  titulo?: string;
  tipo?: EventTipo;
  descripcion?: string;
  case_id?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  todo_el_dia?: boolean;
  recordatorio_minutos?: number;
  color?: string;
}

export interface CalendarEventsResponse {
  events: CalendarEvent[];
}
