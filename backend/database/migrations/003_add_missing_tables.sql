-- Migration 003: Add missing tables for complete functionality
-- Created: 2025-11-23
-- Purpose: Add extraction_cache, audit_logs, clients, and cases tables

-- ============================================================================
-- TABLA: extraction_cache
-- Propósito: Cache de extracciones de IA para reducir costos 40-60%
-- ============================================================================

CREATE TABLE IF NOT EXISTS extraction_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    file_hash TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN
        ('compraventa', 'donacion', 'testamento', 'poder', 'sociedad', 'cancelacion')),
    ocr_text TEXT,
    ocr_provider TEXT DEFAULT 'google_vision',
    extracted_data JSONB,
    extraction_model TEXT,
    extraction_provider TEXT DEFAULT 'openai',
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    last_used_at TIMESTAMPTZ DEFAULT now(),

    -- Unique constraint: mismo hash + tipo + tenant = cache hit
    UNIQUE(file_hash, document_type, tenant_id)
);

-- Índices para performance
CREATE INDEX idx_extraction_cache_hash ON extraction_cache(file_hash);
CREATE INDEX idx_extraction_cache_tenant ON extraction_cache(tenant_id);
CREATE INDEX idx_extraction_cache_type ON extraction_cache(document_type);
CREATE INDEX idx_extraction_cache_last_used ON extraction_cache(last_used_at DESC);

-- Row Level Security
ALTER TABLE extraction_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their tenant's cache"
    ON extraction_cache FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can insert into their tenant's cache"
    ON extraction_cache FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can update their tenant's cache"
    ON extraction_cache FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- ============================================================================
-- TABLA: audit_logs
-- Propósito: Registro completo de auditoría de todas las operaciones
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Acción realizada
    action TEXT NOT NULL CHECK (action IN (
        'create_client', 'update_client', 'delete_client',
        'create_case', 'update_case', 'complete_case', 'cancel_case',
        'upload_documents', 'start_ocr', 'complete_ocr',
        'extract_data', 'validate_data', 'generate_document',
        'download_document', 'sign_document',
        'upload_template', 'delete_template',
        'login', 'logout'
    )),

    -- Entidad afectada
    entity_type TEXT CHECK (entity_type IN
        ('client', 'case', 'session', 'document', 'template', 'user', 'system')),
    entity_id UUID,

    -- Detalles adicionales
    details JSONB DEFAULT '{}'::jsonb,

    -- Información de contexto
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- Índice GIN para búsqueda en JSONB
CREATE INDEX idx_audit_logs_details ON audit_logs USING GIN (details);

-- Row Level Security
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their tenant's audit logs"
    ON audit_logs FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "System can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- TABLA: clients
-- Propósito: Catálogo de clientes (personas físicas y morales)
-- ============================================================================

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Información básica
    tipo_persona TEXT NOT NULL CHECK (tipo_persona IN ('fisica', 'moral')),
    nombre_completo TEXT NOT NULL,

    -- Identificación fiscal
    rfc TEXT,
    curp TEXT,

    -- Contacto
    email TEXT,
    telefono TEXT,

    -- Dirección
    direccion TEXT,
    ciudad TEXT,
    estado TEXT,
    codigo_postal TEXT,

    -- Metadata flexible
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Estado
    activo BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX idx_clients_tenant ON clients(tenant_id);
CREATE INDEX idx_clients_rfc ON clients(rfc) WHERE rfc IS NOT NULL;
CREATE INDEX idx_clients_curp ON clients(curp) WHERE curp IS NOT NULL;
CREATE INDEX idx_clients_email ON clients(email) WHERE email IS NOT NULL;
CREATE INDEX idx_clients_activo ON clients(activo);

-- Índice para búsqueda de texto completo
CREATE INDEX idx_clients_nombre ON clients USING GIN (to_tsvector('spanish', nombre_completo));

-- Row Level Security
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their tenant's clients"
    ON clients FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can insert their tenant's clients"
    ON clients FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can update their tenant's clients"
    ON clients FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can delete their tenant's clients"
    ON clients FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- ============================================================================
-- TABLA: cases
-- Propósito: Expedientes/casos notariales con workflow
-- ============================================================================

CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,

    -- Información del caso
    case_number TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN
        ('compraventa', 'donacion', 'testamento', 'poder', 'sociedad', 'cancelacion')),

    -- Estado del workflow
    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft',
        'documents_uploaded',
        'ocr_processing',
        'data_extracted',
        'validated',
        'document_generated',
        'signed',
        'completed',
        'cancelled'
    )),

    -- Partes involucradas (múltiples)
    parties JSONB DEFAULT '[]'::jsonb,

    -- Descripción
    description TEXT,

    -- Metadata flexible
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,

    -- Constraint: case_number único por tenant
    UNIQUE(tenant_id, case_number)
);

-- Índices para performance
CREATE INDEX idx_cases_tenant ON cases(tenant_id);
CREATE INDEX idx_cases_client ON cases(client_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_type ON cases(document_type);
CREATE INDEX idx_cases_number ON cases(case_number);
CREATE INDEX idx_cases_created ON cases(created_at DESC);

-- Índice GIN para búsqueda en parties
CREATE INDEX idx_cases_parties ON cases USING GIN (parties);

-- Row Level Security
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their tenant's cases"
    ON cases FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can insert their tenant's cases"
    ON cases FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can update their tenant's cases"
    ON cases FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY "Users can delete their tenant's cases"
    ON cases FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- ============================================================================
-- TRIGGERS: Actualizar updated_at automáticamente
-- ============================================================================

-- Función genérica para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para clients
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para cases
CREATE TRIGGER update_cases_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMENTARIOS DESCRIPTIVOS
-- ============================================================================

COMMENT ON TABLE extraction_cache IS 'Cache de extracciones de IA para reducir costos y mejorar performance';
COMMENT ON TABLE audit_logs IS 'Registro completo de auditoría de todas las operaciones del sistema';
COMMENT ON TABLE clients IS 'Catálogo de clientes (personas físicas y morales) de la notaría';
COMMENT ON TABLE cases IS 'Expedientes/casos notariales con workflow de estados';

COMMENT ON COLUMN extraction_cache.file_hash IS 'SHA-256 hash del texto OCR para deduplicación';
COMMENT ON COLUMN extraction_cache.hit_count IS 'Número de veces que se reutilizó esta extracción';
COMMENT ON COLUMN clients.tipo_persona IS 'Tipo de persona: física o moral';
COMMENT ON COLUMN cases.status IS 'Estado del workflow del caso';
COMMENT ON COLUMN cases.parties IS 'Array JSON de partes involucradas en el caso';

-- ============================================================================
-- DATOS DE EJEMPLO (Opcional - Comentado)
-- ============================================================================

-- INSERT INTO clients (tenant_id, tipo_persona, nombre_completo, rfc, email, telefono)
-- VALUES (
--     (SELECT id FROM tenants LIMIT 1),
--     'fisica',
--     'Juan Pérez García',
--     'PEGJ800101XXX',
--     'juan.perez@example.com',
--     '5512345678'
-- );

-- ============================================================================
-- FIN DE MIGRACIÓN
-- ============================================================================

-- Verificar tablas creadas
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('extraction_cache', 'audit_logs', 'clients', 'cases')
ORDER BY tablename;
