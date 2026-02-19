-- =============================================
-- Migration 010: Calendar Events (Calendario)
-- =============================================
-- Adds: calendar_events table for scheduling
-- Types: vencimiento, firma, cita, audiencia, otro
-- =============================================

-- =============================================
-- 1. NEW TABLE: calendar_events
-- =============================================

CREATE TABLE IF NOT EXISTS calendar_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  tipo TEXT NOT NULL DEFAULT 'otro',
  fecha_inicio TIMESTAMPTZ NOT NULL,
  fecha_fin TIMESTAMPTZ,
  todo_el_dia BOOLEAN DEFAULT false,
  recordatorio_minutos INT DEFAULT 30,
  color TEXT DEFAULT '#3b82f6',
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT calendar_events_tipo_check
    CHECK (tipo IN ('vencimiento','firma','cita','audiencia','otro'))
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_calendar_events_tenant ON calendar_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_case ON calendar_events(case_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_fecha ON calendar_events(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_calendar_events_tipo ON calendar_events(tipo);

-- Trigger for updated_at
CREATE TRIGGER update_calendar_events_updated_at
  BEFORE UPDATE ON calendar_events
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 2. ROW LEVEL SECURITY
-- =============================================

ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY calendar_events_tenant_policy ON calendar_events
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY calendar_events_service_role ON calendar_events
  FOR ALL TO service_role
  USING (true);
