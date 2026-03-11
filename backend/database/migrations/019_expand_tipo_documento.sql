-- Migration 019: Expand tipo_documento CHECK constraint
-- The original constraint only allowed 6 types, causing INSERT failures
-- for document types like 'cancelacion_hipoteca', 'ine_ife', etc.
-- This resulted in documents never persisting to the DB (empty history).

-- Drop the old CHECK constraint
ALTER TABLE documentos DROP CONSTRAINT IF EXISTS documentos_tipo_documento_check;

-- Add expanded CHECK constraint with all document types used in the system
ALTER TABLE documentos ADD CONSTRAINT documentos_tipo_documento_check
  CHECK (tipo_documento IN (
    -- Original types
    'compraventa',
    'donacion',
    'testamento',
    'poder',
    'sociedad',
    'cancelacion',
    -- Additional types
    'cancelacion_hipoteca',
    'ine_ife',
    'curp_constancia',
    'pasaporte',
    'acta_nacimiento',
    'otros'
  ));
