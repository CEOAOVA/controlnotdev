-- Migration 018: Security Fixes — RLS & SECURITY DEFINER Views
-- Fixes 4 Supabase security advisor warnings:
--   1. tenants table: RLS disabled + anon has full access
--   2. leads table: RLS disabled + anon has full access
--   3. tenant_statistics view: SECURITY DEFINER
--   4. storage_usage_by_tenant view: SECURITY DEFINER

-- ============================================================
-- Fix 1: tenants table — Enable RLS + restrict access
-- Backend uses service_role (bypasses RLS), so this is safe.
-- ============================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

-- Authenticated users can only SELECT their own tenant
CREATE POLICY "Users can view own tenant"
ON tenants FOR SELECT TO authenticated
USING (id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

-- Revoke all anon access to tenants
REVOKE ALL ON tenants FROM anon;

-- ============================================================
-- Fix 2: leads table — Enable RLS + INSERT-only for anon
-- Landing page form submissions need anon INSERT only.
-- ============================================================

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Anon can only INSERT (submit a lead form)
CREATE POLICY "Anon can submit leads"
ON leads FOR INSERT TO anon
WITH CHECK (true);

-- Authenticated users can view leads (admin dashboard)
CREATE POLICY "Authenticated can view leads"
ON leads FOR SELECT TO authenticated
USING (true);

-- Revoke excess grants from anon (keep only INSERT)
REVOKE SELECT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON leads FROM anon;

-- ============================================================
-- Fix 3: tenant_statistics view — Recreate as SECURITY INVOKER
-- Not used in backend. Underlying table RLS will now apply.
-- ============================================================

DROP VIEW IF EXISTS tenant_statistics;

CREATE VIEW tenant_statistics
WITH (security_invoker = true) AS
SELECT
    t.id AS tenant_id,
    t.nombre AS tenant_nombre,
    COUNT(DISTINCT d.id) AS total_documentos,
    COUNT(DISTINCT CASE WHEN d.estado = 'completado' THEN d.id ELSE NULL::uuid END) AS documentos_completados,
    COUNT(DISTINCT CASE WHEN d.es_ejemplo_bueno THEN d.id ELSE NULL::uuid END) AS documentos_ejemplo,
    COUNT(DISTINCT tp.id) AS total_templates,
    COUNT(DISTINCT u.id) AS total_usuarios
FROM tenants t
LEFT JOIN documentos d ON d.tenant_id = t.id
LEFT JOIN templates tp ON tp.tenant_id = t.id
LEFT JOIN users u ON u.tenant_id = t.id
GROUP BY t.id, t.nombre;

-- Restrict access
REVOKE ALL ON tenant_statistics FROM anon;
GRANT SELECT ON tenant_statistics TO authenticated;
GRANT SELECT ON tenant_statistics TO service_role;

-- ============================================================
-- Fix 4: storage_usage_by_tenant view — Recreate as SECURITY INVOKER
-- Not used in backend. Underlying table RLS will now apply.
-- ============================================================

DROP VIEW IF EXISTS storage_usage_by_tenant;

CREATE VIEW storage_usage_by_tenant
WITH (security_invoker = true) AS
SELECT
    ((storage.foldername(o.name))[1])::UUID AS tenant_id,
    t.nombre AS tenant_nombre,
    o.bucket_id,
    COUNT(*) AS total_archivos,
    SUM(COALESCE((o.metadata->>'size')::BIGINT, 0)) AS total_bytes,
    ROUND(SUM(COALESCE((o.metadata->>'size')::BIGINT, 0)) / 1024.0 / 1024.0, 2) AS total_mb
FROM storage.objects o
JOIN tenants t ON t.id = ((storage.foldername(o.name))[1])::UUID
WHERE o.bucket_id IN ('documentos', 'templates')
GROUP BY (storage.foldername(o.name))[1], t.nombre, o.bucket_id;

-- Restrict access
REVOKE ALL ON storage_usage_by_tenant FROM anon;
GRANT SELECT ON storage_usage_by_tenant TO authenticated;
GRANT SELECT ON storage_usage_by_tenant TO service_role;
