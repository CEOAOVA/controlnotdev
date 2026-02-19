-- =============================================
-- Migration 011: UIF / PLD (Actividades Vulnerables)
-- =============================================
-- Adds: uif_operations table for tracking vulnerable operations
-- Auto-detection of operations exceeding UIF thresholds
-- =============================================

-- =============================================
-- 1. NEW TABLE: uif_operations
-- =============================================

CREATE TABLE IF NOT EXISTS uif_operations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  tipo_operacion TEXT NOT NULL DEFAULT 'otro',
  monto_operacion NUMERIC(14,2) NOT NULL DEFAULT 0,
  nivel_riesgo TEXT NOT NULL DEFAULT 'bajo',
  es_vulnerable BOOLEAN DEFAULT false,
  umbral_aplicado NUMERIC(14,2),
  requiere_aviso BOOLEAN DEFAULT false,
  fecha_aviso TIMESTAMPTZ,
  numero_aviso TEXT,
  status TEXT NOT NULL DEFAULT 'pendiente',
  responsable_id UUID REFERENCES users(id) ON DELETE SET NULL,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT uif_tipo_operacion_check
    CHECK (tipo_operacion IN ('compraventa','donacion','fideicomiso','poder','otro')),
  CONSTRAINT uif_nivel_riesgo_check
    CHECK (nivel_riesgo IN ('bajo','medio','alto','critico')),
  CONSTRAINT uif_status_check
    CHECK (status IN ('pendiente','reportado','archivado'))
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_uif_operations_tenant ON uif_operations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_uif_operations_case ON uif_operations(case_id);
CREATE INDEX IF NOT EXISTS idx_uif_operations_status ON uif_operations(status);
CREATE INDEX IF NOT EXISTS idx_uif_operations_riesgo ON uif_operations(nivel_riesgo);
CREATE INDEX IF NOT EXISTS idx_uif_operations_vulnerable ON uif_operations(es_vulnerable);

-- Trigger for updated_at
CREATE TRIGGER update_uif_operations_updated_at
  BEFORE UPDATE ON uif_operations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 2. ROW LEVEL SECURITY
-- =============================================

ALTER TABLE uif_operations ENABLE ROW LEVEL SECURITY;

CREATE POLICY uif_operations_tenant_policy ON uif_operations
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY uif_operations_service_role ON uif_operations
  FOR ALL TO service_role
  USING (true);
