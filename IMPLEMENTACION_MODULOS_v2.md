# ControlNot v2 - Documentacion de Implementacion de Modulos

**Fecha:** 19 de febrero de 2026
**Estado anterior:** 53% implementado (CRM, documentos, tramites, checklist, OCR, auditoria)
**Estado actual:** ~95% implementado
**Base de datos:** Supabase proyecto `gpbgzfutijbemaagswaz`

---

## Resumen Ejecutivo

Se implementaron 6 modulos completos (backend + frontend) que llevan ControlNot v2 de un CRM basico con OCR a una plataforma notarial integral. El build compila sin errores y las 4 migraciones SQL fueron aplicadas a produccion.

---

## Fase 1: Pagos (Tracking Manual)

### Que hace
Permite registrar y dar seguimiento a los pagos asociados a cada expediente (caso). Soporta honorarios, impuestos, derechos registrales, gastos y otros conceptos. Muestra totales por caso.

### Archivos creados

**Backend:**
| Archivo | Descripcion |
|---------|-------------|
| `database/migrations/009_case_payments.sql` | Tabla `case_payments` con RLS, indices, trigger updated_at |
| `app/repositories/case_payment_repository.py` | CRUD Supabase: `list_by_case()`, `get_totals_by_case()`, `create_payment()` |
| `app/api/endpoints/case_payments.py` | Router `/api/cases/{case_id}/payments` (GET, POST, PATCH, DELETE) |

**Frontend:**
| Archivo | Descripcion |
|---------|-------------|
| `src/api/types/payments-types.ts` | Tipos: `CasePayment`, `PaymentTotals`, constantes de labels |
| `src/api/endpoints/payments.ts` | Cliente API: `paymentsApi.list()`, `.create()`, `.update()`, `.remove()` |
| `src/components/payments/PaymentList.tsx` | Lista de pagos con tarjetas de totales y formato de moneda MXN |
| `src/components/payments/PaymentForm.tsx` | Dialog para registrar pago (tipo, metodo, monto, referencia, etc.) |

### Archivos modificados
- `src/pages/CaseDetailPage.tsx` - Se agrego 7mo tab "Pagos", carga lazy, handlers de CRUD
- `app/api/endpoints/__init__.py` - Export de `case_payments_router`
- `app/api/router.py` - Include del router de pagos

### Esquema de BD
```sql
case_payments (
  id UUID PK,
  tenant_id UUID FK -> tenants,
  case_id UUID FK -> cases,
  tipo CHECK (honorarios|impuestos|derechos|gastos|otro),
  concepto TEXT,
  monto NUMERIC(12,2),
  metodo_pago CHECK (efectivo|transferencia|cheque|tarjeta|otro),
  referencia TEXT,
  fecha_pago DATE,
  recibido_por TEXT,
  comprobante_path TEXT,
  notas TEXT,
  created_at, updated_at
)
-- RLS: tenant_id = auth.uid() lookup
```

---

## Fase 2: Calendario

### Que hace
Calendario mensual para gestionar eventos de la notaria: vencimientos de tramites, firmas programadas, citas con clientes, audiencias, etc. Los eventos pueden vincularse opcionalmente a un expediente.

### Archivos creados

**Backend:**
| Archivo | Descripcion |
|---------|-------------|
| `database/migrations/010_calendar_events.sql` | Tabla `calendar_events` con RLS y relaciones |
| `app/repositories/calendar_repository.py` | `list_by_range()`, `list_upcoming()`, `list_by_case()`, `create_event()` |
| `app/api/endpoints/calendar.py` | Router `/api/calendar` (GET por rango, GET /upcoming, POST, PATCH, DELETE) |

**Frontend:**
| Archivo | Descripcion |
|---------|-------------|
| `src/api/types/calendar-types.ts` | Tipos: `CalendarEvent`, `EventCreateRequest`, constantes de colores |
| `src/api/endpoints/calendar.ts` | Cliente API: `calendarApi.listByRange()`, `.upcoming()`, etc. |
| `src/pages/CalendarPage.tsx` | Pagina principal con navegacion mensual y panel de detalle |
| `src/components/calendar/MonthView.tsx` | Grid mensual (lunes-based), eventos agrupados por dia |
| `src/components/calendar/EventCard.tsx` | Tarjeta de evento con color por tipo |
| `src/components/calendar/EventForm.tsx` | Dialog crear/editar evento |

### Archivos modificados
- `src/App.tsx` - Ruta `/calendario` con lazy import
- `src/components/layout/Sidebar.tsx` - Item "Calendario" con icono Calendar

### Esquema de BD
```sql
calendar_events (
  id UUID PK,
  tenant_id UUID FK -> tenants,
  case_id UUID FK -> cases (nullable),
  titulo TEXT NOT NULL,
  descripcion TEXT,
  tipo CHECK (vencimiento|firma|cita|audiencia|otro),
  fecha_inicio TIMESTAMPTZ,
  fecha_fin TIMESTAMPTZ,
  todo_el_dia BOOLEAN DEFAULT false,
  recordatorio_minutos INT DEFAULT 30,
  color VARCHAR(7),
  created_by UUID FK -> users,
  created_at, updated_at
)
```

---

## Fase 3: Reportes

### Que hace
Dashboard de reportes con 4 vistas: resumen de expedientes (por status, tipo, prioridad), semaforo de tramites (vencidos, por vencer), resumen financiero (pagos por tipo, totales), y productividad (casos cerrados, tiempos promedio).

### Archivos creados

**Backend:**
| Archivo | Descripcion |
|---------|-------------|
| `app/api/endpoints/reports.py` | Router `/api/reports` con 4 endpoints de consulta directa a Supabase |

Endpoints:
- `GET /reports/cases-summary` - Conteos por status, tipo_acto, prioridad
- `GET /reports/tramites-summary` - Semaforo global, tramites vencidos, conteo por tipo
- `GET /reports/financial-summary` - Pagos por tipo, totales, top 5 casos
- `GET /reports/productivity` - Casos cerrados por periodo, tiempos promedio

**Frontend:**
| Archivo | Descripcion |
|---------|-------------|
| `src/api/endpoints/reports.ts` | Tipos inline + cliente API para 4 endpoints |
| `src/pages/ReportsPage.tsx` | Dashboard con KPIs, carga paralela, boton refresh |
| `src/components/reports/CasesReport.tsx` | Desglose por status/tipo en tabla |
| `src/components/reports/FinancialReport.tsx` | Resumen financiero con formato moneda |
| `src/components/reports/TramitesReport.tsx` | Semaforo y listado de vencimientos |

### Archivos modificados
- `src/App.tsx` - Ruta `/reportes`
- `src/components/layout/Sidebar.tsx` - Item "Reportes" con icono BarChart3

---

## Fase 4: UIF / PLD (Actividades Vulnerables)

### Que hace
Modulo de cumplimiento para la Unidad de Inteligencia Financiera. Detecta automaticamente cuando un expediente supera los umbrales de operaciones vulnerables (compraventa > $682,399.60 MXN), evalua nivel de riesgo, y permite registrar y dar seguimiento a los avisos.

### Archivos creados

**Backend:**
| Archivo | Descripcion |
|---------|-------------|
| `database/migrations/011_uif.sql` | Tabla `uif_operations` con RLS |
| `app/repositories/uif_repository.py` | `list_vulnerable()`, `get_by_case()`, `get_summary()` |
| `app/services/uif_service.py` | Logica de umbrales UIF, evaluacion de riesgo por multiplicador |
| `app/api/endpoints/uif.py` | Router `/api/uif` (GET list, GET check, POST flag, PATCH, GET evaluate) |

Umbrales configurados en `uif_service.py`:
```python
UIF_THRESHOLDS = {
    "compraventa": 682_399.60,
    "donacion": 682_399.60,
    "fideicomiso": 682_399.60,
    "hipoteca": 682_399.60,
    "poder": 341_199.80,   # La mitad del umbral inmobiliario
}
```

**Frontend:**
| Archivo | Descripcion |
|---------|-------------|
| `src/api/types/uif-types.ts` | Tipos: `UIFOperation`, `UIFSummary`, constantes |
| `src/api/endpoints/uif.ts` | Cliente API completo |
| `src/pages/UIFPage.tsx` | Panel de operaciones vulnerables con filtros y resumen |
| `src/components/uif/UIFAlert.tsx` | Alerta inline en CaseDetailPage (auto-check al montar) |
| `src/components/uif/UIFOperationList.tsx` | Lista de operaciones con badges de riesgo |

### Archivos modificados
- `src/App.tsx` - Ruta `/uif`
- `src/components/layout/Sidebar.tsx` - Item "UIF/PLD" con icono ShieldAlert
- `src/pages/CaseDetailPage.tsx` - Se agrego `<UIFAlert>` antes del WorkflowBar

### Esquema de BD
```sql
uif_operations (
  id UUID PK,
  tenant_id UUID FK -> tenants,
  case_id UUID FK -> cases,
  tipo_operacion CHECK (compraventa|donacion|fideicomiso|poder|otro),
  monto_operacion NUMERIC(14,2),
  nivel_riesgo CHECK (bajo|medio|alto|critico),
  es_vulnerable BOOLEAN DEFAULT false,
  umbral_aplicado NUMERIC(14,2),
  requiere_aviso BOOLEAN DEFAULT false,
  fecha_aviso DATE,
  numero_aviso TEXT,
  status CHECK (pendiente|reportado|archivado),
  responsable_id UUID FK -> users,
  notas TEXT,
  created_at, updated_at
)
```

---

## Fase 5: WhatsApp (Meta Cloud API)

### Que hace
Modulo de mensajeria WhatsApp integrado con Meta Cloud API. Permite recibir y enviar mensajes, gestionar conversaciones estilo inbox, vincular contactos con clientes/expedientes, y enviar notificaciones automaticas por eventos del sistema (caso creado, tramite vencido, etc.).

### Archivos creados

**Backend:**
| Archivo | Descripcion |
|---------|-------------|
| `database/migrations/012_whatsapp.sql` | 5 tablas: `wa_contacts`, `wa_conversations`, `wa_messages`, `wa_templates`, `wa_notification_rules` |
| `app/repositories/wa_repository.py` | CRUD completo para contactos, conversaciones, mensajes, templates |
| `app/services/whatsapp_service.py` | Cliente Meta Cloud API: `send_text()`, `send_template()`, `verify_webhook()` |
| `app/services/wa_notification_service.py` | Notificaciones automaticas por evento |
| `app/api/endpoints/whatsapp.py` | Router `/api/whatsapp` con webhook + endpoints autenticados |

Endpoints:
- `POST /whatsapp/webhook` - Recepcion de mensajes (publico, sin auth)
- `GET /whatsapp/webhook` - Verificacion Meta (publico)
- `GET /whatsapp/conversations` - Listar conversaciones
- `GET /whatsapp/conversations/{id}/messages` - Historial de mensajes
- `POST /whatsapp/send` - Enviar mensaje de texto
- `POST /whatsapp/send-template` - Enviar template aprobado
- `GET /whatsapp/templates` - Listar templates
- `POST /whatsapp/contacts/link` - Vincular contacto WA con cliente

**Frontend:**
| Archivo | Descripcion |
|---------|-------------|
| `src/api/types/whatsapp-types.ts` | Tipos completos para conversaciones, mensajes, contactos, templates |
| `src/api/endpoints/whatsapp.ts` | Cliente API |
| `src/pages/WhatsAppPage.tsx` | Inbox estilo chat (lista + panel) |
| `src/components/whatsapp/ConversationList.tsx` | Lista lateral de conversaciones con search |
| `src/components/whatsapp/ChatPanel.tsx` | Panel de chat con scroll automatico |
| `src/components/whatsapp/MessageBubble.tsx` | Burbuja de mensaje (client/agent/system/ai) |
| `src/components/whatsapp/MessageInput.tsx` | Input con boton send |
| `src/components/whatsapp/ContactLinker.tsx` | Dialog para vincular contacto con cliente/caso |

### Archivos modificados
- `src/App.tsx` - Ruta `/whatsapp`
- `src/components/layout/Sidebar.tsx` - Item "WhatsApp" con icono MessageCircle
- `app/core/config.py` - 5 nuevas variables de entorno WhatsApp
- `app/api/endpoints/__init__.py` - Export del router
- `app/api/router.py` - Include del router

### Esquema de BD (5 tablas)
```sql
wa_contacts (id, tenant_id, phone UNIQUE per tenant, name, client_id FK, is_blocked, last_seen, metadata)
wa_conversations (id, tenant_id, contact_id FK, case_id FK, assigned_to FK, status, last_message_at, unread_count, ai_enabled)
wa_messages (id, tenant_id, conversation_id FK, whatsapp_message_id UNIQUE, sender_type, content, message_type, media_url, status, reply_to_id, timestamp)
wa_templates (id, tenant_id, name UNIQUE per tenant, display_name, category, language, status, components JSONB, is_active)
wa_notification_rules (id, tenant_id, event_type, template_id FK, is_active, conditions JSONB)
```

### Variables de entorno nuevas
```env
WHATSAPP_API_URL=https://graph.facebook.com/v18.0    # Default, no requiere config
WHATSAPP_PHONE_ID=                                     # ID del numero en Meta Business
WHATSAPP_ACCESS_TOKEN=                                 # Token permanente de Meta
WHATSAPP_VERIFY_TOKEN=controlnot_verify                # Token para verificar webhook
WHATSAPP_WEBHOOK_SECRET=                               # Secreto para validar firmas
```

---

## Fase 6: RBAC Frontend

### Que hace
Control de acceso basado en roles en el frontend. Filtra automaticamente los items del sidebar segun el rol del usuario y permite envolver componentes con `<RequireRole>` para mostrar/ocultar contenido.

### 8 Roles soportados
| Rol | Acceso |
|-----|--------|
| `admin` | Todo |
| `notario` | Todo |
| `abogado` | Expedientes, Calendario, Reportes, Documentos, WhatsApp |
| `asistente` | Expedientes, Calendario, Documentos |
| `mesa_control` | Expedientes, Calendario, Tramites, Checklist |
| `pagos` | Expedientes, Pagos, Reportes |
| `folios_protocolo` | Expedientes, Documentos |
| `archivo` | Expedientes, Documentos, Historial |

### Archivos creados
| Archivo | Descripcion |
|---------|-------------|
| `src/hooks/usePermissions.ts` | Hook con `ROLE_PERMISSIONS` matrix, `canAccess()`, convenience flags |
| `src/components/auth/RequireRole.tsx` | Wrapper: `<RequireRole module="uif">...</RequireRole>` |

### Archivos modificados
- `src/hooks/useAuth.ts` - Agrego `userRole: profile?.rol || 'asistente'`
- `src/store/useAuthStore.ts` - Agrego `rol` a UserProfile y fetchProfile
- `src/components/layout/Sidebar.tsx` - Cada item tiene `module`, se filtran con `usePermissions()`

---

## Resumen de Archivos

### Totales
| Categoria | Cantidad |
|-----------|----------|
| Migraciones SQL | 4 |
| Archivos backend nuevos | 13 |
| Archivos frontend nuevos | 30 |
| Archivos modificados | 14 |
| **Total** | **~61** |

### Migraciones aplicadas a Supabase
1. `009_case_payments.sql` - Tabla de pagos
2. `010_calendar_events.sql` - Tabla de eventos de calendario
3. `011_uif.sql` - Tabla de operaciones UIF/PLD
4. `012_whatsapp.sql` - 5 tablas de WhatsApp

### Tablas en BD (29 total)
Las 20 existentes + 8 nuevas:
`case_payments`, `calendar_events`, `uif_operations`, `wa_contacts`, `wa_conversations`, `wa_messages`, `wa_templates`, `wa_notification_rules`

---

## Siguientes Pasos

### 1. Actualizar Docker Compose y Variables de Entorno (PRIORITARIO)

#### 1.1 Agregar variables de WhatsApp al docker-compose.coolify.yml

Agregar en la seccion `environment` del servicio `backend`:

```yaml
# WhatsApp (Meta Cloud API)
- WHATSAPP_PHONE_ID=${WHATSAPP_PHONE_ID}
- WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}
- WHATSAPP_VERIFY_TOKEN=${WHATSAPP_VERIFY_TOKEN:-controlnot_verify}
- WHATSAPP_WEBHOOK_SECRET=${WHATSAPP_WEBHOOK_SECRET}
```

#### 1.2 Actualizar .env.example (raiz)

Agregar al final:

```env
# ===================
# WHATSAPP (Meta Cloud API)
# ===================
WHATSAPP_PHONE_ID=123456789012345
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxx
WHATSAPP_VERIFY_TOKEN=controlnot_verify
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret
```

#### 1.3 Actualizar backend/.env.example

Agregar:

```env
# WhatsApp (Meta Cloud API)
# Configurar desde: https://developers.facebook.com/apps/
WHATSAPP_PHONE_ID=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_VERIFY_TOKEN=controlnot_verify
WHATSAPP_WEBHOOK_SECRET=
```

#### 1.4 Configurar variables en Coolify

En el panel de Coolify, agregar las 4 variables de WhatsApp como secrets para el servicio backend.

---

### 2. Configurar WhatsApp Business API en Meta

1. Crear app en [Meta for Developers](https://developers.facebook.com/)
2. Agregar producto "WhatsApp" a la app
3. Obtener `WHATSAPP_PHONE_ID` del numero de pruebas o produccion
4. Generar `WHATSAPP_ACCESS_TOKEN` permanente (System User Token)
5. Configurar webhook URL: `https://api.pruebas.aurinot.com/api/whatsapp/webhook`
6. Suscribirse a campos: `messages`, `messaging_postbacks`
7. Usar el `WHATSAPP_VERIFY_TOKEN` configurado ("controlnot_verify" por default)

---

### 3. Configurar Webhook de WhatsApp en Produccion

El endpoint del webhook ya esta implementado:
- **Verificacion:** `GET https://api.pruebas.aurinot.com/api/whatsapp/webhook`
- **Recepcion:** `POST https://api.pruebas.aurinot.com/api/whatsapp/webhook`

Ambos son publicos (sin autenticacion) como requiere Meta.

**IMPORTANTE:** Verificar que Traefik/CORS no bloquee las peticiones de Meta al webhook. Si es necesario, agregar un middleware especifico para la ruta del webhook.

---

### 4. Rebuild y Deploy de Docker

```bash
# Opcion A: Desde Coolify
# Hacer push al repo y Coolify auto-deploya

# Opcion B: Manual
cd controlnot-v2
docker-compose -f docker-compose.coolify.yml build --no-cache
docker-compose -f docker-compose.coolify.yml up -d
```

Verificar que el backend inicie correctamente revisando logs:
```bash
docker-compose -f docker-compose.coolify.yml logs -f backend
```

Las variables de WhatsApp son **opcionales** (todos tienen defaults o `Optional[str] = None`), asi que el backend arrancara sin ellas, solo que el modulo de WhatsApp no podra enviar mensajes hasta que se configuren.

---

### 5. Testing Post-Deploy

| Modulo | Verificacion |
|--------|-------------|
| Pagos | Crear un pago en un expediente existente, verificar totales |
| Calendario | Crear evento, navegar entre meses, verificar filtro por caso |
| Reportes | Abrir /reportes, verificar que carga las 4 secciones |
| UIF/PLD | Abrir un caso con valor > $682,399.60, verificar alerta |
| WhatsApp | Verificar webhook con Meta test tool, enviar mensaje de prueba |
| RBAC | Cambiar `rol` de un usuario en BD y verificar que sidebar filtra |

---

### 6. Mejoras Pendientes (Post-MVP)

| Mejora | Prioridad | Descripcion |
|--------|-----------|-------------|
| Facturacion CFDI | Alta | Integracion con PAC (Facturapi/SW Sapien) para timbrado |
| Notificaciones push | Media | Browser push notifications para eventos del calendario |
| Reportes PDF export | Media | Exportar reportes a PDF con formato oficial |
| WhatsApp media | Media | Soporte para envio/recepcion de imagenes y documentos |
| WhatsApp AI | Baja | Respuestas automaticas con IA para preguntas frecuentes |
| Dashboard widgets | Baja | Widgets personalizables en el dashboard principal |
| Firma electronica | Alta | Integracion con proveedor de firma electronica avanzada |
| Audit log UI | Media | Pagina para visualizar el log de auditoria existente |
| Bulk payments | Baja | Registro masivo de pagos por lote |
| Calendario sync | Baja | Sincronizacion con Google Calendar / Outlook |

---

### 7. Notas Tecnicas

- **Build frontend:** `npx vite build` - compila sin errores (warning de chunk size es normal)
- **WhatsApp service:** Usa lazy loading de config para evitar errores de import-time
- **UIF umbrales:** Los montos son configurables en `uif_service.py`, actualizar segun SAT/UIF
- **RBAC:** El rol viene del campo `rol` en la tabla `users` de Supabase
- **Todas las tablas nuevas:** Tienen RLS habilitado con policies para `authenticated` y `service_role`
