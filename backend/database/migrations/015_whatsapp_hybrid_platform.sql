-- Migration 015: WhatsApp Hybrid Platform Architecture
-- Adds is_platform flag to wa_phone_tenant_map for multi-number routing
-- is_platform = true: AuriNot shared number (routes by staff phone lookup across all tenants)
-- is_platform = false: dedicated notaría number (routes directly to tenant)

ALTER TABLE wa_phone_tenant_map
  ADD COLUMN IF NOT EXISTS is_platform BOOLEAN NOT NULL DEFAULT false;

COMMENT ON COLUMN wa_phone_tenant_map.is_platform IS 'True for platform-wide AuriNot number, false for per-notaría dedicated numbers';
