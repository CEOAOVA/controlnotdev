-- =============================================
-- Migration 012: WhatsApp Integration
-- =============================================
-- Adds: wa_contacts, wa_conversations, wa_messages,
--        wa_templates, wa_notification_rules
-- Based on devwhats-phase1-clean schema design
-- =============================================

-- =============================================
-- 1. wa_contacts
-- =============================================

CREATE TABLE IF NOT EXISTS wa_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  phone TEXT NOT NULL,
  name TEXT,
  client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
  is_blocked BOOLEAN DEFAULT false,
  last_seen TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(tenant_id, phone)
);

CREATE INDEX IF NOT EXISTS idx_wa_contacts_tenant ON wa_contacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wa_contacts_phone ON wa_contacts(phone);
CREATE INDEX IF NOT EXISTS idx_wa_contacts_client ON wa_contacts(client_id);

CREATE TRIGGER update_wa_contacts_updated_at
  BEFORE UPDATE ON wa_contacts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE wa_contacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_contacts_tenant_policy ON wa_contacts
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_contacts_service_role ON wa_contacts
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 2. wa_conversations
-- =============================================

CREATE TABLE IF NOT EXISTS wa_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  contact_id UUID NOT NULL REFERENCES wa_contacts(id) ON DELETE CASCADE,
  case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'open',
  last_message_at TIMESTAMPTZ,
  last_message_preview TEXT,
  unread_count INT DEFAULT 0,
  ai_enabled BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT wa_conversations_status_check
    CHECK (status IN ('open','closed','pending'))
);

CREATE INDEX IF NOT EXISTS idx_wa_conversations_tenant ON wa_conversations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wa_conversations_contact ON wa_conversations(contact_id);
CREATE INDEX IF NOT EXISTS idx_wa_conversations_case ON wa_conversations(case_id);
CREATE INDEX IF NOT EXISTS idx_wa_conversations_status ON wa_conversations(status);
CREATE INDEX IF NOT EXISTS idx_wa_conversations_last_msg ON wa_conversations(last_message_at DESC);

CREATE TRIGGER update_wa_conversations_updated_at
  BEFORE UPDATE ON wa_conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE wa_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_conversations_tenant_policy ON wa_conversations
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_conversations_service_role ON wa_conversations
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 3. wa_messages
-- =============================================

CREATE TABLE IF NOT EXISTS wa_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  conversation_id UUID NOT NULL REFERENCES wa_conversations(id) ON DELETE CASCADE,
  whatsapp_message_id TEXT UNIQUE,
  sender_type TEXT NOT NULL DEFAULT 'client',
  sender_id TEXT,
  content TEXT,
  message_type TEXT NOT NULL DEFAULT 'text',
  media_url TEXT,
  media_path TEXT,
  status TEXT NOT NULL DEFAULT 'sent',
  reply_to_id UUID REFERENCES wa_messages(id) ON DELETE SET NULL,
  metadata JSONB DEFAULT '{}',
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT wa_messages_sender_type_check
    CHECK (sender_type IN ('client','agent','system','ai')),
  CONSTRAINT wa_messages_type_check
    CHECK (message_type IN ('text','image','document','audio','template')),
  CONSTRAINT wa_messages_status_check
    CHECK (status IN ('sent','delivered','read','failed'))
);

CREATE INDEX IF NOT EXISTS idx_wa_messages_tenant ON wa_messages(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wa_messages_conversation ON wa_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_wa_messages_timestamp ON wa_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_wa_messages_wa_id ON wa_messages(whatsapp_message_id);

ALTER TABLE wa_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_messages_tenant_policy ON wa_messages
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_messages_service_role ON wa_messages
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 4. wa_templates
-- =============================================

CREATE TABLE IF NOT EXISTS wa_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  display_name TEXT,
  category TEXT NOT NULL DEFAULT 'utility',
  language TEXT DEFAULT 'es',
  status TEXT NOT NULL DEFAULT 'PENDING',
  components JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT wa_templates_category_check
    CHECK (category IN ('utility','marketing','authentication')),
  CONSTRAINT wa_templates_status_check
    CHECK (status IN ('PENDING','APPROVED','REJECTED')),
  UNIQUE(tenant_id, name)
);

CREATE INDEX IF NOT EXISTS idx_wa_templates_tenant ON wa_templates(tenant_id);

CREATE TRIGGER update_wa_templates_updated_at
  BEFORE UPDATE ON wa_templates
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE wa_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_templates_tenant_policy ON wa_templates
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_templates_service_role ON wa_templates
  FOR ALL TO service_role
  USING (true);

-- =============================================
-- 5. wa_notification_rules
-- =============================================

CREATE TABLE IF NOT EXISTS wa_notification_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  template_id UUID REFERENCES wa_templates(id) ON DELETE SET NULL,
  is_active BOOLEAN DEFAULT true,
  conditions JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT wa_notification_rules_event_check
    CHECK (event_type IN ('case_created','status_change','tramite_vencido','checklist_complete','payment_received'))
);

CREATE INDEX IF NOT EXISTS idx_wa_notification_rules_tenant ON wa_notification_rules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wa_notification_rules_event ON wa_notification_rules(event_type);

ALTER TABLE wa_notification_rules ENABLE ROW LEVEL SECURITY;

CREATE POLICY wa_notification_rules_tenant_policy ON wa_notification_rules
  FOR ALL TO authenticated
  USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY wa_notification_rules_service_role ON wa_notification_rules
  FOR ALL TO service_role
  USING (true);
