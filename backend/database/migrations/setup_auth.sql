-- ============================================================================
-- setup_auth.sql - Script de configuración inicial de autenticación
-- ============================================================================
-- Este script configura los datos iniciales necesarios para usar el sistema
-- con autenticación de Supabase.
--
-- INSTRUCCIONES:
-- 1. Primero, crea un usuario en Supabase Auth (Dashboard > Authentication)
-- 2. Anota el UUID del usuario creado
-- 3. Ejecuta este script reemplazando <USER_UUID> con el UUID real
-- 4. El script creará:
--    - Una notaría (tenant) de ejemplo
--    - Un registro de usuario vinculado al tenant
--    - Datos de prueba opcionales
-- ============================================================================

-- Variables a reemplazar:
-- <USER_UUID>: UUID del usuario creado en Supabase Auth
--              Ejemplo: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

-- ============================================================================
-- PASO 1: Crear Tenant (Notaría)
-- ============================================================================

DO $$
DECLARE
    v_tenant_id UUID;
    v_user_uuid UUID := '<USER_UUID>'; -- REEMPLAZAR CON UUID REAL
BEGIN
    -- Insertar tenant de ejemplo
    INSERT INTO tenants (
        nombre,
        rfc,
        direccion,
        telefono,
        email,
        plan,
        activo
    ) VALUES (
        'Notaría Pública No. 1',
        'NPN010101ABC',
        'Av. Principal 123, Col. Centro, Ciudad, Estado',
        '+52 55 1234 5678',
        'contacto@notaria1.mx',
        'professional',
        true
    )
    RETURNING id INTO v_tenant_id;

    RAISE NOTICE 'Tenant creado con ID: %', v_tenant_id;

    -- ============================================================================
    -- PASO 2: Vincular Usuario al Tenant
    -- ============================================================================

    INSERT INTO users (
        id,  -- Mismo UUID que en Supabase Auth
        tenant_id,
        email,
        nombre_completo,
        rol,
        activo
    ) VALUES (
        v_user_uuid,
        v_tenant_id,
        'admin@notaria1.mx',  -- Mismo email usado en Supabase Auth
        'Administrador Principal',
        'admin',
        true
    );

    RAISE NOTICE 'Usuario vinculado al tenant';

    -- ============================================================================
    -- PASO 3: Datos de Prueba (Opcional)
    -- ============================================================================

    -- Cliente de ejemplo
    INSERT INTO clients (
        tenant_id,
        tipo_persona,
        nombre_completo,
        rfc,
        email,
        telefono
    ) VALUES (
        v_tenant_id,
        'fisica',
        'Juan Pérez García',
        'PEGJ850101ABC',
        'juan.perez@email.com',
        '+52 55 9876 5432'
    );

    RAISE NOTICE 'Cliente de prueba creado';

    -- Template de ejemplo
    INSERT INTO templates (
        tenant_id,
        tipo_documento,
        nombre,
        placeholders,
        es_publico,
        activo
    ) VALUES (
        v_tenant_id,
        'compraventa',
        'Escritura de Compraventa Estándar',
        ARRAY[
            'NOMBRE_COMPRADOR',
            'NOMBRE_VENDEDOR',
            'DESCRIPCION_INMUEBLE',
            'PRECIO_VENTA',
            'FECHA_OPERACION'
        ],
        false,
        true
    );

    RAISE NOTICE 'Template de prueba creado';

    -- ============================================================================
    -- PASO 4: Configurar Preferencias de Estilo
    -- ============================================================================

    INSERT INTO estilo_preferencias (
        tenant_id,
        font_family,
        font_size,
        line_spacing,
        header_style
    ) VALUES (
        v_tenant_id,
        'Arial',
        12,
        1.15,
        '{
            "alignment": "center",
            "bold": true,
            "font_size": 14
        }'::jsonb
    );

    RAISE NOTICE 'Preferencias de estilo configuradas';

    -- ============================================================================
    -- RESUMEN
    -- ============================================================================

    RAISE NOTICE '============================================';
    RAISE NOTICE 'CONFIGURACIÓN COMPLETADA';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Tenant ID: %', v_tenant_id;
    RAISE NOTICE 'Usuario ID: %', v_user_uuid;
    RAISE NOTICE '';
    RAISE NOTICE 'Próximos pasos:';
    RAISE NOTICE '1. Inicia sesión en el frontend con el usuario creado';
    RAISE NOTICE '2. El token JWT incluirá automáticamente el tenant_id';
    RAISE NOTICE '3. Todas las operaciones quedarán aisladas por tenant';
    RAISE NOTICE '============================================';

END $$;

-- ============================================================================
-- VERIFICACIÓN: Consultar datos creados
-- ============================================================================

-- Verificar tenant
SELECT
    id,
    nombre,
    rfc,
    plan,
    activo,
    created_at
FROM tenants
ORDER BY created_at DESC
LIMIT 1;

-- Verificar usuario
SELECT
    u.id,
    u.email,
    u.nombre_completo,
    u.rol,
    t.nombre AS notaria
FROM users u
JOIN tenants t ON u.tenant_id = t.id
ORDER BY u.created_at DESC
LIMIT 1;

-- ============================================================================
-- LIMPIEZA (Solo para desarrollo/testing)
-- ============================================================================
-- Si necesitas resetear y volver a ejecutar el script:
--
-- DELETE FROM users WHERE email = 'admin@notaria1.mx';
-- DELETE FROM clients WHERE tenant_id IN (
--     SELECT id FROM tenants WHERE nombre = 'Notaría Pública No. 1'
-- );
-- DELETE FROM templates WHERE tenant_id IN (
--     SELECT id FROM tenants WHERE nombre = 'Notaría Pública No. 1'
-- );
-- DELETE FROM estilo_preferencias WHERE tenant_id IN (
--     SELECT id FROM tenants WHERE nombre = 'Notaría Pública No. 1'
-- );
-- DELETE FROM tenants WHERE nombre = 'Notaría Pública No. 1';
-- ============================================================================
