-- =============================================
-- SEED DATA: WhatsApp Integration Test Scenarios
-- =============================================
-- Cubre TODOS los escenarios de prueba:
--   1. Routing: numero plataforma vs dedicado
--   2. Staff: notario, asistente, abogado (menus interactivos)
--   3. Clientes: persona fisica, moral, contacto sin vincular
--   4. Cases: multiples estados del workflow con checklist, tramites, pagos
--   5. Conversaciones: abiertas, cerradas, pendientes, con/sin caso
--   6. Mensajes: texto, imagen, documento, audio, template, interactivos
--   7. Notificaciones: reglas activas/inactivas, staff/cliente
--   8. Templates: aprobados, pendientes, rechazados
--   9. Extracciones de documentos via WA
--  10. Calendar events vinculados a casos
-- =============================================

-- Usar UUIDs deterministicos para referencias cruzadas
-- Prefijo: a0000000- para tenant 1, b0000000- para tenant 2

BEGIN;

-- =============================================
-- LIMPIEZA (idempotente - safe re-run)
-- =============================================
DELETE FROM wa_command_log WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_document_extractions WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_messages WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_conversations WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_contacts WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_notification_rules WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_templates WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_staff_phones WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM wa_phone_tenant_map WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM calendar_events WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM case_payments WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM case_tramites WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM case_checklist WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM case_parties WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM case_activity_log WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM cases WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM clients WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM users WHERE tenant_id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);
DELETE FROM tenants WHERE id IN (
  'a0000000-0000-0000-0000-000000000001'::uuid,
  'b0000000-0000-0000-0000-000000000001'::uuid
);


-- =============================================
-- 1. TENANTS (2 notarias para probar multi-tenant)
-- =============================================

INSERT INTO tenants (id, nombre, rfc, numero_notaria, estado, ciudad, activo, metadata) VALUES
(
  'a0000000-0000-0000-0000-000000000001',
  'Notaria 14 Test - Lic. Patricia Servin',
  'NSM850101TST',
  14,
  'Michoacan',
  'Morelia',
  true,
  '{"plan": "premium", "max_users": 10}'::jsonb
),
(
  'b0000000-0000-0000-0000-000000000001',
  'Notaria 7 Test - Lic. Roberto Mendez',
  'NRM900215TST',
  7,
  'Jalisco',
  'Guadalajara',
  true,
  '{"plan": "basico", "max_users": 5}'::jsonb
);


-- =============================================
-- 2. USERS (sin auth.users FK para seed - insertar con ON CONFLICT)
-- NOTA: En produccion estos vienen de Supabase Auth.
-- Para seed usamos INSERT directo; si la FK a auth.users
-- esta activa, primero crear los auth users o desactivar FK temporalmente.
-- =============================================

-- Tenant A: Notaria 14
INSERT INTO users (id, tenant_id, email, nombre_completo, rol, activo) VALUES
('a0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000001',
 'patricia.servin@notaria14test.com', 'Lic. Patricia Servin Maldonado', 'notario', true),
('a0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000001',
 'maria.garcia@notaria14test.com', 'Maria Garcia Lopez', 'asistente', true),
('a0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000001',
 'carlos.ruiz@notaria14test.com', 'Lic. Carlos Ruiz Hernandez', 'abogado', true),
('a0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000001',
 'admin@notaria14test.com', 'Admin Sistema N14', 'admin', true);

-- Tenant B: Notaria 7
INSERT INTO users (id, tenant_id, email, nombre_completo, rol, activo) VALUES
('b0000000-0000-0000-0000-000000000010', 'b0000000-0000-0000-0000-000000000001',
 'roberto.mendez@notaria7test.com', 'Lic. Roberto Mendez Flores', 'notario', true),
('b0000000-0000-0000-0000-000000000011', 'b0000000-0000-0000-0000-000000000001',
 'laura.torres@notaria7test.com', 'Laura Torres Ramirez', 'asistente', true);


-- =============================================
-- 3. CLIENTS (variedad: fisica, moral, multiples)
-- =============================================

-- Tenant A clients
INSERT INTO clients (id, tenant_id, tipo_persona, nombre_completo, rfc, curp, email, telefono, direccion, ciudad, estado, codigo_postal) VALUES
-- Comprador de compraventa
('a0000000-0000-0000-0000-000000000100', 'a0000000-0000-0000-0000-000000000001',
 'fisica', 'Juan Perez Garcia', 'PEGJ800315AB1', 'PEGJ800315HMNRRC09',
 'juan.perez@gmail.com', '5215512345678', 'Av. Madero 100, Col. Centro', 'Morelia', 'Michoacan', '58000'),
-- Vendedor de compraventa
('a0000000-0000-0000-0000-000000000101', 'a0000000-0000-0000-0000-000000000001',
 'fisica', 'Ana Martinez Soto', 'MASA750820CD2', 'MASA750820MMNRTN05',
 'ana.martinez@hotmail.com', '5215587654321', 'Calle Morelos 50, Col. Reforma', 'Morelia', 'Michoacan', '58020'),
-- Empresa donante
('a0000000-0000-0000-0000-000000000102', 'a0000000-0000-0000-0000-000000000001',
 'moral', 'Constructora del Bajio SA de CV', 'CBJ010101AAA', NULL,
 'contacto@constructorabajio.com', '5215544332211', 'Blvd. Garcia de Leon 500', 'Morelia', 'Michoacan', '58100'),
-- Donatario (persona fisica)
('a0000000-0000-0000-0000-000000000103', 'a0000000-0000-0000-0000-000000000001',
 'fisica', 'Roberto Sanchez Diaz', 'SADR900101EF3', 'SADR900101HMNNCB01',
 'roberto.sanchez@yahoo.com', '5215566778899', 'Calle Aquiles Serdan 25', 'Morelia', 'Michoacan', '58040'),
-- Testador
('a0000000-0000-0000-0000-000000000104', 'a0000000-0000-0000-0000-000000000001',
 'fisica', 'Elena Vazquez Rios', 'VARE650510GH4', 'VARE650510MMNZLN08',
 'elena.vazquez@gmail.com', '5215533221100', 'Privada Insurgentes 12', 'Morelia', 'Michoacan', '58060'),
-- Cliente sin telefono registrado (para probar contacto WA sin vincular)
('a0000000-0000-0000-0000-000000000105', 'a0000000-0000-0000-0000-000000000001',
 'fisica', 'Pedro Gomez Luna', 'GOLP880101IJ5', NULL,
 'pedro.gomez@outlook.com', NULL, NULL, 'Morelia', 'Michoacan', NULL);

-- Tenant B clients
INSERT INTO clients (id, tenant_id, tipo_persona, nombre_completo, rfc, curp, email, telefono, ciudad, estado) VALUES
('b0000000-0000-0000-0000-000000000100', 'b0000000-0000-0000-0000-000000000001',
 'fisica', 'Sofia Ramirez Ortega', 'RAOS850220KL6', 'RAOS850220MJLMRT02',
 'sofia.ramirez@gmail.com', '5213312345678', 'Guadalajara', 'Jalisco'),
('b0000000-0000-0000-0000-000000000101', 'b0000000-0000-0000-0000-000000000001',
 'moral', 'Inmobiliaria Tapatia SA', 'ITA050315MN7', NULL,
 'ventas@inmotapatia.com', '5213398765432', 'Guadalajara', 'Jalisco');


-- =============================================
-- 4. CASES (multiples tipos y estados del workflow)
-- =============================================

-- Tenant A: 6 expedientes en distintas fases
INSERT INTO cases (id, tenant_id, client_id, case_number, document_type, status, assigned_to, priority, escritura_number, valor_operacion, notas, parties) VALUES
-- Compraventa en revision (fase temprana)
('a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000100', 'EXP-2025-001', 'compraventa', 'en_revision',
 'a0000000-0000-0000-0000-000000000012', 'alta', NULL, 2500000.00,
 'Compraventa inmueble residencial Col. Centro',
 '[{"role":"comprador","nombre":"Juan Perez Garcia"},{"role":"vendedor","nombre":"Ana Martinez Soto"}]'::jsonb),

-- Donacion con checklist pendiente
('a0000000-0000-0000-0000-000000001002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000102', 'EXP-2025-002', 'donacion', 'checklist_pendiente',
 'a0000000-0000-0000-0000-000000000011', 'normal', NULL, 1800000.00,
 'Donacion de terreno comercial',
 '[{"role":"donante","nombre":"Constructora del Bajio SA de CV"},{"role":"donatario","nombre":"Roberto Sanchez Diaz"}]'::jsonb),

-- Testamento en firma
('a0000000-0000-0000-0000-000000001003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000104', 'EXP-2025-003', 'testamento', 'en_firma',
 'a0000000-0000-0000-0000-000000000010', 'normal', '15234', NULL,
 'Testamento publico abierto',
 '[{"role":"testador","nombre":"Elena Vazquez Rios"}]'::jsonb),

-- Poder en tramites de gobierno
('a0000000-0000-0000-0000-000000001004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000100', 'EXP-2025-004', 'poder', 'tramites_gobierno',
 'a0000000-0000-0000-0000-000000000012', 'alta', '15235', NULL,
 'Poder general para actos de administracion',
 '[{"role":"poderdante","nombre":"Juan Perez Garcia"},{"role":"apoderado","nombre":"Ana Martinez Soto"}]'::jsonb),

-- Compraventa cerrada (caso historico)
('a0000000-0000-0000-0000-000000001005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000101', 'EXP-2024-015', 'compraventa', 'cerrado',
 'a0000000-0000-0000-0000-000000000012', 'normal', '15200', 3200000.00,
 'Compraventa departamento Lomas',
 '[{"role":"vendedor","nombre":"Ana Martinez Soto"},{"role":"comprador","nombre":"Pedro Gomez Luna"}]'::jsonb),

-- Sociedad en borrador (recien creada)
('a0000000-0000-0000-0000-000000001006', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000000102', 'EXP-2025-006', 'sociedad', 'borrador',
 'a0000000-0000-0000-0000-000000000011', 'baja', NULL, 500000.00,
 'Constitucion de SA de CV',
 '[{"role":"socio","nombre":"Constructora del Bajio SA de CV"},{"role":"socio","nombre":"Roberto Sanchez Diaz"}]'::jsonb);

-- Tenant B: 2 expedientes
INSERT INTO cases (id, tenant_id, client_id, case_number, document_type, status, assigned_to, priority, valor_operacion, parties) VALUES
('b0000000-0000-0000-0000-000000001001', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-000000000100', 'EXP-2025-001', 'compraventa', 'presupuesto',
 'b0000000-0000-0000-0000-000000000010', 'alta', 4500000.00,
 '[{"role":"comprador","nombre":"Sofia Ramirez Ortega"},{"role":"vendedor","nombre":"Inmobiliaria Tapatia SA"}]'::jsonb),
('b0000000-0000-0000-0000-000000001002', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-000000000100', 'EXP-2025-002', 'testamento', 'en_revision',
 'b0000000-0000-0000-0000-000000000011', 'normal', NULL,
 '[{"role":"testador","nombre":"Sofia Ramirez Ortega"}]'::jsonb);


-- =============================================
-- 5. CASE PARTIES (detalle de partes por expediente)
-- =============================================

INSERT INTO case_parties (id, tenant_id, case_id, client_id, role, nombre, rfc, tipo_persona, email, telefono, orden) VALUES
-- EXP-2025-001 Compraventa
('a0000000-0000-0000-0000-000000002001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000100',
 'comprador', 'Juan Perez Garcia', 'PEGJ800315AB1', 'fisica', 'juan.perez@gmail.com', '5215512345678', 1),
('a0000000-0000-0000-0000-000000002002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000101',
 'vendedor', 'Ana Martinez Soto', 'MASA750820CD2', 'fisica', 'ana.martinez@hotmail.com', '5215587654321', 2),
-- EXP-2025-002 Donacion
('a0000000-0000-0000-0000-000000002003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'a0000000-0000-0000-0000-000000000102',
 'donante', 'Constructora del Bajio SA de CV', 'CBJ010101AAA', 'moral', 'contacto@constructorabajio.com', '5215544332211', 1),
('a0000000-0000-0000-0000-000000002004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'a0000000-0000-0000-0000-000000000103',
 'donatario', 'Roberto Sanchez Diaz', 'SADR900101EF3', 'fisica', 'roberto.sanchez@yahoo.com', '5215566778899', 2),
-- EXP-2025-003 Testamento
('a0000000-0000-0000-0000-000000002005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001003', 'a0000000-0000-0000-0000-000000000104',
 'testador', 'Elena Vazquez Rios', 'VARE650510GH4', 'fisica', 'elena.vazquez@gmail.com', '5215533221100', 1);


-- =============================================
-- 6. CASE CHECKLIST (documentos requeridos por expediente)
-- =============================================

-- EXP-2025-001: Compraventa - mezcla de estados
INSERT INTO case_checklist (id, tenant_id, case_id, nombre, categoria, status, obligatorio, fecha_solicitud, fecha_recepcion) VALUES
('a0000000-0000-0000-0000-000000003001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'INE Comprador', 'parte_a', 'recibido', true, NOW() - INTERVAL '10 days', NOW() - INTERVAL '5 days'),
('a0000000-0000-0000-0000-000000003002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'CURP Comprador', 'parte_a', 'recibido', true, NOW() - INTERVAL '10 days', NOW() - INTERVAL '5 days'),
('a0000000-0000-0000-0000-000000003003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Constancia de situacion fiscal Comprador', 'parte_a', 'solicitado', true, NOW() - INTERVAL '5 days', NULL),
('a0000000-0000-0000-0000-000000003004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'INE Vendedor', 'parte_b', 'recibido', true, NOW() - INTERVAL '10 days', NOW() - INTERVAL '7 days'),
('a0000000-0000-0000-0000-000000003005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Escritura antecedente', 'inmueble', 'pendiente', true, NULL, NULL),
('a0000000-0000-0000-0000-000000003006', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Certificado de libertad de gravamen', 'inmueble', 'solicitado', true, NOW() - INTERVAL '3 days', NULL),
('a0000000-0000-0000-0000-000000003007', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Predial al corriente', 'fiscal', 'pendiente', true, NULL, NULL),
('a0000000-0000-0000-0000-000000003008', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Certificado de no adeudo de agua', 'fiscal', 'no_aplica', false, NULL, NULL);

-- EXP-2025-002: Donacion - casi todo pendiente
INSERT INTO case_checklist (id, tenant_id, case_id, nombre, categoria, status, obligatorio) VALUES
('a0000000-0000-0000-0000-000000003010', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'Acta constitutiva donante', 'parte_a', 'pendiente', true),
('a0000000-0000-0000-0000-000000003011', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'Poder del representante legal', 'parte_a', 'pendiente', true),
('a0000000-0000-0000-0000-000000003012', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'INE Donatario', 'parte_b', 'recibido', true),
('a0000000-0000-0000-0000-000000003013', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'Avaluo del inmueble', 'inmueble', 'pendiente', true);


-- =============================================
-- 7. CASE TRAMITES (gobierno, registro, etc.)
-- =============================================

-- EXP-2025-001: Compraventa - sin tramites aun (esta en revision)

-- EXP-2025-004: Poder - en tramites de gobierno
INSERT INTO case_tramites (id, tenant_id, case_id, assigned_to, tipo, nombre, status, fecha_inicio, fecha_limite, costo, notas) VALUES
('a0000000-0000-0000-0000-000000004001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'a0000000-0000-0000-0000-000000000012',
 'gobierno', 'Inscripcion en Registro Publico', 'en_proceso',
 NOW() - INTERVAL '5 days', NOW() + INTERVAL '10 days', 3500.00,
 'Expediente ingresado, folio de recepcion: RP-2025-4521'),
('a0000000-0000-0000-0000-000000004002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'a0000000-0000-0000-0000-000000000011',
 'gobierno', 'Pago de ISR ante SAT', 'completado',
 NOW() - INTERVAL '15 days', NOW() - INTERVAL '5 days', 12500.00,
 'Linea de captura pagada, referencia: SAT-2025-887766'),
-- Tramite VENCIDO (para probar alerta)
('a0000000-0000-0000-0000-000000004003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'a0000000-0000-0000-0000-000000000012',
 'gobierno', 'Aviso preventivo ante RPP', 'vencido',
 NOW() - INTERVAL '30 days', NOW() - INTERVAL '5 days', 800.00,
 'VENCIDO - No se presento en tiempo');

-- EXP-2025-002: Donacion - tramite pendiente con fecha limite proxima
INSERT INTO case_tramites (id, tenant_id, case_id, tipo, nombre, status, fecha_limite) VALUES
('a0000000-0000-0000-0000-000000004004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002',
 'gobierno', 'Calculo de impuesto por donacion (ISR)', 'pendiente', NOW() + INTERVAL '3 days');

-- Tenant B
INSERT INTO case_tramites (id, tenant_id, case_id, tipo, nombre, status, fecha_limite) VALUES
('b0000000-0000-0000-0000-000000004001', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-000000001001',
 'gobierno', 'Certificado de no adeudo predial', 'pendiente', NOW() + INTERVAL '7 days');


-- =============================================
-- 8. CASE PAYMENTS (pagos)
-- =============================================

INSERT INTO case_payments (id, tenant_id, case_id, tipo, concepto, monto, metodo_pago, referencia, fecha_pago, recibido_por) VALUES
-- EXP-2025-001: Anticipo de honorarios
('a0000000-0000-0000-0000-000000005001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'honorarios', 'Anticipo 50% honorarios escrituracion',
 15000.00, 'transferencia', 'SPEI-20250301-001', NOW() - INTERVAL '7 days', 'Maria Garcia'),
-- EXP-2025-004: Pagos de tramites
('a0000000-0000-0000-0000-000000005002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'impuestos', 'ISR por enajenacion',
 12500.00, 'transferencia', 'SPEI-20250215-002', NOW() - INTERVAL '15 days', 'Carlos Ruiz'),
('a0000000-0000-0000-0000-000000005003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'derechos', 'Derechos de registro RPP',
 3500.00, 'efectivo', NULL, NOW() - INTERVAL '5 days', 'Maria Garcia'),
-- EXP-2024-015: Caso cerrado - todos los pagos
('a0000000-0000-0000-0000-000000005004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001005', 'honorarios', 'Honorarios escrituracion completo',
 30000.00, 'cheque', 'CHQ-4455', NOW() - INTERVAL '60 days', 'Patricia Servin'),
('a0000000-0000-0000-0000-000000005005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001005', 'impuestos', 'ISAI + ISR',
 48000.00, 'transferencia', 'SPEI-20241201-003', NOW() - INTERVAL '65 days', 'Carlos Ruiz');


-- =============================================
-- 9. CALENDAR EVENTS (citas, vencimientos, firmas)
-- =============================================

INSERT INTO calendar_events (id, tenant_id, case_id, titulo, descripcion, tipo, fecha_inicio, fecha_fin, created_by) VALUES
-- Firma programada para testamento
('a0000000-0000-0000-0000-000000006001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001003', 'Firma testamento - Elena Vazquez',
 'Testamento publico abierto. Requiere 3 testigos. Sala de firma reservada.',
 'firma', NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days' + INTERVAL '2 hours',
 'a0000000-0000-0000-0000-000000000010'),
-- Cita con comprador
('a0000000-0000-0000-0000-000000006002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'Cita revision docs - Juan Perez',
 'Revisar documentacion faltante de compraventa',
 'cita', NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day' + INTERVAL '1 hour',
 'a0000000-0000-0000-0000-000000000012'),
-- Vencimiento de tramite
('a0000000-0000-0000-0000-000000006003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'VENCIMIENTO: Inscripcion RPP',
 'Fecha limite para presentar documentos en RPP',
 'vencimiento', NOW() + INTERVAL '10 days', NULL,
 'a0000000-0000-0000-0000-000000000012'),
-- Vencimiento ya pasado (para alertas)
('a0000000-0000-0000-0000-000000006004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001002', 'VENCIMIENTO: Calculo ISR donacion',
 'Limite para presentar calculo ante SAT',
 'vencimiento', NOW() + INTERVAL '3 days', NULL,
 'a0000000-0000-0000-0000-000000000011');


-- =============================================
-- 10. WA_PHONE_TENANT_MAP (routing de webhooks)
-- =============================================
-- Escenario: 1 numero plataforma (AuriNot) + 1 numero dedicado por notaria

INSERT INTO wa_phone_tenant_map (id, phone_number_id, tenant_id, is_platform) VALUES
-- Numero de plataforma AuriNot (compartido - staff de cualquier tenant)
('a0000000-0000-0000-0000-000000007001', '910944215432464',
 'a0000000-0000-0000-0000-000000000001', true),
-- Numero dedicado Notaria 14
('a0000000-0000-0000-0000-000000007002', 'DEDICATED_N14_TEST_001',
 'a0000000-0000-0000-0000-000000000001', false),
-- Numero dedicado Notaria 7
('b0000000-0000-0000-0000-000000007001', 'DEDICATED_N7_TEST_001',
 'b0000000-0000-0000-0000-000000000001', false);


-- =============================================
-- 11. WA_STAFF_PHONES (staff registrado para menus interactivos)
-- =============================================

-- Tenant A: 3 staff con distintos roles
INSERT INTO wa_staff_phones (id, tenant_id, phone, user_id, display_name, role, is_active, session_state) VALUES
('a0000000-0000-0000-0000-000000008001', 'a0000000-0000-0000-0000-000000000001',
 '5215599990001', 'a0000000-0000-0000-0000-000000000010',
 'Lic. Patricia Servin', 'notario', true, '{}'::jsonb),
('a0000000-0000-0000-0000-000000008002', 'a0000000-0000-0000-0000-000000000001',
 '5215599990002', 'a0000000-0000-0000-0000-000000000011',
 'Maria Garcia', 'asistente', true, '{}'::jsonb),
('a0000000-0000-0000-0000-000000008003', 'a0000000-0000-0000-0000-000000000001',
 '5215599990003', 'a0000000-0000-0000-0000-000000000012',
 'Lic. Carlos Ruiz', 'abogado', true, '{}'::jsonb),
-- Staff INACTIVO (para probar que no recibe menus)
('a0000000-0000-0000-0000-000000008004', 'a0000000-0000-0000-0000-000000000001',
 '5215599990004', 'a0000000-0000-0000-0000-000000000013',
 'Admin N14 (inactivo)', 'admin', false, '{}'::jsonb);

-- Tenant B: 2 staff
INSERT INTO wa_staff_phones (id, tenant_id, phone, user_id, display_name, role, is_active, session_state) VALUES
('b0000000-0000-0000-0000-000000008001', 'b0000000-0000-0000-0000-000000000001',
 '5213399990001', 'b0000000-0000-0000-0000-000000000010',
 'Lic. Roberto Mendez', 'notario', true, '{}'::jsonb),
('b0000000-0000-0000-0000-000000008002', 'b0000000-0000-0000-0000-000000000001',
 '5213399990002', 'b0000000-0000-0000-0000-000000000011',
 'Laura Torres', 'asistente', true, '{}'::jsonb);


-- =============================================
-- 12. WA_CONTACTS (contactos de WhatsApp)
-- =============================================

-- Tenant A: clientes con contacto WA
INSERT INTO wa_contacts (id, tenant_id, phone, name, client_id, is_blocked, last_seen) VALUES
-- Vinculado a cliente (comprador)
('a0000000-0000-0000-0000-000000009001', 'a0000000-0000-0000-0000-000000000001',
 '5215512345678', 'Juan Perez', 'a0000000-0000-0000-0000-000000000100',
 false, NOW() - INTERVAL '1 hour'),
-- Vinculado a cliente (vendedora)
('a0000000-0000-0000-0000-000000009002', 'a0000000-0000-0000-0000-000000000001',
 '5215587654321', 'Ana Martinez', 'a0000000-0000-0000-0000-000000000101',
 false, NOW() - INTERVAL '3 hours'),
-- Vinculado a cliente (empresa - contacto de la empresa)
('a0000000-0000-0000-0000-000000009003', 'a0000000-0000-0000-0000-000000000001',
 '5215544332211', 'Constructora Bajio', 'a0000000-0000-0000-0000-000000000102',
 false, NOW() - INTERVAL '2 days'),
-- Contacto SIN vincular a cliente (probar vinculacion)
('a0000000-0000-0000-0000-000000009004', 'a0000000-0000-0000-0000-000000000001',
 '5215511112222', 'Desconocido WA', NULL,
 false, NOW() - INTERVAL '1 day'),
-- Contacto BLOQUEADO (probar filtrado)
('a0000000-0000-0000-0000-000000009005', 'a0000000-0000-0000-0000-000000000001',
 '5215500001111', 'Spam Contact', NULL,
 true, NOW() - INTERVAL '30 days');

-- Tenant B
INSERT INTO wa_contacts (id, tenant_id, phone, name, client_id) VALUES
('b0000000-0000-0000-0000-000000009001', 'b0000000-0000-0000-0000-000000000001',
 '5213312345678', 'Sofia Ramirez', 'b0000000-0000-0000-0000-000000000100');


-- =============================================
-- 13. WA_CONVERSATIONS (estados variados)
-- =============================================

INSERT INTO wa_conversations (id, tenant_id, contact_id, case_id, assigned_to, status, last_message_at, last_message_preview, unread_count, ai_enabled) VALUES
-- Conv 1: Abierta, vinculada a caso compraventa, con mensajes no leidos
('a0000000-0000-0000-0000-00000000a001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000009001', 'a0000000-0000-0000-0000-000000001001',
 'a0000000-0000-0000-0000-000000000012', 'open',
 NOW() - INTERVAL '30 minutes', 'Ya tengo la constancia fiscal, la envio por aqui?', 3, false),

-- Conv 2: Abierta, vinculada a caso donacion, AI habilitado
('a0000000-0000-0000-0000-00000000a002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000009003', 'a0000000-0000-0000-0000-000000001002',
 'a0000000-0000-0000-0000-000000000011', 'open',
 NOW() - INTERVAL '2 hours', 'Necesitamos el acta constitutiva actualizada', 1, true),

-- Conv 3: Cerrada (caso historico)
('a0000000-0000-0000-0000-00000000a003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000009002', 'a0000000-0000-0000-0000-000000001005',
 NULL, 'closed',
 NOW() - INTERVAL '30 days', 'Gracias, todo recibido', 0, false),

-- Conv 4: Pendiente, SIN caso vinculado (contacto nuevo sin vincular)
('a0000000-0000-0000-0000-00000000a004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000009004', NULL,
 NULL, 'pending',
 NOW() - INTERVAL '1 day', 'Hola, me gustaria cotizar una escritura', 1, false),

-- Conv 5: Abierta, vendedora con caso testamento
('a0000000-0000-0000-0000-00000000a005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000009002', 'a0000000-0000-0000-0000-000000001003',
 'a0000000-0000-0000-0000-000000000010', 'open',
 NOW() - INTERVAL '6 hours', 'La firma es el jueves?', 0, false),

-- Tenant B
('b0000000-0000-0000-0000-00000000a001', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-000000009001', 'b0000000-0000-0000-0000-000000001001',
 'b0000000-0000-0000-0000-000000000010', 'open',
 NOW() - INTERVAL '4 hours', 'Cuando estaria el presupuesto?', 2, false);


-- =============================================
-- 14. WA_MESSAGES (historial de conversaciones)
-- =============================================

-- === Conversacion 1: Juan Perez <-> Abogado (compraventa) ===
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, sender_id, content, message_type, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_001', 'client', '5215512345678',
 'Buenos dias, ya me pidieron unos documentos para la compraventa', 'text', 'delivered',
 NOW() - INTERVAL '3 hours'),
('a0000000-0000-0000-0000-00000000b002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_002', 'agent', 'a0000000-0000-0000-0000-000000000012',
 'Buen dia Sr. Perez! Si, necesitamos su constancia de situacion fiscal y la escritura antecedente.', 'text', 'read',
 NOW() - INTERVAL '2 hours' - INTERVAL '50 minutes'),
('a0000000-0000-0000-0000-00000000b003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_003', 'client', '5215512345678',
 'Aqui le mando mi INE por si la necesita', 'image', 'delivered',
 NOW() - INTERVAL '2 hours'),
('a0000000-0000-0000-0000-00000000b004', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_004', 'system', NULL,
 'Documento recibido y almacenado. Tipo detectado: INE (confianza: 95%)', 'text', 'delivered',
 NOW() - INTERVAL '1 hour' - INTERVAL '55 minutes'),
('a0000000-0000-0000-0000-00000000b005', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_005', 'client', '5215512345678',
 'Ya tengo la constancia fiscal, la envio por aqui?', 'text', 'delivered',
 NOW() - INTERVAL '30 minutes'),
('a0000000-0000-0000-0000-00000000b006', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_006', 'client', '5215512345678',
 'Tambien tengo el predial', 'text', 'delivered',
 NOW() - INTERVAL '28 minutes'),
('a0000000-0000-0000-0000-00000000b007', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_007', 'client', '5215512345678',
 'constancia_fiscal_2025.pdf', 'document', 'delivered',
 NOW() - INTERVAL '25 minutes');

-- === Conversacion 2: Constructora Bajio <-> Asistente (donacion, AI) ===
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, sender_id, content, message_type, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b010', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a002', 'wamid_test_010', 'agent', 'a0000000-0000-0000-0000-000000000011',
 'Buen dia, le informamos que para la donacion necesitamos los siguientes documentos...', 'text', 'read',
 NOW() - INTERVAL '3 days'),
('a0000000-0000-0000-0000-00000000b011', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a002', 'wamid_test_011', 'client', '5215544332211',
 'Entendido, estamos reuniendo la documentacion', 'text', 'delivered',
 NOW() - INTERVAL '2 days'),
('a0000000-0000-0000-0000-00000000b012', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a002', 'wamid_test_012', 'ai', NULL,
 'Recordatorio automatico: Faltan por entregar el acta constitutiva y poder del representante legal para el expediente EXP-2025-002.', 'text', 'delivered',
 NOW() - INTERVAL '1 day'),
('a0000000-0000-0000-0000-00000000b013', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a002', 'wamid_test_013', 'client', '5215544332211',
 'Necesitamos el acta constitutiva actualizada', 'text', 'delivered',
 NOW() - INTERVAL '2 hours');

-- === Conversacion 3: Ana Martinez - cerrada (historica) ===
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, content, message_type, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b020', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a003', 'wamid_test_020', 'system',
 'Su expediente EXP-2024-015 ha sido completado. Puede pasar a recoger su escritura.', 'text', 'read',
 NOW() - INTERVAL '31 days'),
('a0000000-0000-0000-0000-00000000b021', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a003', 'wamid_test_021', 'client',
 'Gracias, todo recibido', 'text', 'delivered',
 NOW() - INTERVAL '30 days');

-- === Conversacion 4: Contacto desconocido ===
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, sender_id, content, message_type, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b030', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a004', 'wamid_test_030', 'client', '5215511112222',
 'Hola, me gustaria cotizar una escritura', 'text', 'delivered',
 NOW() - INTERVAL '1 day');

-- === Conversacion 5: Ana con testamento (firma proxima) ===
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, content, message_type, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b040', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a005', 'wamid_test_040', 'agent',
 'Le confirmo que la firma del testamento esta programada para el jueves a las 11:00am', 'text', 'read',
 NOW() - INTERVAL '8 hours'),
('a0000000-0000-0000-0000-00000000b041', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a005', 'wamid_test_041', 'client',
 'La firma es el jueves?', 'text', 'delivered',
 NOW() - INTERVAL '6 hours'),
-- Mensaje con status failed (para probar lifecycle)
('a0000000-0000-0000-0000-00000000b042', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a005', 'wamid_test_042', 'agent',
 'Si, el jueves 10 de marzo a las 11am. Por favor llegue 15 min antes.', 'text', 'failed',
 NOW() - INTERVAL '5 hours');

-- Mensaje de audio (para probar tipo audio)
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, sender_id, content, message_type, media_url, status, timestamp) VALUES
('a0000000-0000-0000-0000-00000000b050', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000a001', 'wamid_test_050', 'client', '5215512345678',
 '[Audio]', 'audio', NULL, 'delivered',
 NOW() - INTERVAL '20 minutes');

-- Tenant B
INSERT INTO wa_messages (id, tenant_id, conversation_id, whatsapp_message_id, sender_type, sender_id, content, message_type, status, timestamp) VALUES
('b0000000-0000-0000-0000-00000000b001', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-00000000a001', 'wamid_test_b001', 'client', '5213312345678',
 'Buen dia, quisiera saber el presupuesto para mi escritura', 'text', 'delivered',
 NOW() - INTERVAL '5 hours'),
('b0000000-0000-0000-0000-00000000b002', 'b0000000-0000-0000-0000-000000000001',
 'b0000000-0000-0000-0000-00000000a001', 'wamid_test_b002', 'client', '5213312345678',
 'Cuando estaria el presupuesto?', 'text', 'delivered',
 NOW() - INTERVAL '4 hours');


-- =============================================
-- 15. WA_TEMPLATES (plantillas de WhatsApp)
-- =============================================

INSERT INTO wa_templates (id, tenant_id, name, display_name, category, language, status, is_active, components) VALUES
-- Template APROBADO: notificacion de caso
('a0000000-0000-0000-0000-00000000c001', 'a0000000-0000-0000-0000-000000000001',
 'case_status_update', 'Actualizacion de Expediente', 'utility', 'es', 'APPROVED', true,
 '[{"type":"header","format":"text","text":"Notaria 14 - Actualizacion"},{"type":"body","text":"Estimado(a) {{1}}, su expediente {{2}} ha cambiado a estado: {{3}}. Para mas informacion contactenos."},{"type":"footer","text":"Notaria 14 - Morelia"}]'::jsonb),

-- Template APROBADO: recordatorio de cita
('a0000000-0000-0000-0000-00000000c002', 'a0000000-0000-0000-0000-000000000001',
 'appointment_reminder', 'Recordatorio de Cita', 'utility', 'es', 'APPROVED', true,
 '[{"type":"body","text":"Estimado(a) {{1}}, le recordamos su cita el dia {{2}} a las {{3}}. Direccion: Av. Madero 200, Morelia."},{"type":"footer","text":"Notaria 14"}]'::jsonb),

-- Template APROBADO: bienvenida
('a0000000-0000-0000-0000-00000000c003', 'a0000000-0000-0000-0000-000000000001',
 'welcome_message', 'Mensaje de Bienvenida', 'utility', 'es', 'APPROVED', true,
 '[{"type":"body","text":"Bienvenido(a) a Notaria 14. Hemos registrado su contacto. Un asesor le atendera pronto."}]'::jsonb),

-- Template PENDIENTE (para probar estado pending)
('a0000000-0000-0000-0000-00000000c004', 'a0000000-0000-0000-0000-000000000001',
 'payment_confirmation', 'Confirmacion de Pago', 'utility', 'es', 'PENDING', true,
 '[{"type":"body","text":"Confirmamos su pago de ${{1}} por concepto de {{2}} para expediente {{3}}."}]'::jsonb),

-- Template RECHAZADO (para probar estado rejected)
('a0000000-0000-0000-0000-00000000c005', 'a0000000-0000-0000-0000-000000000001',
 'marketing_promo', 'Promocion Servicios', 'marketing', 'es', 'REJECTED', false,
 '[{"type":"body","text":"Aproveche nuestras promociones en servicios notariales!"}]'::jsonb),

-- Tenant B: template basico
('b0000000-0000-0000-0000-00000000c001', 'b0000000-0000-0000-0000-000000000001',
 'case_update_n7', 'Actualizacion Expediente N7', 'utility', 'es', 'APPROVED', true,
 '[{"type":"body","text":"Notaria 7 informa: su expediente {{1}} tiene una actualizacion: {{2}}."}]'::jsonb);


-- =============================================
-- 16. WA_NOTIFICATION_RULES (reglas de notificacion)
-- =============================================

INSERT INTO wa_notification_rules (id, tenant_id, event_type, template_id, is_active, notify_staff, message_text, conditions) VALUES
-- Notificar al cliente cuando se crea un caso
('a0000000-0000-0000-0000-00000000d001', 'a0000000-0000-0000-0000-000000000001',
 'case_created', 'a0000000-0000-0000-0000-00000000c003', true, false,
 NULL, '{}'::jsonb),

-- Notificar al cliente cuando cambia el estado del caso
('a0000000-0000-0000-0000-00000000d002', 'a0000000-0000-0000-0000-000000000001',
 'status_change', 'a0000000-0000-0000-0000-00000000c001', true, false,
 NULL, '{}'::jsonb),

-- Alertar al STAFF cuando un tramite vence
('a0000000-0000-0000-0000-00000000d003', 'a0000000-0000-0000-0000-000000000001',
 'tramite_vencido', NULL, true, true,
 'ALERTA: El tramite "{{tramite_nombre}}" del expediente {{case_number}} ha vencido. Atencion inmediata requerida.',
 '{"roles": ["notario", "abogado"]}'::jsonb),

-- Notificar al cliente cuando se completa el checklist
('a0000000-0000-0000-0000-00000000d004', 'a0000000-0000-0000-0000-000000000001',
 'checklist_complete', NULL, true, false,
 'Todos los documentos de su expediente {{case_number}} han sido recibidos y validados. Procederemos con la siguiente etapa.',
 '{}'::jsonb),

-- Notificar pago recibido (INACTIVA - para probar toggle)
('a0000000-0000-0000-0000-00000000d005', 'a0000000-0000-0000-0000-000000000001',
 'payment_received', NULL, false, false,
 'Hemos registrado su pago por ${{monto}}. Gracias.',
 '{}'::jsonb),

-- Alertar staff cuando se recibe pago
('a0000000-0000-0000-0000-00000000d006', 'a0000000-0000-0000-0000-000000000001',
 'payment_received', NULL, true, true,
 'Pago recibido: ${{monto}} - {{concepto}} para expediente {{case_number}}',
 '{"roles": ["asistente", "admin"]}'::jsonb),

-- Auto-reply AI habilitado (P0-2)
('a0000000-0000-0000-0000-00000000d007', 'a0000000-0000-0000-0000-000000000001',
 'auto_reply', NULL, true, false,
 NULL, '{}'::jsonb),

-- Notificar cuando se actualiza un item del checklist (P0-1)
('a0000000-0000-0000-0000-00000000d008', 'a0000000-0000-0000-0000-000000000001',
 'checklist_updated', NULL, true, true,
 'Se ha recibido el documento "{{documento}}" para el expediente {{case_number}}.',
 '{"roles": ["asistente"]}'::jsonb),

-- Daily digest para staff (P0-1)
('a0000000-0000-0000-0000-00000000d009', 'a0000000-0000-0000-0000-000000000001',
 'daily_digest', NULL, true, true,
 NULL, '{"roles": ["notario", "asistente"]}'::jsonb),

-- Tenant B: regla basica
('b0000000-0000-0000-0000-00000000d001', 'b0000000-0000-0000-0000-000000000001',
 'case_created', 'b0000000-0000-0000-0000-00000000c001', true, true,
 NULL, '{}'::jsonb);


-- =============================================
-- 17. WA_DOCUMENT_EXTRACTIONS (extraccion via WA)
-- =============================================

INSERT INTO wa_document_extractions (id, tenant_id, message_id, case_id, document_type, extracted_data, confidence, status) VALUES
-- INE extraida exitosamente
('a0000000-0000-0000-0000-00000000e001', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000b003', 'a0000000-0000-0000-0000-000000001001',
 'ine',
 '{"nombre":"Juan Perez Garcia","curp":"PEGJ800315HMNRRC09","clave_elector":"PRGRJN80031509H200","seccion":"0512","vigencia":"2029","domicilio":"Av. Madero 100, Col. Centro, Morelia, Mich."}'::jsonb,
 0.95, 'completed'),
-- Constancia fiscal en proceso
('a0000000-0000-0000-0000-00000000e002', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000b007', 'a0000000-0000-0000-0000-000000001001',
 'constancia_fiscal',
 '{"rfc":"PEGJ800315AB1","nombre":"PEREZ GARCIA JUAN","regimen":"612 - Personas Fisicas con Actividades Empresariales","estatus":"Activo"}'::jsonb,
 0.88, 'completed'),
-- Extraccion fallida (para probar error handling)
('a0000000-0000-0000-0000-00000000e003', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-00000000b050', NULL,
 NULL, '{}'::jsonb, 0.0, 'failed');


-- =============================================
-- 18. WA_COMMAND_LOG (historial de comandos staff)
-- =============================================

INSERT INTO wa_command_log (id, tenant_id, staff_phone, user_id, command, payload, result, response_preview, created_at) VALUES
('a0000000-0000-0000-0000-00000000f001', 'a0000000-0000-0000-0000-000000000001',
 '5215599990001', 'a0000000-0000-0000-0000-000000000010',
 'menu', '{"content":"menu","msg_type":"text"}'::jsonb,
 'ok', 'Menu principal mostrado', NOW() - INTERVAL '2 hours'),
('a0000000-0000-0000-0000-00000000f002', 'a0000000-0000-0000-0000-000000000001',
 '5215599990001', 'a0000000-0000-0000-0000-000000000010',
 'main_cases', '{"content":"Mis Expedientes","msg_type":"interactive"}'::jsonb,
 'ok', 'Listado de 3 expedientes', NOW() - INTERVAL '1 hour' - INTERVAL '55 minutes'),
('a0000000-0000-0000-0000-00000000f003', 'a0000000-0000-0000-0000-000000000001',
 '5215599990003', 'a0000000-0000-0000-0000-000000000012',
 'main_alerts', '{"content":"Alertas","msg_type":"interactive"}'::jsonb,
 'ok', '1 tramite vencido', NOW() - INTERVAL '1 hour'),
('a0000000-0000-0000-0000-00000000f004', 'a0000000-0000-0000-0000-000000000001',
 '5215599990002', 'a0000000-0000-0000-0000-000000000011',
 'main_summary', '{"content":"Resumen","msg_type":"interactive"}'::jsonb,
 'ok', 'Resumen: 5 activos, 3 pendientes', NOW() - INTERVAL '30 minutes');


-- =============================================
-- 19. CASE ACTIVITY LOG (para historial en staff menu)
-- =============================================

INSERT INTO case_activity_log (id, tenant_id, case_id, user_id, action, description, entity_type, created_at) VALUES
('a0000000-0000-0000-0000-00000000ff01', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000012',
 'create_case', 'Expediente creado: Compraventa Col. Centro', 'case', NOW() - INTERVAL '15 days'),
('a0000000-0000-0000-0000-00000000ff02', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000012',
 'transition_case', 'Estado: borrador -> en_revision', 'case', NOW() - INTERVAL '10 days'),
('a0000000-0000-0000-0000-00000000ff03', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001001', 'a0000000-0000-0000-0000-000000000011',
 'update_checklist_item', 'INE Comprador: pendiente -> recibido', 'case', NOW() - INTERVAL '5 days'),
('a0000000-0000-0000-0000-00000000ff04', 'a0000000-0000-0000-0000-000000000001',
 'a0000000-0000-0000-0000-000000001004', 'a0000000-0000-0000-0000-000000000012',
 'complete_tramite', 'Pago ISR ante SAT completado', 'case', NOW() - INTERVAL '5 days');


COMMIT;

-- =============================================
-- RESUMEN DE ESCENARIOS CUBIERTOS
-- =============================================
--
-- ROUTING WEBHOOK:
--   - Numero plataforma (is_platform=true): 910944215432464 -> tenant A
--   - Numero dedicado N14 (is_platform=false): DEDICATED_N14_TEST_001 -> tenant A
--   - Numero dedicado N7 (is_platform=false): DEDICATED_N7_TEST_001 -> tenant B
--
-- STAFF (menus interactivos via WA):
--   - 5215599990001 -> Notario (tenant A) - prueba menu principal, expedientes
--   - 5215599990002 -> Asistente (tenant A) - prueba resumen, notificaciones
--   - 5215599990003 -> Abogado (tenant A) - prueba alertas, tramites
--   - 5215599990004 -> Admin INACTIVO (tenant A) - no debe recibir menu
--   - 5213399990001 -> Notario (tenant B) - prueba cross-tenant en plataforma
--   - 5213399990002 -> Asistente (tenant B)
--
-- CLIENTES (mensajes entrantes):
--   - 5215512345678 -> Juan Perez (vinculado, conv abierta, caso activo, mensajes no leidos)
--   - 5215587654321 -> Ana Martinez (vinculada, conv cerrada + conv abierta testamento)
--   - 5215544332211 -> Constructora Bajio (empresa, conv con AI enabled)
--   - 5215511112222 -> Desconocido (sin vincular, conv pendiente)
--   - 5215500001111 -> Bloqueado (contacto bloqueado)
--   - 5213312345678 -> Sofia Ramirez (tenant B, conv abierta)
--
-- UNKNOWN SENDER (plataforma):
--   - Cualquier numero NO en wa_staff_phones enviando al 910944215432464
--     -> Debe recibir mensaje de rechazo
--
-- CASES (workflow completo):
--   - EXP-2025-001: compraventa, en_revision, con checklist mixto, pagos parciales
--   - EXP-2025-002: donacion, checklist_pendiente, docs pendientes, tramite proximo
--   - EXP-2025-003: testamento, en_firma, firma programada en calendario
--   - EXP-2025-004: poder, tramites_gobierno, tramite vencido (alerta!), pagos
--   - EXP-2024-015: compraventa, cerrado (historico, pagos completos)
--   - EXP-2025-006: sociedad, borrador (recien creado)
--
-- MENSAJES (tipos variados):
--   - text, image, document, audio
--   - sender_type: client, agent, system, ai
--   - status: sent, delivered, read, failed
--
-- TEMPLATES: APPROVED (3), PENDING (1), REJECTED (1)
-- NOTIF RULES: activas (5), inactiva (1), staff-only (2), client-only (3)
-- EXTRACTIONS: completed (2), failed (1)
-- CALENDAR: firma, cita, vencimiento proximo, vencimiento pasado
