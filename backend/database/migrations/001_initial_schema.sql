-- ========================================
-- CONTROLNOT V2 - INITIAL SCHEMA
-- Multi-Tenant SaaS Database Schema
-- ========================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========================================
-- TABLA: tenants
-- ========================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    rfc TEXT UNIQUE NOT NULL,
    numero_notaria INTEGER,
    estado TEXT NOT NULL,
    ciudad TEXT,
    activo BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para tenants
CREATE INDEX idx_tenants_rfc ON tenants(rfc);
CREATE INDEX idx_tenants_estado ON tenants(estado);
CREATE INDEX idx_tenants_activo ON tenants(activo) WHERE activo = TRUE;

COMMENT ON TABLE tenants IS 'Tabla de notarías (tenants) del sistema multi-tenant';

-- ========================================
-- TABLA: users
-- ========================================
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    email TEXT UNIQUE NOT NULL,
    nombre_completo TEXT,
    rol TEXT NOT NULL DEFAULT 'notario' CHECK (rol IN ('admin', 'notario', 'asistente')),
    activo BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para users
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_rol ON users(rol);

COMMENT ON TABLE users IS 'Usuarios del sistema con relación a su notaría (tenant)';

-- ========================================
-- TABLA: documentos
-- ========================================
CREATE TABLE documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    user_id UUID REFERENCES users(id),

    -- Metadata del documento
    tipo_documento TEXT NOT NULL CHECK (tipo_documento IN ('compraventa', 'donacion', 'testamento', 'poder', 'sociedad', 'cancelacion')),
    nombre_documento TEXT,
    estado TEXT NOT NULL DEFAULT 'borrador' CHECK (estado IN ('borrador', 'procesando', 'revisado', 'completado', 'error')),

    -- Storage
    storage_path TEXT,
    google_drive_id TEXT,

    -- Datos extraídos y procesados
    extracted_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    edited_data JSONB,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Flags
    es_ejemplo_bueno BOOLEAN DEFAULT FALSE,
    requiere_revision BOOLEAN DEFAULT FALSE,

    -- Metadata adicional
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Índices para documentos
CREATE INDEX idx_documentos_tenant ON documentos(tenant_id);
CREATE INDEX idx_documentos_tipo ON documentos(tipo_documento);
CREATE INDEX idx_documentos_estado ON documentos(estado);
CREATE INDEX idx_documentos_usuario ON documentos(user_id);
CREATE INDEX idx_documentos_fecha ON documentos(created_at DESC);
CREATE INDEX idx_documentos_ejemplos ON documentos(tenant_id, tipo_documento) WHERE es_ejemplo_bueno = TRUE;

-- Índice compuesto para búsquedas comunes
CREATE INDEX idx_documentos_tenant_tipo_fecha ON documentos(tenant_id, tipo_documento, created_at DESC);

COMMENT ON TABLE documentos IS 'Documentos procesados por el sistema con datos extraídos';

-- ========================================
-- TABLA: templates
-- ========================================
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id), -- NULL = template compartido/público

    -- Metadata del template
    tipo_documento TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,

    -- Storage
    storage_path TEXT,
    google_drive_id TEXT,
    google_drive_folder_id TEXT,

    -- Placeholders extraídos del template
    placeholders JSONB DEFAULT '[]'::jsonb,
    total_placeholders INTEGER DEFAULT 0,

    -- Flags
    es_publico BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para templates
CREATE INDEX idx_templates_tenant ON templates(tenant_id);
CREATE INDEX idx_templates_tipo ON templates(tipo_documento);
CREATE INDEX idx_templates_publicos ON templates(es_publico) WHERE es_publico = TRUE;
CREATE INDEX idx_templates_activos ON templates(activo) WHERE activo = TRUE;

COMMENT ON TABLE templates IS 'Plantillas Word utilizadas para generar documentos';

-- ========================================
-- TABLA: sessions
-- ========================================
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    user_id UUID REFERENCES users(id),

    -- Estado de la sesión
    tipo_documento TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'iniciado' CHECK (estado IN ('iniciado', 'procesando', 'completado', 'error', 'cancelado')),

    -- Progreso
    total_archivos INTEGER DEFAULT 0,
    archivos_procesados INTEGER DEFAULT 0,
    progreso_porcentaje FLOAT DEFAULT 0,

    -- Datos de la sesión
    session_data JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Índices para sessions
CREATE INDEX idx_sessions_tenant ON sessions(tenant_id);
CREATE INDEX idx_sessions_usuario ON sessions(user_id);
CREATE INDEX idx_sessions_estado ON sessions(estado);
CREATE INDEX idx_sessions_fecha ON sessions(created_at DESC);

COMMENT ON TABLE sessions IS 'Sesiones de procesamiento de documentos';

-- ========================================
-- TABLA: vector_metadata
-- ========================================
CREATE TABLE vector_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    documento_id UUID REFERENCES documentos(id) ON DELETE CASCADE,

    -- Referencia al vector DB (Qdrant)
    vector_db_id TEXT NOT NULL,
    collection_name TEXT NOT NULL DEFAULT 'notarios_documentos',

    -- Metadata
    tipo_documento TEXT NOT NULL,
    calidad TEXT CHECK (calidad IN ('bueno', 'regular', 'malo')),
    embedding_model TEXT DEFAULT 'text-embedding-3-small',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para vector_metadata
CREATE INDEX idx_vector_tenant ON vector_metadata(tenant_id);
CREATE INDEX idx_vector_documento ON vector_metadata(documento_id);
CREATE INDEX idx_vector_db_id ON vector_metadata(vector_db_id);

COMMENT ON TABLE vector_metadata IS 'Metadata de vectores indexados en Qdrant para RAG/Few-Shot';

-- ========================================
-- TABLA: estilo_preferencias
-- ========================================
CREATE TABLE estilo_preferencias (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,

    -- Terminología personalizada
    terminologia_preferida JSONB DEFAULT '{}'::jsonb,

    -- Formatos
    formato_fechas TEXT DEFAULT 'completo' CHECK (formato_fechas IN ('completo', 'abreviado', 'numerico')),
    formato_numeros TEXT DEFAULT 'letras' CHECK (formato_numeros IN ('letras', 'digitos', 'ambos')),

    -- Cláusulas recurrentes
    clausulas_recurrentes JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE estilo_preferencias IS 'Preferencias de estilo de redacción por notaría';

-- ========================================
-- FUNCIONES HELPER
-- ========================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documentos_updated_at BEFORE UPDATE ON documentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_estilo_preferencias_updated_at BEFORE UPDATE ON estilo_preferencias
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Habilitar RLS en todas las tablas principales
ALTER TABLE documentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE estilo_preferencias ENABLE ROW LEVEL SECURITY;

-- ========================================
-- POLÍTICAS RLS: documentos
-- ========================================

-- Los usuarios solo pueden ver documentos de su tenant
CREATE POLICY "Users access own tenant documents"
ON documentos FOR SELECT TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Los usuarios pueden insertar documentos en su tenant
CREATE POLICY "Users insert own tenant documents"
ON documentos FOR INSERT TO authenticated
WITH CHECK (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Los usuarios pueden actualizar documentos de su tenant
CREATE POLICY "Users update own tenant documents"
ON documentos FOR UPDATE TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Los usuarios pueden eliminar documentos de su tenant
CREATE POLICY "Users delete own tenant documents"
ON documentos FOR DELETE TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- ========================================
-- POLÍTICAS RLS: templates
-- ========================================

-- Los usuarios pueden ver templates públicos o de su tenant
CREATE POLICY "Users access public or own tenant templates"
ON templates FOR SELECT TO authenticated
USING (
    es_publico = TRUE OR
    tenant_id IS NULL OR
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Solo pueden insertar templates en su tenant
CREATE POLICY "Users insert own tenant templates"
ON templates FOR INSERT TO authenticated
WITH CHECK (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- Solo pueden actualizar sus propios templates
CREATE POLICY "Users update own tenant templates"
ON templates FOR UPDATE TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- ========================================
-- POLÍTICAS RLS: sessions
-- ========================================

CREATE POLICY "Users access own tenant sessions"
ON sessions FOR ALL TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- ========================================
-- POLÍTICAS RLS: vector_metadata
-- ========================================

CREATE POLICY "Users access own tenant vectors"
ON vector_metadata FOR ALL TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- ========================================
-- POLÍTICAS RLS: estilo_preferencias
-- ========================================

CREATE POLICY "Users access own tenant preferences"
ON estilo_preferencias FOR ALL TO authenticated
USING (
    tenant_id = (SELECT tenant_id FROM users WHERE id = auth.uid())
);

-- ========================================
-- DATOS INICIALES / SEED
-- ========================================

-- Insertar tenant de ejemplo (opcional, comentar si no se necesita)
-- INSERT INTO tenants (nombre, rfc, numero_notaria, estado, ciudad)
-- VALUES ('Notaría 14 - Patricia Servín Maldonado', 'NSM850101ABC', 14, 'Michoacán', 'Morelia');

-- ========================================
-- VISTAS ÚTILES
-- ========================================

-- Vista de estadísticas por tenant
CREATE OR REPLACE VIEW tenant_statistics AS
SELECT
    t.id AS tenant_id,
    t.nombre AS tenant_nombre,
    COUNT(DISTINCT d.id) AS total_documentos,
    COUNT(DISTINCT CASE WHEN d.estado = 'completado' THEN d.id END) AS documentos_completados,
    COUNT(DISTINCT CASE WHEN d.es_ejemplo_bueno THEN d.id END) AS documentos_ejemplo,
    COUNT(DISTINCT tp.id) AS total_templates,
    COUNT(DISTINCT u.id) AS total_usuarios
FROM tenants t
LEFT JOIN documentos d ON d.tenant_id = t.id
LEFT JOIN templates tp ON tp.tenant_id = t.id
LEFT JOIN users u ON u.tenant_id = t.id
GROUP BY t.id, t.nombre;

COMMENT ON VIEW tenant_statistics IS 'Estadísticas agregadas por notaría';

-- ========================================
-- FIN DE MIGRACIÓN
-- ========================================

COMMENT ON SCHEMA public IS 'ControlNot V2 - Schema Multi-Tenant con RLS';
