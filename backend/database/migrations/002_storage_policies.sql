-- ========================================
-- CONTROLNOT V2 - STORAGE POLICIES
-- Configuración de Supabase Storage con RLS
-- ========================================

-- ========================================
-- CREAR BUCKETS
-- ========================================

-- Bucket para documentos (privado)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'documentos',
    'documentos',
    false,
    52428800, -- 50MB por archivo
    ARRAY[
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/bmp',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
)
ON CONFLICT (id) DO NOTHING;

-- Bucket para templates (semi-público)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'templates',
    'templates',
    false,
    10485760, -- 10MB por archivo
    ARRAY[
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
)
ON CONFLICT (id) DO NOTHING;

-- ========================================
-- POLÍTICAS RLS: BUCKET DOCUMENTOS
-- ========================================

-- POLÍTICA: Los usuarios pueden ver archivos de su tenant
CREATE POLICY "Users can view own tenant files"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'documentos' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- POLÍTICA: Los usuarios pueden subir archivos a su carpeta tenant
CREATE POLICY "Users can upload to own tenant folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'documentos' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- POLÍTICA: Los usuarios pueden actualizar archivos de su tenant
CREATE POLICY "Users can update own tenant files"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id = 'documentos' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- POLÍTICA: Los usuarios pueden eliminar archivos de su tenant
CREATE POLICY "Users can delete own tenant files"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'documentos' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- ========================================
-- POLÍTICAS RLS: BUCKET TEMPLATES
-- ========================================

-- POLÍTICA: Los usuarios pueden ver templates públicos o de su tenant
CREATE POLICY "Users can view public or own tenant templates"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'templates' AND (
        -- Templates en carpeta 'public' son visibles para todos
        (storage.foldername(name))[1] = 'public' OR
        -- O templates de su propio tenant
        (storage.foldername(name))[1] = (
            SELECT tenant_id::text FROM users WHERE id = auth.uid()
        )
    )
);

-- POLÍTICA: Los usuarios pueden subir templates a su carpeta tenant
CREATE POLICY "Users can upload templates to own folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'templates' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- POLÍTICA: Los usuarios solo pueden actualizar sus propios templates
CREATE POLICY "Users can update own tenant templates"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id = 'templates' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- POLÍTICA: Los usuarios solo pueden eliminar sus propios templates
CREATE POLICY "Users can delete own tenant templates"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'templates' AND
    (storage.foldername(name))[1] = (
        SELECT tenant_id::text FROM users WHERE id = auth.uid()
    )
);

-- ========================================
-- ESTRUCTURA DE CARPETAS RECOMENDADA
-- ========================================

/*
ESTRUCTURA EN STORAGE:

documentos/
├── {tenant_id_1}/
│   ├── uploads/
│   │   ├── compraventa/
│   │   ├── donacion/
│   │   ├── cancelacion/
│   │   └── otros/
│   ├── outputs/
│   │   └── {YYYY-MM}/
│   └── ejemplos/
│       ├── compraventa/
│       ├── donacion/
│       └── cancelacion/
├── {tenant_id_2}/
│   └── ...

templates/
├── public/
│   ├── compraventa_basico.docx
│   ├── donacion_basico.docx
│   └── cancelacion_basico.docx
├── {tenant_id_1}/
│   ├── compraventa_personalizado.docx
│   └── donacion_personalizada.docx
└── {tenant_id_2}/
    └── ...
*/

-- ========================================
-- FUNCIONES HELPER PARA STORAGE
-- ========================================

-- Función para obtener URL firmada temporal (válida 1 hora)
CREATE OR REPLACE FUNCTION get_signed_url(
    p_bucket TEXT,
    p_path TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_url TEXT;
BEGIN
    -- Verificar que el usuario tiene acceso al archivo
    IF NOT EXISTS (
        SELECT 1 FROM storage.objects
        WHERE bucket_id = p_bucket
        AND name = p_path
        AND (storage.foldername(name))[1] = (
            SELECT tenant_id::text FROM users WHERE id = auth.uid()
        )
    ) THEN
        RAISE EXCEPTION 'Access denied to file: %', p_path;
    END IF;

    -- Generar URL firmada (esto requiere configuración adicional en Supabase)
    -- Por ahora retornamos el path, en producción usar storage.sign()
    RETURN format('https://%s.supabase.co/storage/v1/object/sign/%s/%s',
        current_setting('app.settings.supabase_project_ref'),
        p_bucket,
        p_path
    );
END;
$$;

COMMENT ON FUNCTION get_signed_url IS 'Genera URL firmada temporal para acceso seguro a archivos';

-- ========================================
-- VISTAS ÚTILES PARA STORAGE
-- ========================================

-- Vista de uso de storage por tenant
CREATE OR REPLACE VIEW storage_usage_by_tenant AS
SELECT
    (storage.foldername(o.name))[1]::UUID AS tenant_id,
    t.nombre AS tenant_nombre,
    o.bucket_id,
    COUNT(*) AS total_archivos,
    SUM(
        COALESCE(
            (o.metadata->>'size')::BIGINT,
            0
        )
    ) AS total_bytes,
    ROUND(
        SUM(
            COALESCE(
                (o.metadata->>'size')::BIGINT,
                0
            )
        ) / 1024.0 / 1024.0,
        2
    ) AS total_mb
FROM storage.objects o
JOIN tenants t ON t.id = (storage.foldername(o.name))[1]::UUID
WHERE o.bucket_id IN ('documentos', 'templates')
GROUP BY (storage.foldername(o.name))[1], t.nombre, o.bucket_id;

COMMENT ON VIEW storage_usage_by_tenant IS 'Estadísticas de uso de storage por notaría';

-- ========================================
-- LIMPIEZA AUTOMÁTICA (OPCIONAL)
-- ========================================

-- Función para limpiar archivos temporales antiguos (>7 días)
CREATE OR REPLACE FUNCTION cleanup_old_temp_files()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_deleted INTEGER := 0;
BEGIN
    -- Eliminar archivos en carpetas temp/ más antiguos de 7 días
    DELETE FROM storage.objects
    WHERE bucket_id = 'documentos'
    AND name LIKE '%/temp/%'
    AND created_at < NOW() - INTERVAL '7 days';

    GET DIAGNOSTICS v_deleted = ROW_COUNT;

    RETURN v_deleted;
END;
$$;

COMMENT ON FUNCTION cleanup_old_temp_files IS 'Limpia archivos temporales antiguos (>7 días)';

-- Programar limpieza automática con pg_cron (si está habilitado)
-- SELECT cron.schedule('cleanup-temp-files', '0 2 * * *', 'SELECT cleanup_old_temp_files()');

-- ========================================
-- FIN DE CONFIGURACIÓN DE STORAGE
-- ========================================
