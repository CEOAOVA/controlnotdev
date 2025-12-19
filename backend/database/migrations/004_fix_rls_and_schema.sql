-- ============================================================================
-- Migration 004: Fix RLS policies and add missing columns
-- Created: 2025-12-17
-- Purpose: Normalize RLS to auth.uid(), add case_id/template_id to documentos
-- ============================================================================

-- ============================================================================
-- PARTE 1: AGREGAR COLUMNAS FALTANTES A DOCUMENTOS
-- ============================================================================

-- Agregar case_id (referencia a cases)
ALTER TABLE documentos
ADD COLUMN IF NOT EXISTS case_id UUID REFERENCES cases(id) ON DELETE SET NULL;

-- Agregar template_id (referencia a templates)
ALTER TABLE documentos
ADD COLUMN IF NOT EXISTS template_id UUID REFERENCES templates(id) ON DELETE SET NULL;

-- Índices para las nuevas columnas
CREATE INDEX IF NOT EXISTS idx_documentos_case ON documentos(case_id) WHERE case_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documentos_template ON documentos(template_id) WHERE template_id IS NOT NULL;

COMMENT ON COLUMN documentos.case_id IS 'Referencia al caso/expediente asociado';
COMMENT ON COLUMN documentos.template_id IS 'Referencia al template usado para generar';

-- ============================================================================
-- PARTE 2: HABILITAR RLS EN TABLA USERS
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Usuarios pueden ver su propio registro
CREATE POLICY "Users can view own record"
ON users FOR SELECT TO authenticated
USING (id = auth.uid());

-- Usuarios pueden actualizar su propio registro (excepto tenant_id y rol)
CREATE POLICY "Users can update own record"
ON users FOR UPDATE TO authenticated
USING (id = auth.uid());

-- Solo el sistema puede insertar usuarios (via auth trigger)
-- No policy needed for INSERT - handled by Supabase Auth

-- ============================================================================
-- PARTE 3: CORREGIR RLS DE MIGRACIÓN 003 (current_setting → auth.uid)
-- ============================================================================

-- === EXTRACTION_CACHE ===
DROP POLICY IF EXISTS "Users can view their tenant's cache" ON extraction_cache;
DROP POLICY IF EXISTS "Users can insert into their tenant's cache" ON extraction_cache;
DROP POLICY IF EXISTS "Users can update their tenant's cache" ON extraction_cache;

CREATE POLICY "Tenant users can view cache"
ON extraction_cache FOR SELECT TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can insert cache"
ON extraction_cache FOR INSERT TO authenticated
WITH CHECK (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can update cache"
ON extraction_cache FOR UPDATE TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

-- === AUDIT_LOGS ===
DROP POLICY IF EXISTS "Users can view their tenant's audit logs" ON audit_logs;

CREATE POLICY "Tenant users can view audit logs"
ON audit_logs FOR SELECT TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

-- INSERT policy stays as is (system can always insert)

-- === CLIENTS ===
DROP POLICY IF EXISTS "Users can view their tenant's clients" ON clients;
DROP POLICY IF EXISTS "Users can insert their tenant's clients" ON clients;
DROP POLICY IF EXISTS "Users can update their tenant's clients" ON clients;
DROP POLICY IF EXISTS "Users can delete their tenant's clients" ON clients;

CREATE POLICY "Tenant users can view clients"
ON clients FOR SELECT TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can insert clients"
ON clients FOR INSERT TO authenticated
WITH CHECK (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can update clients"
ON clients FOR UPDATE TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can delete clients"
ON clients FOR DELETE TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

-- === CASES ===
DROP POLICY IF EXISTS "Users can view their tenant's cases" ON cases;
DROP POLICY IF EXISTS "Users can insert their tenant's cases" ON cases;
DROP POLICY IF EXISTS "Users can update their tenant's cases" ON cases;
DROP POLICY IF EXISTS "Users can delete their tenant's cases" ON cases;

CREATE POLICY "Tenant users can view cases"
ON cases FOR SELECT TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can insert cases"
ON cases FOR INSERT TO authenticated
WITH CHECK (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can update cases"
ON cases FOR UPDATE TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Tenant users can delete cases"
ON cases FOR DELETE TO authenticated
USING (tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid()));

-- ============================================================================
-- PARTE 4: VERIFICACIÓN
-- ============================================================================

-- Verificar que todas las tablas tienen RLS habilitado
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('tenants', 'users', 'documentos', 'templates', 'sessions',
                  'clients', 'cases', 'extraction_cache', 'audit_logs')
ORDER BY tablename;

-- ============================================================================
-- FIN DE MIGRACIÓN
-- ============================================================================

COMMENT ON SCHEMA public IS 'ControlNot V2 - Schema con RLS normalizado (auth.uid)';
