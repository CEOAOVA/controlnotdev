-- ========================================
-- MIGRACIÓN 005: Perfil de Notaría
-- Agrega campos adicionales para pre-llenado de datos del instrumento
-- ========================================

-- Agregar columnas al perfil de notaría (tabla tenants)
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS notario_nombre TEXT;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS notario_titulo TEXT DEFAULT 'Licenciado';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS numero_notaria_palabras TEXT;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS ultimo_numero_instrumento INTEGER DEFAULT 0;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS direccion TEXT;

-- Comentarios descriptivos
COMMENT ON COLUMN tenants.notario_nombre IS 'Nombre completo del notario titular (ej: Patricia Servín Maldonado)';
COMMENT ON COLUMN tenants.notario_titulo IS 'Título del notario (Licenciado, Doctor, Maestra, etc.)';
COMMENT ON COLUMN tenants.numero_notaria_palabras IS 'Número de notaría en palabras (ej: catorce)';
COMMENT ON COLUMN tenants.ultimo_numero_instrumento IS 'Último número de instrumento usado para auto-incremento';
COMMENT ON COLUMN tenants.direccion IS 'Dirección completa de la notaría';

-- Función para convertir número a palabras (hasta 999)
CREATE OR REPLACE FUNCTION numero_a_palabras(num INTEGER)
RETURNS TEXT AS $$
DECLARE
    unidades TEXT[] := ARRAY['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve'];
    decenas TEXT[] := ARRAY['', 'diez', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'];
    especiales TEXT[] := ARRAY['diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve'];
    veintis TEXT[] := ARRAY['veinte', 'veintiuno', 'veintidós', 'veintitrés', 'veinticuatro', 'veinticinco', 'veintiséis', 'veintisiete', 'veintiocho', 'veintinueve'];
    centenas TEXT[] := ARRAY['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'];
    resultado TEXT := '';
    c INTEGER;
    d INTEGER;
    u INTEGER;
BEGIN
    IF num IS NULL OR num < 0 OR num > 999 THEN
        RETURN NULL;
    END IF;

    IF num = 0 THEN
        RETURN 'cero';
    END IF;

    IF num = 100 THEN
        RETURN 'cien';
    END IF;

    c := num / 100;
    d := (num % 100) / 10;
    u := num % 10;

    -- Centenas
    IF c > 0 THEN
        resultado := centenas[c + 1];
    END IF;

    -- Decenas y unidades
    IF d = 1 THEN
        -- 10-19
        IF resultado != '' THEN
            resultado := resultado || ' ';
        END IF;
        resultado := resultado || especiales[u + 1];
    ELSIF d = 2 THEN
        -- 20-29
        IF resultado != '' THEN
            resultado := resultado || ' ';
        END IF;
        resultado := resultado || veintis[u + 1];
    ELSIF d > 2 THEN
        -- 30-99
        IF resultado != '' THEN
            resultado := resultado || ' ';
        END IF;
        resultado := resultado || decenas[d + 1];
        IF u > 0 THEN
            resultado := resultado || ' y ' || unidades[u + 1];
        END IF;
    ELSIF u > 0 THEN
        -- 1-9
        IF resultado != '' THEN
            resultado := resultado || ' ';
        END IF;
        resultado := resultado || unidades[u + 1];
    END IF;

    RETURN resultado;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger para auto-generar numero_notaria_palabras
CREATE OR REPLACE FUNCTION update_numero_notaria_palabras()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.numero_notaria IS NOT NULL AND (NEW.numero_notaria_palabras IS NULL OR NEW.numero_notaria_palabras = '') THEN
        NEW.numero_notaria_palabras := numero_a_palabras(NEW.numero_notaria);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger solo si no existe
DROP TRIGGER IF EXISTS trigger_update_numero_palabras ON tenants;
CREATE TRIGGER trigger_update_numero_palabras
    BEFORE INSERT OR UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_numero_notaria_palabras();

-- Actualizar registros existentes que tengan numero_notaria pero no palabras
UPDATE tenants
SET numero_notaria_palabras = numero_a_palabras(numero_notaria)
WHERE numero_notaria IS NOT NULL AND (numero_notaria_palabras IS NULL OR numero_notaria_palabras = '');

-- ========================================
-- ÍNDICES
-- ========================================
CREATE INDEX IF NOT EXISTS idx_tenants_notario_nombre ON tenants(notario_nombre);
