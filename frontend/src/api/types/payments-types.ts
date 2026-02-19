/**
 * Payment Types
 * Types for case payment tracking
 */

export type PaymentTipo = 'honorarios' | 'impuestos' | 'derechos' | 'gastos' | 'otro';
export type PaymentMetodo = 'efectivo' | 'transferencia' | 'cheque' | 'tarjeta' | 'otro';

export const PAYMENT_TIPO_LABELS: Record<PaymentTipo, string> = {
  honorarios: 'Honorarios',
  impuestos: 'Impuestos',
  derechos: 'Derechos',
  gastos: 'Gastos',
  otro: 'Otro',
};

export const PAYMENT_METODO_LABELS: Record<PaymentMetodo, string> = {
  efectivo: 'Efectivo',
  transferencia: 'Transferencia',
  cheque: 'Cheque',
  tarjeta: 'Tarjeta',
  otro: 'Otro',
};

export interface CasePayment {
  id: string;
  tenant_id: string;
  case_id: string;
  tipo: PaymentTipo;
  concepto: string;
  monto: number;
  metodo_pago: PaymentMetodo;
  referencia?: string;
  fecha_pago: string;
  recibido_por?: string;
  comprobante_path?: string;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentTotals {
  by_tipo: Record<string, number>;
  total: number;
  count: number;
}

export interface PaymentListResponse {
  payments: CasePayment[];
  totals: PaymentTotals;
  limit: number;
  offset: number;
}

export interface PaymentCreateRequest {
  tipo: PaymentTipo;
  concepto: string;
  monto: number;
  metodo_pago?: PaymentMetodo;
  referencia?: string;
  fecha_pago?: string;
  recibido_por?: string;
  comprobante_path?: string;
  notas?: string;
}

export interface PaymentUpdateRequest {
  tipo?: PaymentTipo;
  concepto?: string;
  monto?: number;
  metodo_pago?: PaymentMetodo;
  referencia?: string;
  fecha_pago?: string;
  recibido_por?: string;
  comprobante_path?: string;
  notas?: string;
}
