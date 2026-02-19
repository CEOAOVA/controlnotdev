# Módulo CRM Expedientes — Release Notes

> **Versión:** 1.0.0
> **Fecha:** 2026-02-18
> **Estado:** Frontend completado — pendiente integración con backend API

---

## 1. Resumen Ejecutivo

El **Módulo CRM de Expedientes** es un sistema integral de gestión de escrituras notariales dentro de ControlNot v2. Permite a notarios y personal administrativo:

- **Crear y dar seguimiento** a expedientes (escrituras) desde borrador hasta cierre
- **Controlar el flujo de trabajo** de 12 pasos con transiciones validadas
- **Gestionar partes involucradas** (vendedores, compradores, donantes, etc.)
- **Verificar documentación requerida** mediante checklists categorizados
- **Monitorear trámites** con sistema de semáforo (en tiempo / por vencer / vencido)
- **Registrar actividad** en una línea de tiempo con notas y eventos

El módulo reemplaza el seguimiento manual de expedientes con un flujo digital trazable y auditable.

---

## 2. Nuevas Rutas y Navegación

### Rutas agregadas

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/cases` | `CasesPage` | Listado de expedientes con filtros y paginación |
| `/cases/:caseId` | `CaseDetailPage` | Detalle completo de un expediente |

### Navegación en Sidebar

Se agregó el enlace **"Expedientes"** con icono `Briefcase` (Lucide) en el sidebar principal (`Sidebar.tsx`), entre "Generar Documento" y "Templates":

```
Dashboard          → /
Generar Documento  → /generate
Expedientes        → /cases        ← NUEVO
Templates          → /templates
Historial          → /history
Configuración      → /settings
```

---

## 3. Flujo de Trabajo (Workflow)

### 14 Estados del Expediente

El ciclo de vida de un expediente comprende **12 estados lineales** + **2 estados especiales**:

```
┌──────────┐    ┌────────────┐    ┌─────────────────┐    ┌─────────────┐
│ Borrador │───→│ En Revisión│───→│Checklist Pendien.│───→│ Presupuesto │
└──────────┘    └────────────┘    └─────────────────┘    └─────────────┘
                                                                │
     ┌──────────────────────────────────────────────────────────┘
     ▼
┌──────────────────┐    ┌──────────┐    ┌───────────┐    ┌──────────────────┐
│Cálculo Impuestos │───→│ En Firma │───→│ Post-Firma│───→│Trámites Gobierno │
└──────────────────┘    └──────────┘    └───────────┘    └──────────────────┘
                                                                │
     ┌──────────────────────────────────────────────────────────┘
     ▼
┌─────────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────┐
│ Inscripción │───→│ Facturación │───→│ Entrega  │───→│ Cerrado │
└─────────────┘    └─────────────┘    └──────────┘    └─────────┘

Estados especiales (accesibles desde cualquier paso):
  ╳ Cancelado    ⏸ Suspendido (puede reanudarse)
```

### Tabla de Estados

| # | Clave | Etiqueta | Color Badge |
|---|-------|----------|-------------|
| 1 | `borrador` | Borrador | gris |
| 2 | `en_revision` | En Revisión | azul |
| 3 | `checklist_pendiente` | Checklist Pendiente | amarillo |
| 4 | `presupuesto` | Presupuesto | púrpura |
| 5 | `calculo_impuestos` | Cálculo de Impuestos | naranja |
| 6 | `en_firma` | En Firma | índigo |
| 7 | `postfirma` | Post-Firma | teal |
| 8 | `tramites_gobierno` | Trámites de Gobierno | cyan |
| 9 | `inscripcion` | Inscripción | lime |
| 10 | `facturacion` | Facturación | ámbar |
| 11 | `entrega` | Entrega | esmeralda |
| 12 | `cerrado` | Cerrado | verde |
| — | `cancelado` | Cancelado | rojo |
| — | `suspendido` | Suspendido | rosa |

### Transiciones

- Las transiciones disponibles se obtienen del backend (`available_transitions`)
- **Cancelar** y **Suspender** requieren confirmación con motivo obligatorio (campo de texto en diálogo modal)
- **Reanudar** permite reactivar un expediente suspendido

---

## 4. Página de Listado (`/cases`)

### Filtros (`CaseFilters`)

| Filtro | Tipo | Detalle |
|--------|------|---------|
| Búsqueda | Texto (debounce 300ms) | Busca por número de expediente o descripción |
| Estado | Select | Los 14 estados posibles |
| Tipo de documento | Select | Tipos de escritura (compraventa, donación, etc.) |
| Prioridad | Select | Baja, Normal, Alta, Urgente |
| Limpiar | Botón | Reinicia todos los filtros |

### Tabla de Expedientes (`CaseTable`)

**Vista desktop** — Tabla HTML con columnas:

| Columna | Contenido |
|---------|-----------|
| Expediente | Número de caso |
| Tipo | Tipo de documento |
| Estado | `CaseStatusBadge` con color |
| Prioridad | `CasePriorityBadge` |
| Fecha | Fecha de creación |
| Asignado | Persona asignada |

**Vista móvil** — Tarjetas apiladas con la misma información.

**Estados de la tabla:**
- **Cargando:** 5 filas skeleton animadas
- **Sin resultados:** Icono `Briefcase` + mensaje "No hay expedientes"
- **Con datos:** Click en fila navega a `/cases/:id`

### Crear Expediente (`CaseCreateDialog`)

Botón **"Nuevo Expediente"** abre un diálogo modal con campos:

| Campo | Requerido | Tipo |
|-------|-----------|------|
| Número de expediente | Sí | Texto |
| Cliente | Sí | Texto (ID) |
| Tipo de documento | No | Select |
| Prioridad | No | Select |
| Valor de operación | No | Número |
| Fecha de firma | No | Fecha |
| Descripción | No | Textarea |

---

## 5. Página de Detalle (`/cases/:caseId`)

### Encabezado

Muestra el **número de expediente**, `CaseStatusBadge` y `CasePriorityBadge` en línea.

### Barra de Workflow (`WorkflowBar`)

Barra horizontal de **12 pasos** con scroll horizontal en pantallas pequeñas (ancho mínimo 600px):

```
  ①──②──③──④──⑤──⑥──⑦──⑧──⑨──⑩──⑪──⑫
  ✓   ✓   ●   ○   ○   ○   ○   ○   ○   ○   ○   ○
```

- **Verde con ✓** = Paso completado
- **Azul sólido** = Paso actual
- **Gris vacío** = Paso pendiente
- **Cancelado/Suspendido** = Punto rojo/rosa con etiqueta (sin barra de pasos)

### Botones de Transición (`TransitionButtons`)

Se muestran dinámicamente según las transiciones disponibles del backend:

| Variante | Estilo | Uso |
|----------|--------|-----|
| `default` | Primario | Avanzar al siguiente estado |
| `destructive` | Rojo | Cancelar expediente |
| `outline` | Contorno | Suspender expediente |

### 6 Pestañas

#### 5.1 Resumen (`CaseEditForm`)

Formulario editable con los datos generales del expediente:

| Campo | Editable | Tipo |
|-------|----------|------|
| Número de expediente | No (solo lectura) | — |
| Tipo de documento | No (solo lectura) | — |
| Prioridad | Sí | Select |
| Número de escritura | Sí | Texto |
| Volumen | Sí | Texto |
| Folio real | Sí | Texto |
| Valor de operación | Sí | Número |
| Fecha de firma | Sí | Fecha |
| Descripción | Sí | Textarea |
| Notas | Sí | Textarea |

#### 5.2 Partes (`PartyList` + `PartyForm`)

CRUD completo de participantes del expediente.

**9 Roles disponibles:**

| Rol | Descripción típica |
|-----|-------------------|
| `vendedor` | Enajenante en compraventa |
| `comprador` | Adquiriente en compraventa |
| `donante` | Quien dona en donación |
| `donatario` | Quien recibe en donación |
| `testador` | Quien otorga testamento |
| `poderdante` | Quien otorga poder |
| `apoderado` | Quien recibe poder |
| `representante` | Representante legal |
| `otro` | Cualquier otro participante |

**Campos por parte:**

| Campo | Requerido | Tipo |
|-------|-----------|------|
| Rol | Sí | Select (9 opciones) |
| Tipo de persona | — | Física / Moral |
| Nombre | Sí | Texto |
| RFC | No | Texto |
| Email | No | Texto |
| Teléfono | No | Texto |
| Representante legal | No | Texto |

**Vista:** Tabla en desktop (Rol, Nombre, RFC, Tipo, Contacto, Acciones) / Tarjetas en móvil.

#### 5.3 Checklist (`ChecklistPanel`)

Sistema de verificación de documentos requeridos.

**6 Categorías:**

| Clave | Etiqueta |
|-------|----------|
| `parte_a` | Parte A |
| `parte_b` | Parte B |
| `inmueble` | Inmueble |
| `fiscal` | Fiscal |
| `gobierno` | Gobierno |
| `general` | General |

**6 Estados de cada item:**

| Estado | Color | Descripción |
|--------|-------|-------------|
| `pendiente` | Gris | No iniciado |
| `solicitado` | Azul | Se pidió el documento |
| `recibido` | Teal | Documento recibido |
| `aprobado` | Verde | Documento aprobado |
| `rechazado` | Rojo | Documento rechazado |
| `no_aplica` | Neutro | No aplica a este caso |

**Funcionalidades:**
- Items agrupados visualmente por categoría
- Badge "Obligatorio" en items requeridos
- Barra de progreso: `completados / total obligatorios (XX%)`
- Botón **"Inicializar desde Catálogo"** carga items predefinidos según tipo de documento
- Cambio de estado inline con dropdown por item
- Creación y eliminación manual de items

#### 5.4 Trámites (`TramiteList` + `TramiteForm`)

Gestión de procedimientos con monitoreo por semáforo.

**Sistema de Semáforo:**

| Color | Etiqueta | Significado |
|-------|----------|-------------|
| 🟢 Verde | En tiempo | Trámite dentro de plazo |
| 🟡 Amarillo | Por vencer | Próximo a fecha límite |
| 🔴 Rojo | Vencido | Pasó la fecha límite |
| ⚪ Gris | Sin fecha | No tiene fecha límite asignada |

> El semáforo es **calculado en el servidor** — el frontend solo renderiza el valor recibido.

**Campos por trámite:**

| Campo | Requerido | Tipo |
|-------|-----------|------|
| Tipo | Sí | Texto |
| Nombre | Sí | Texto |
| Fecha límite | No | Fecha |
| Costo | No | Número |
| Notas | No | Textarea |

**Acciones por trámite:**
- ✅ Marcar como completado
- ✏️ Editar
- 🗑️ Eliminar

#### 5.5 Documentos

Lista de documentos generados asociados al expediente. Consume `GET /cases/:id/documents`.

#### 5.6 Timeline (`ActivityTimeline` + `NoteInput`)

Bitácora cronológica de actividad del expediente.

- **Eventos automáticos:** Transiciones de estado, cambios de datos, acciones del sistema
- **Notas manuales:** Campo de texto con botón enviar (soporta `Ctrl+Enter`)
- **Formato:** Timeline vertical con línea izquierda, tarjetas con descripción + timestamp
- **Paginación:** `limit=50`, `offset=0` (por defecto)

---

## 6. Dashboard y Métricas

### 4 Tarjetas KPI

| Métrica | Fuente | Icono |
|---------|--------|-------|
| Total Expedientes | `dashboard.total_cases` | Briefcase |
| En Progreso | Suma de estados activos (excluye cerrado/cancelado) | Clock |
| Trámites Vencidos | `dashboard.overdue_tramites` | AlertCircle |
| Próximos a Vencer | `dashboard.upcoming_tramites` | TrendingUp |

### Semáforo Global

Indicadores visuales agregados de todos los trámites de la notaría:

```
🟢 12 en tiempo  🟡 5 por vencer  🔴 3 vencidos  ⚪ 8 sin fecha
```

### Secciones adicionales del Dashboard

- **Expedientes Recientes:** Los 5 casos más recientes con número, tipo, descripción y badge de estado
- **Por Estado:** Grid mostrando cada estado con badge de color y conteo (solo estados con count > 0)

---

## 7. Componentes Visuales

### `CaseStatusBadge`

Badge con color de fondo y texto según estado del expediente:

```
┌─────────────────────────────────────────────────┐
│ Estado              │ Fondo          │ Texto     │
├─────────────────────┼────────────────┼───────────┤
│ Borrador            │ gray-100       │ gray-700  │
│ En Revisión         │ blue-100       │ blue-700  │
│ Checklist Pendiente │ yellow-100     │ yellow-700│
│ Presupuesto         │ purple-100     │ purple-700│
│ Cálculo Impuestos   │ orange-100     │ orange-700│
│ En Firma            │ indigo-100     │ indigo-700│
│ Post-Firma          │ teal-100       │ teal-700  │
│ Trámites Gobierno   │ cyan-100       │ cyan-700  │
│ Inscripción         │ lime-100       │ lime-700  │
│ Facturación         │ amber-100      │ amber-700 │
│ Entrega             │ emerald-100    │ emerald-700│
│ Cerrado             │ green-100      │ green-700 │
│ Cancelado           │ red-100        │ red-700   │
│ Suspendido          │ rose-100       │ rose-700  │
└─────────────────────┴────────────────┴───────────┘
```

### `CasePriorityBadge`

| Prioridad | Fondo | Texto |
|-----------|-------|-------|
| Baja | gray-100 | gray-600 |
| Normal | blue-100 | blue-700 |
| Alta | orange-100 | orange-700 |
| Urgente | red-100 | red-700 |

### `TramiteSemaforoPill`

Círculo de 12×12px coloreado. Prop `showLabel` muestra etiqueta de texto al lado.

| Color | Clase | Etiqueta |
|-------|-------|----------|
| Verde | `bg-green-500` | En tiempo |
| Amarillo | `bg-yellow-500` | Por vencer |
| Rojo | `bg-red-500` | Vencido |
| Gris | `bg-gray-400` | Sin fecha |

---

## 8. API Endpoints

### Cases (Expedientes)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cases` | Listar expedientes (paginado, filtrable) |
| `GET` | `/cases/:id` | Obtener detalle de expediente |
| `POST` | `/cases` | Crear expediente |
| `PUT` | `/cases/:id` | Actualizar expediente |
| `POST` | `/cases/:id/transition` | Transicionar estado de workflow |
| `POST` | `/cases/:id/suspend` | Suspender con motivo |
| `POST` | `/cases/:id/resume` | Reanudar expediente suspendido |
| `GET` | `/cases/:id/transitions` | Obtener transiciones disponibles |
| `GET` | `/cases/:id/documents` | Obtener documentos vinculados |
| `GET` | `/cases/statistics` | Estadísticas globales |
| `GET` | `/cases/dashboard` | Datos del dashboard KPI |

### Parties (Partes)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cases/:caseId/parties` | Listar partes |
| `POST` | `/cases/:caseId/parties` | Agregar parte |
| `PUT` | `/cases/:caseId/parties/:partyId` | Actualizar parte |
| `DELETE` | `/cases/:caseId/parties/:partyId` | Eliminar parte |

### Checklist

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cases/:caseId/checklist` | Listar items del checklist |
| `POST` | `/cases/:caseId/checklist/initialize` | Inicializar desde catálogo |
| `POST` | `/cases/:caseId/checklist` | Crear item manualmente |
| `PUT` | `/cases/:caseId/checklist/:itemId` | Actualizar estado de item |
| `DELETE` | `/cases/:caseId/checklist/:itemId` | Eliminar item |

### Trámites

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cases/:caseId/tramites` | Listar trámites del expediente |
| `POST` | `/cases/:caseId/tramites` | Crear trámite |
| `PUT` | `/cases/:caseId/tramites/:tramiteId` | Actualizar trámite |
| `POST` | `/cases/:caseId/tramites/:tramiteId/complete` | Marcar como completado |
| `DELETE` | `/cases/:caseId/tramites/:tramiteId` | Eliminar trámite |
| `GET` | `/tramites/overdue` | Trámites vencidos (global) |
| `GET` | `/tramites/upcoming?days=7` | Trámites próximos a vencer |

### Timeline

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cases/:caseId/timeline?limit=50&offset=0` | Obtener eventos |
| `POST` | `/cases/:caseId/notes` | Agregar nota |

### Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/catalogos/checklist-templates?document_type=...` | Listar plantillas de checklist |
| `POST` | `/catalogos/checklist-templates` | Crear plantilla |
| `PUT` | `/catalogos/checklist-templates/:id` | Actualizar plantilla |
| `DELETE` | `/catalogos/checklist-templates/:id` | Eliminar plantilla |

**Total: 31 endpoints**

---

## 9. Arquitectura de Archivos

### Páginas

| Archivo | Función |
|---------|---------|
| `pages/CasesPage.tsx` | Listado de expedientes con filtros y paginación |
| `pages/CaseDetailPage.tsx` | Detalle con 6 pestañas y workflow |
| `pages/Dashboard.tsx` | Dashboard con KPIs y semáforo global |

### Componentes — Cases

| Archivo | Función |
|---------|---------|
| `components/cases/CaseStatusBadge.tsx` | Badge de color por estado |
| `components/cases/CasePriorityBadge.tsx` | Badge de color por prioridad |
| `components/cases/WorkflowBar.tsx` | Barra horizontal de 12 pasos |
| `components/cases/TransitionButtons.tsx` | Botones de transición de estado |
| `components/cases/CaseFilters.tsx` | Filtros de búsqueda y selección |
| `components/cases/CaseTable.tsx` | Tabla/cards responsive de expedientes |
| `components/cases/CaseCreateDialog.tsx` | Diálogo modal para crear expediente |
| `components/cases/CaseEditForm.tsx` | Formulario editable en pestaña Resumen |
| `components/cases/index.ts` | Barrel exports |

### Componentes — Parties

| Archivo | Función |
|---------|---------|
| `components/parties/PartyList.tsx` | Lista/tabla de partes con CRUD |
| `components/parties/PartyForm.tsx` | Formulario para agregar/editar parte |
| `components/parties/index.ts` | Barrel exports |

### Componentes — Checklist

| Archivo | Función |
|---------|---------|
| `components/checklist/ChecklistPanel.tsx` | Panel con agrupación por categoría |
| `components/checklist/ChecklistItemRow.tsx` | Fila individual con cambio de estado |
| `components/checklist/ChecklistProgress.tsx` | Barra de progreso de obligatorios |
| `components/checklist/index.ts` | Barrel exports |

### Componentes — Trámites

| Archivo | Función |
|---------|---------|
| `components/tramites/TramiteList.tsx` | Lista de trámites con acciones |
| `components/tramites/TramiteForm.tsx` | Formulario para crear/editar trámite |
| `components/tramites/TramiteSemaforoPill.tsx` | Indicador de semáforo |
| `components/tramites/index.ts` | Barrel exports |

### Componentes — Timeline

| Archivo | Función |
|---------|---------|
| `components/timeline/ActivityTimeline.tsx` | Timeline vertical de eventos |
| `components/timeline/NoteInput.tsx` | Input de notas con Ctrl+Enter |
| `components/timeline/index.ts` | Barrel exports |

### Componentes — Dashboard

| Archivo | Función |
|---------|---------|
| `components/dashboard/CaseDashboardCards.tsx` | Tarjetas KPI reutilizables |
| `components/dashboard/SemaforoGlobal.tsx` | Semáforo agregado |
| `components/dashboard/index.ts` | Barrel exports |

### API y Tipos

| Archivo | Función |
|---------|---------|
| `api/types/cases-types.ts` | Interfaces, tipos, constantes y mapas de colores |
| `api/endpoints/cases.ts` | Funciones fetch para los 31 endpoints |
| `hooks/useCases.ts` | Hook React para estado y operaciones CRM |

---

## 10. Estado de Validación

| Verificación | Resultado |
|--------------|-----------|
| `tsc --noEmit` | ✅ Sin errores TypeScript |
| `vite build` | ✅ Build exitoso |
| Renderizado visual | ✅ Interfaz funcional |
| Responsividad | ✅ Desktop y móvil |

---

## 11. Requisitos para Producción

El módulo frontend está completo, pero requiere los siguientes componentes backend para funcionar en producción:

### Backend API (FastAPI)

- [ ] Implementar los 31 endpoints documentados en la sección 8
- [ ] Lógica de transiciones de workflow con validaciones
- [ ] Cálculo de semáforo para trámites (basado en `fecha_limite`)
- [ ] Endpoint de dashboard con agregaciones

### Base de Datos (Supabase)

- [ ] Migración: Tabla `cases` con campos de expediente
- [ ] Migración: Tabla `case_parties` con roles y datos de contacto
- [ ] Migración: Tabla `checklist_items` con categorías y estados
- [ ] Migración: Tabla `tramites` con semáforo y fechas
- [ ] Migración: Tabla `case_timeline` para eventos y notas
- [ ] Migración: Tabla `checklist_templates` para catálogos
- [ ] Row Level Security (RLS) por `tenant_id`
- [ ] Índices en campos de búsqueda y filtrado

### Catálogos

- [ ] Plantillas de checklist por tipo de documento (compraventa, donación, testamento, etc.)
- [ ] Datos semilla para tipos de trámite comunes

---

## 12. Resumen de Tecnologías

| Tecnología | Uso |
|------------|-----|
| React 18 | Framework UI |
| TypeScript | Tipado estático |
| Vite | Bundler y dev server |
| Tailwind CSS | Estilos utilitarios |
| shadcn/ui | Componentes base (Badge, Button, Dialog, Select, Progress, etc.) |
| Lucide React | Iconografía |
| React Router | Navegación SPA |
