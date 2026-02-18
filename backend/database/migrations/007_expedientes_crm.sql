-- =============================================
-- Migration 007: Expedientes CRM Completo
-- =============================================
-- Adds: case_parties, case_checklist, case_tramites,
--        case_activity_log, catalogo_checklist_templates
-- Alters: cases (new fields + workflow statuses),
--         users (expanded roles), audit_logs (new actions)
-- =============================================

-- =============================================
-- 1. ALTER TABLE cases - New fields + workflow status
-- =============================================

-- Add new columns
ALTER TABLE cases ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'normal';
ALTER TABLE cases ADD COLUMN IF NOT EXISTS escritura_number TEXT;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS volumen TEXT;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS folio_real TEXT;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS valor_operacion NUMERIC(15,2);
ALTER TABLE cases ADD COLUMN IF NOT EXISTS fecha_firma TIMESTAMPTZ;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS fecha_cierre TIMESTAMPTZ;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE cases ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';

-- Add priority check
ALTER TABLE cases ADD CONSTRAINT cases_priority_check
  CHECK (priority IN ('baja','normal','alta','urgente'));

-- Expand status CHECK (drop old + add new)
ALTER TABLE cases DROP CONSTRAINT IF EXISTS cases_status_check;
ALTER TABLE cases ADD CONSTRAINT cases_status_check CHECK (status IN (
  'draft','documents_uploaded','ocr_processing','data_extracted','validated',
  'document_generated','signed','completed','cancelled',
  'borrador','en_revision','checklist_pendiente','presupuesto','calculo_impuestos',
  'en_firma','postfirma','tramites_gobierno','inscripcion','facturacion',
  'entrega','cerrado','cancelado','suspendido'
));

-- Migrate existing row statuses to new workflow values
UPDATE cases SET status = 'borrador' WHERE status = 'draft';

-- Index for assigned_to queries
CREATE INDEX IF NOT EXISTS idx_cases_assigned_to ON cases(assigned_to);
CREATE INDEX IF NOT EXISTS idx_cases_priority ON cases(priority);
CREATE INDEX IF NOT EXISTS idx_cases_fecha_firma ON cases(fecha_firma);

-- =============================================
-- 2. ALTER TABLE users - Expand roles
-- =============================================
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_rol_check;
ALTER TABLE users ADD CONSTRAINT users_rol_check CHECK (
  rol IN ('admin','notario','abogado','asistente','mesa_control','pagos','folios_protocolo','archivo')
);

-- =============================================
-- 3. ALTER TABLE audit_logs - Expand actions
-- =============================================
ALTER TABLE audit_logs DROP CONSTRAINT IF EXISTS audit_logs_action_check;
ALTER TABLE audit_logs ADD CONSTRAINT audit_logs_action_check CHECK (action IN (
  'create_client','update_client','delete_client',
  'create_case','update_case','complete_case','cancel_case',
  'upload_documents','start_ocr','complete_ocr',
  'extract_data','validate_data','generate_document',
  'download_document','sign_document',
  'upload_template','delete_template',
  'login','logout',
  'auth_login_success','auth_login_failed','auth_logout','auth_signup','auth_password_reset',
  'transition_case','suspend_case','resume_case',
  'add_party','update_party','remove_party',
  'initialize_checklist','update_checklist_item',
  'create_tramite','complete_tramite','add_case_note'
));

-- =============================================
-- 4. Table: case_parties
-- =============================================
CREATE TABLE IF NOT EXISTS case_parties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
  role TEXT NOT NULL,
  nombre TEXT NOT NULL,
  rfc TEXT,
  tipo_persona TEXT,
  email TEXT,
  telefono TEXT,
  representante_legal TEXT,
  poder_notarial TEXT,
  orden INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(case_id, client_id, role)
);

CREATE INDEX IF NOT EXISTS idx_case_parties_tenant ON case_parties(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_parties_case ON case_parties(case_id);

-- Trigger for updated_at
CREATE TRIGGER update_case_parties_updated_at
  BEFORE UPDATE ON case_parties
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE case_parties ENABLE ROW LEVEL SECURITY;

CREATE POLICY case_parties_tenant_policy ON case_parties
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY case_parties_service_role ON case_parties
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 5. Table: case_checklist
-- =============================================
CREATE TABLE IF NOT EXISTS case_checklist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  categoria TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pendiente',
  obligatorio BOOLEAN DEFAULT true,
  uploaded_file_id UUID,
  storage_path TEXT,
  fecha_solicitud TIMESTAMPTZ,
  fecha_recepcion TIMESTAMPTZ,
  fecha_vencimiento TIMESTAMPTZ,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT case_checklist_status_check CHECK (
    status IN ('pendiente','solicitado','recibido','aprobado','rechazado','no_aplica')
  ),
  CONSTRAINT case_checklist_categoria_check CHECK (
    categoria IN ('parte_a','parte_b','inmueble','fiscal','gobierno','general')
  )
);

CREATE INDEX IF NOT EXISTS idx_case_checklist_tenant ON case_checklist(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_checklist_case ON case_checklist(case_id);
CREATE INDEX IF NOT EXISTS idx_case_checklist_status ON case_checklist(status);

CREATE TRIGGER update_case_checklist_updated_at
  BEFORE UPDATE ON case_checklist
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE case_checklist ENABLE ROW LEVEL SECURITY;

CREATE POLICY case_checklist_tenant_policy ON case_checklist
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY case_checklist_service_role ON case_checklist
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 6. Table: case_tramites
-- =============================================
CREATE TABLE IF NOT EXISTS case_tramites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  tipo TEXT NOT NULL,
  nombre TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pendiente',
  fecha_inicio TIMESTAMPTZ,
  fecha_limite TIMESTAMPTZ,
  fecha_completado TIMESTAMPTZ,
  resultado TEXT,
  costo NUMERIC(12,2),
  depende_de UUID REFERENCES case_tramites(id) ON DELETE SET NULL,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT case_tramites_status_check CHECK (
    status IN ('pendiente','en_proceso','completado','cancelado','vencido')
  )
);

CREATE INDEX IF NOT EXISTS idx_case_tramites_tenant ON case_tramites(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_tramites_case ON case_tramites(case_id);
CREATE INDEX IF NOT EXISTS idx_case_tramites_status ON case_tramites(status);
CREATE INDEX IF NOT EXISTS idx_case_tramites_fecha_limite ON case_tramites(fecha_limite);
CREATE INDEX IF NOT EXISTS idx_case_tramites_assigned ON case_tramites(assigned_to);

CREATE TRIGGER update_case_tramites_updated_at
  BEFORE UPDATE ON case_tramites
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE case_tramites ENABLE ROW LEVEL SECURITY;

CREATE POLICY case_tramites_tenant_policy ON case_tramites
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY case_tramites_service_role ON case_tramites
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 7. Table: case_activity_log
-- =============================================
CREATE TABLE IF NOT EXISTS case_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  description TEXT,
  entity_type TEXT,
  entity_id UUID,
  old_value JSONB,
  new_value JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_case_activity_tenant ON case_activity_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_activity_case ON case_activity_log(case_id);
CREATE INDEX IF NOT EXISTS idx_case_activity_action ON case_activity_log(action);
CREATE INDEX IF NOT EXISTS idx_case_activity_created ON case_activity_log(created_at);

ALTER TABLE case_activity_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY case_activity_tenant_policy ON case_activity_log
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY case_activity_service_role ON case_activity_log
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 8. Table: catalogo_checklist_templates
-- =============================================
CREATE TABLE IF NOT EXISTS catalogo_checklist_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  document_type TEXT NOT NULL,
  nombre TEXT NOT NULL,
  categoria TEXT NOT NULL,
  obligatorio BOOLEAN DEFAULT true,
  orden INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT catalogo_checklist_categoria_check CHECK (
    categoria IN ('parte_a','parte_b','inmueble','fiscal','gobierno','general')
  )
);

CREATE INDEX IF NOT EXISTS idx_catalogo_checklist_doctype ON catalogo_checklist_templates(document_type);
CREATE INDEX IF NOT EXISTS idx_catalogo_checklist_tenant ON catalogo_checklist_templates(tenant_id);

CREATE TRIGGER update_catalogo_checklist_updated_at
  BEFORE UPDATE ON catalogo_checklist_templates
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE catalogo_checklist_templates ENABLE ROW LEVEL SECURITY;

-- System defaults (tenant_id IS NULL) are readable by all authenticated users
-- Tenant-specific templates are only visible to that tenant
CREATE POLICY catalogo_checklist_read_policy ON catalogo_checklist_templates
  FOR SELECT TO authenticated
  USING (
    tenant_id IS NULL
    OR tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY catalogo_checklist_write_policy ON catalogo_checklist_templates
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY catalogo_checklist_service_role ON catalogo_checklist_templates
  FOR ALL TO service_role
  USING (true);
