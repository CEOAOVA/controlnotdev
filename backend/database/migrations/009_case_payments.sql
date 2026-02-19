-- =============================================
-- Migration 009: Case Payments (Pagos)
-- =============================================
-- Adds: case_payments table for tracking manual payments
-- Types: honorarios, impuestos, derechos, gastos, otro
-- Methods: efectivo, transferencia, cheque, tarjeta, otro
-- =============================================

-- =============================================
-- 1. NEW TABLE: case_payments
-- =============================================

CREATE TABLE IF NOT EXISTS case_payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL,
  concepto TEXT NOT NULL,
  monto NUMERIC(12,2) NOT NULL CHECK (monto > 0),
  metodo_pago TEXT NOT NULL DEFAULT 'efectivo',
  referencia TEXT,
  fecha_pago TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  recibido_por TEXT,
  comprobante_path TEXT,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT case_payments_tipo_check
    CHECK (tipo IN ('honorarios','impuestos','derechos','gastos','otro')),
  CONSTRAINT case_payments_metodo_check
    CHECK (metodo_pago IN ('efectivo','transferencia','cheque','tarjeta','otro'))
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_case_payments_tenant ON case_payments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_payments_case ON case_payments(case_id);
CREATE INDEX IF NOT EXISTS idx_case_payments_tipo ON case_payments(tipo);
CREATE INDEX IF NOT EXISTS idx_case_payments_fecha ON case_payments(fecha_pago);

-- Trigger for updated_at
CREATE TRIGGER update_case_payments_updated_at
  BEFORE UPDATE ON case_payments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 2. ROW LEVEL SECURITY
-- =============================================

ALTER TABLE case_payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY case_payments_tenant_policy ON case_payments
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY case_payments_service_role ON case_payments
  FOR ALL TO service_role
  USING (true);
