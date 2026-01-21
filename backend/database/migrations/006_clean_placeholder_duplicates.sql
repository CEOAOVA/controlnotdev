-- ============================================================
-- Migration: 006_clean_placeholder_duplicates.sql
-- Descripción: Limpia placeholders duplicados con prefijo '{'
-- ============================================================
--
-- Este script corrige un bug donde el regex de extracción capturaba
-- placeholders duplicados con formato "{placeholder" además de "placeholder"
-- cuando el template usa {{placeholder}}.
--
-- Ejemplo del problema:
--   ANTES: ["deudor", "{deudor", "notario", "{notario"]  -- duplicados
--   DESPUÉS: ["deudor", "notario"]                        -- correcto
--
-- Uso:
--   psql -d controlnot -f 006_clean_placeholder_duplicates.sql
--   O ejecutar directamente en Supabase SQL Editor
-- ============================================================

-- 1. Ver estado actual antes de limpiar
SELECT
    'ANTES DE LIMPIAR' as estado,
    COUNT(*) as total_versions,
    SUM(CASE WHEN placeholders::text LIKE '%"{%' THEN 1 ELSE 0 END) as versions_con_duplicados
FROM template_versions;

-- 2. Crear función para limpiar placeholders con { prefix
CREATE OR REPLACE FUNCTION clean_placeholder_duplicates(arr jsonb)
RETURNS jsonb AS $$
    SELECT COALESCE(
        jsonb_agg(elem ORDER BY elem),
        '[]'::jsonb
    )
    FROM jsonb_array_elements_text(arr) AS elem
    WHERE NOT elem LIKE '{%'
$$ LANGUAGE sql IMMUTABLE;

-- 3. Crear función para limpiar keys de mapping con { prefix
CREATE OR REPLACE FUNCTION clean_mapping_keys(mapping jsonb)
RETURNS jsonb AS $$
    SELECT COALESCE(
        jsonb_object_agg(key, value),
        '{}'::jsonb
    )
    FROM jsonb_each_text(mapping)
    WHERE NOT key LIKE '{%'
$$ LANGUAGE sql IMMUTABLE;

-- 4. Actualizar template_versions - Limpiar placeholders
UPDATE template_versions
SET placeholders = clean_placeholder_duplicates(placeholders)
WHERE placeholders::text LIKE '%"{%';

-- 5. Actualizar template_versions - Limpiar placeholder_mapping keys
UPDATE template_versions
SET placeholder_mapping = clean_mapping_keys(placeholder_mapping)
WHERE placeholder_mapping::text LIKE '%"{%';

-- 6. Actualizar templates - Limpiar placeholders
UPDATE templates
SET
    placeholders = clean_placeholder_duplicates(placeholders),
    total_placeholders = jsonb_array_length(clean_placeholder_duplicates(placeholders))
WHERE placeholders::text LIKE '%"{%';

-- 7. Verificar resultados
SELECT
    'DESPUÉS DE LIMPIAR' as estado,
    COUNT(*) as total_versions,
    SUM(CASE WHEN placeholders::text LIKE '%"{%' THEN 1 ELSE 0 END) as versions_con_duplicados
FROM template_versions;

-- 8. Mostrar resumen de templates actualizados
SELECT
    t.nombre as template_name,
    t.tipo_documento,
    t.total_placeholders,
    tv.version_number,
    jsonb_array_length(tv.placeholders) as placeholders_count
FROM templates t
LEFT JOIN template_versions tv ON tv.template_id = t.id
ORDER BY t.nombre, tv.version_number;

-- 9. Limpiar funciones temporales (opcional)
-- DROP FUNCTION IF EXISTS clean_placeholder_duplicates(jsonb);
-- DROP FUNCTION IF EXISTS clean_mapping_keys(jsonb);

-- ============================================================
-- Notas:
-- - Las funciones se mantienen para uso futuro (opcionalmente eliminar)
-- - Ejecutar el script de recalculate_mappings.py después para
--   actualizar los placeholder_mapping con el algoritmo mejorado:
--   cd backend && python -m scripts.recalculate_mappings
-- ============================================================
