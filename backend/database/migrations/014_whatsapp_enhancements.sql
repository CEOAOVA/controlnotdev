-- =============================================
-- Migration 014: WhatsApp Enhancements
-- =============================================
-- Adds: wa_phone_tenant_map (multi-tenant webhook routing)
--        wa_document_extractions (document processing tracking)
-- =============================================

-- =============================================
-- 1. wa_phone_tenant_map
-- Maps WhatsApp phone_number_id to tenant for webhook routing
-- =============================================

CREATE TABLE IF NOT EXISTS wa_phone_tenant_map (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number_id TEXT NOT NULL UNIQUE,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wa_phone_tenant_phone ON wa_phone_tenant_map(phone_number_id);

ALTER TABLE wa_phone_tenant_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_phone_tenant_map_service_role ON wa_phone_tenant_map
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 2. wa_document_extractions
-- Tracks documents processed via WhatsApp pipeline
-- =============================================

CREATE TABLE IF NOT EXISTS wa_document_extractions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  message_id UUID REFERENCES wa_messages(id) ON DELETE SET NULL,
  case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
  document_type TEXT,
  extracted_data JSONB DEFAULT '{}',
  confidence FLOAT DEFAULT 0.0,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wa_doc_extractions_tenant ON wa_document_extractions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wa_doc_extractions_case ON wa_document_extractions(case_id);
CREATE INDEX IF NOT EXISTS idx_wa_doc_extractions_message ON wa_document_extractions(message_id);

ALTER TABLE wa_document_extractions ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_doc_extractions_tenant_policy ON wa_document_extractions
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_doc_extractions_service_role ON wa_document_extractions
  FOR ALL TO service_role
  USING (true);
