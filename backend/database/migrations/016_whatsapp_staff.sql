-- Migration 015: WhatsApp Staff Management
-- Adds tables for staff phone registration, command logging,
-- and staff notification support.

-- ============================================
-- Table: wa_staff_phones
-- Maps staff phone numbers to users for interactive menu access
-- ============================================
CREATE TABLE IF NOT EXISTS wa_staff_phones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    phone TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'asistente' CHECK (role IN ('notario', 'asistente', 'abogado', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    session_state JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, phone)
);

-- ============================================
-- Table: wa_command_log
-- Audit log of all staff commands executed via WhatsApp
-- ============================================
CREATE TABLE IF NOT EXISTS wa_command_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    staff_phone TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    command TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    result TEXT,
    response_preview TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================
-- Add notify_staff column to wa_notification_rules
-- ============================================
ALTER TABLE wa_notification_rules
    ADD COLUMN IF NOT EXISTS notify_staff BOOLEAN NOT NULL DEFAULT false;

-- Add message_text column if not exists (used for custom text notifications)
ALTER TABLE wa_notification_rules
    ADD COLUMN IF NOT EXISTS message_text TEXT;

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_wa_staff_phones_tenant_phone
    ON wa_staff_phones(tenant_id, phone);

CREATE INDEX IF NOT EXISTS idx_wa_staff_phones_tenant_active
    ON wa_staff_phones(tenant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_wa_command_log_tenant
    ON wa_command_log(tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_wa_command_log_staff
    ON wa_command_log(staff_phone, created_at DESC);

-- ============================================
-- RLS Policies
-- ============================================
ALTER TABLE wa_staff_phones ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_command_log ENABLE ROW LEVEL SECURITY;

-- wa_staff_phones policies
CREATE POLICY "wa_staff_phones_tenant_select" ON wa_staff_phones
    FOR SELECT TO authenticated
    USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY "wa_staff_phones_tenant_insert" ON wa_staff_phones
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY "wa_staff_phones_tenant_update" ON wa_staff_phones
    FOR UPDATE TO authenticated
    USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY "wa_staff_phones_tenant_delete" ON wa_staff_phones
    FOR DELETE TO authenticated
    USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY "wa_staff_phones_service_all" ON wa_staff_phones
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- wa_command_log policies
CREATE POLICY "wa_command_log_tenant_select" ON wa_command_log
    FOR SELECT TO authenticated
    USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY "wa_command_log_service_all" ON wa_command_log
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- ============================================
-- Trigger: auto-update updated_at on wa_staff_phones
-- ============================================
CREATE TRIGGER update_wa_staff_phones_updated_at
    BEFORE UPDATE ON wa_staff_phones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
