# Frontend CRM - Guia de Integracion

> Backend compilado y funcionando: **108 rutas**, **16 routers**, **14 estados de workflow**
> Base URL: `http://localhost:8000/api`

---

## 1. Estado Actual del Frontend

| Existe | Falta |
|--------|-------|
| Axios client con auth headers (`src/api/client.ts`) | Tipos TS para CRM (parties, checklist, tramites) |
| `src/api/endpoints/cases.ts` con CRUD basico | Llamadas a endpoints CRM nuevos |
| `useCases` hook basico | Paginas `/cases` y `/cases/:id` |
| `StatusPill` component reutilizable | StatusBadge con 14 estados en espanol |
| Patron de tabla en `History` page | Store de Zustand para casos |
| React Hook Form + Zod | Rutas en `App.tsx` |

---

## 2. Tipos TypeScript a Crear

### `src/api/types/cases-crm.ts`

```typescript
// ===========================
// STATUS & WORKFLOW
// ===========================

export const CASE_STATUSES = [
  'borrador', 'en_revision', 'checklist_pendiente', 'presupuesto',
  'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
  'inscripcion', 'facturacion', 'entrega', 'cerrado', 'cancelado', 'suspendido'
] as const;

export type CaseStatus = typeof CASE_STATUSES[number];

export const STATUS_LABELS: Record<CaseStatus, string> = {
  borrador: 'Borrador',
  en_revision: 'En Revision',
  checklist_pendiente: 'Checklist Pendiente',
  presupuesto: 'Presupuesto',
  calculo_impuestos: 'Calculo de Impuestos',
  en_firma: 'En Firma',
  postfirma: 'Post-Firma',
  tramites_gobierno: 'Tramites de Gobierno',
  inscripcion: 'Inscripcion',
  facturacion: 'Facturacion',
  entrega: 'Entrega',
  cerrado: 'Cerrado',
  cancelado: 'Cancelado',
  suspendido: 'Suspendido',
};

// Colores sugeridos para badges (tailwind)
export const STATUS_COLORS: Record<CaseStatus, string> = {
  borrador: 'bg-gray-100 text-gray-700',
  en_revision: 'bg-blue-100 text-blue-700',
  checklist_pendiente: 'bg-yellow-100 text-yellow-700',
  presupuesto: 'bg-purple-100 text-purple-700',
  calculo_impuestos: 'bg-orange-100 text-orange-700',
  en_firma: 'bg-indigo-100 text-indigo-700',
  postfirma: 'bg-teal-100 text-teal-700',
  tramites_gobierno: 'bg-cyan-100 text-cyan-700',
  inscripcion: 'bg-lime-100 text-lime-700',
  facturacion: 'bg-amber-100 text-amber-700',
  entrega: 'bg-emerald-100 text-emerald-700',
  cerrado: 'bg-green-100 text-green-700',
  cancelado: 'bg-red-100 text-red-700',
  suspendido: 'bg-rose-100 text-rose-700',
};

export type CasePriority = 'baja' | 'normal' | 'alta' | 'urgente';
export type DocumentType = 'compraventa' | 'donacion' | 'testamento' | 'poder' | 'sociedad' | 'cancelacion';
export type ChecklistStatus = 'pendiente' | 'solicitado' | 'recibido' | 'aprobado' | 'rechazado' | 'no_aplica';
export type ChecklistCategoria = 'parte_a' | 'parte_b' | 'inmueble' | 'fiscal' | 'gobierno' | 'general';
export type TramiteSemaforo = 'verde' | 'amarillo' | 'rojo' | 'gris';

// ===========================
// CASE
// ===========================

export interface Case {
  id: string;
  tenant_id: string;
  client_id: string;
  case_number: string;
  document_type: DocumentType;
  status: CaseStatus;
  parties: Record<string, any>[];
  description?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  assigned_to?: string;
  priority?: CasePriority;
  escritura_number?: string;
  volumen?: string;
  folio_real?: string;
  valor_operacion?: number;
  fecha_firma?: string;
  fecha_cierre?: string;
  notas?: string;
  tags?: string[];
}

export interface CaseWithClient extends Case {
  client?: Record<string, any>;
}

export interface CaseDetail extends CaseWithClient {
  case_parties: CaseParty[];
  checklist_summary?: ChecklistSummary;
  tramites_summary?: SemaforoSummary;
  available_transitions: Transition[];
}

export interface CaseListResponse {
  cases: Case[];
  total: number;
  page: number;
  page_size: number;
}

// ===========================
// PARTIES (tabla normalizada)
// ===========================

export interface CaseParty {
  id: string;
  tenant_id: string;
  case_id: string;
  client_id?: string;
  role: string;
  nombre: string;
  rfc?: string;
  tipo_persona?: 'fisica' | 'moral';
  email?: string;
  telefono?: string;
  representante_legal?: string;
  poder_notarial?: string;
  orden: number;
  created_at: string;
  updated_at: string;
}

// ===========================
// CHECKLIST
// ===========================

export interface ChecklistItem {
  id: string;
  tenant_id: string;
  case_id: string;
  nombre: string;
  categoria: ChecklistCategoria;
  status: ChecklistStatus;
  obligatorio: boolean;
  uploaded_file_id?: string;
  storage_path?: string;
  fecha_solicitud?: string;
  fecha_recepcion?: string;
  fecha_vencimiento?: string;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface ChecklistSummary {
  total: number;
  by_status: Record<ChecklistStatus, number>;
  obligatorios: number;
  obligatorios_completados: number;
  completion_pct: number;
  all_required_complete: boolean;
}

// ===========================
// TRAMITES
// ===========================

export interface Tramite {
  id: string;
  tenant_id: string;
  case_id: string;
  assigned_to?: string;
  tipo: string;
  nombre: string;
  status: string;
  fecha_inicio?: string;
  fecha_limite?: string;
  fecha_completado?: string;
  resultado?: string;
  costo?: number;
  depende_de?: string;
  notas?: string;
  semaforo?: TramiteSemaforo;
  created_at: string;
  updated_at: string;
}

export interface SemaforoSummary {
  verde: number;
  amarillo: number;
  rojo: number;
  gris: number;
  total: number;
}

// ===========================
// WORKFLOW & ACTIVITY
// ===========================

export interface Transition {
  status: CaseStatus;
  label: string;
}

export interface TransitionResponse {
  current_status: CaseStatus;
  current_label: string;
  transitions: Transition[];
}

export interface CaseTimeline {
  case_id: string;
  events: Record<string, any>[];
  total: number;
  limit: number;
  offset: number;
}

// ===========================
// DASHBOARD
// ===========================

export interface CaseDashboard {
  total_cases: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  semaforo_global: SemaforoSummary;
  overdue_tramites: number;
  upcoming_tramites: number;
}

export interface CaseStatistics {
  total_cases: number;
  by_status: Record<string, number>;
  by_document_type: Record<string, number>;
}

// ===========================
// CATALOGO
// ===========================

export interface CatalogoChecklist {
  id: string;
  tenant_id?: string;
  document_type: string;
  nombre: string;
  categoria: ChecklistCategoria;
  obligatorio: boolean;
  orden: number;
  created_at: string;
  updated_at: string;
}
```

---

## 3. API Endpoints - Referencia Completa

### 3.1 Cases (`/api/cases`)

| Metodo | Ruta | Body / Query | Response | Uso |
|--------|------|-------------|----------|-----|
| `POST` | `/cases` | `CaseCreateRequest` | `CaseWithClient` | Crear expediente |
| `GET` | `/cases` | `?status=&document_type=&priority=&assigned_to=&search=&page=1&page_size=50` | `CaseListResponse` | Lista paginada con filtros |
| `GET` | `/cases/statistics` | - | `CaseStatistics` | Stats para graficas |
| `GET` | `/cases/dashboard` | - | `CaseDashboard` | Dashboard completo |
| `GET` | `/cases/:id` | - | `CaseDetail` | Detalle con parties + checklist + tramites + transiciones |
| `PUT` | `/cases/:id` | `CaseUpdateRequest` (partial) | `Case` | Editar campos |
| `PUT` | `/cases/:id/status` | `{ status }` | `Case` | Cambio directo (sin validacion) |
| `POST` | `/cases/:id/transition` | `{ status, notes? }` | `Case` | **Transicion validada (usar este)** |
| `POST` | `/cases/:id/suspend` | `{ reason }` | `Case` | Suspender caso |
| `POST` | `/cases/:id/resume` | - (sin body) | `Case` | Reanudar caso suspendido |
| `GET` | `/cases/:id/transitions` | - | `TransitionResponse` | Botones disponibles |
| `GET` | `/cases/:id/documents` | - | `{ documents, total }` | Documentos generados |

### 3.2 Parties (`/api/cases/:id/parties`)

| Metodo | Ruta | Body | Response |
|--------|------|------|----------|
| `GET` | `/cases/:id/parties` | - | `CaseParty[]` |
| `POST` | `/cases/:id/parties` | `{ role, nombre, client_id?, rfc?, tipo_persona?, email?, telefono?, representante_legal?, poder_notarial?, orden? }` | `CaseParty` |
| `PUT` | `/cases/:id/parties/:partyId` | Campos parciales | `CaseParty` |
| `DELETE` | `/cases/:id/parties/:partyId` | - | 204 |

### 3.3 Checklist (`/api/cases/:id/checklist`)

| Metodo | Ruta | Body | Response |
|--------|------|------|----------|
| `GET` | `/cases/:id/checklist` | - | `ChecklistItem[]` |
| `POST` | `/cases/:id/checklist` | `{ nombre, categoria, obligatorio?, notas? }` | `ChecklistItem` |
| `POST` | `/cases/:id/checklist/initialize` | `{ document_type? }` | `ChecklistItem[]` (crea desde catalogo) |
| `PUT` | `/cases/:id/checklist/:itemId` | `{ status, notas? }` | `ChecklistItem` |
| `DELETE` | `/cases/:id/checklist/:itemId` | - | 204 |

**Status validos del checklist:** `pendiente` | `solicitado` | `recibido` | `aprobado` | `rechazado` | `no_aplica`

### 3.4 Tramites (`/api/cases/:id/tramites`)

| Metodo | Ruta | Body | Response |
|--------|------|------|----------|
| `GET` | `/cases/:id/tramites` | - | `Tramite[]` (con semaforo calculado) |
| `POST` | `/cases/:id/tramites` | `{ tipo, nombre, assigned_to?, fecha_limite?, costo?, depende_de?, notas? }` | `Tramite` |
| `PUT` | `/cases/:id/tramites/:tramiteId` | Campos parciales | `Tramite` |
| `POST` | `/cases/:id/tramites/:tramiteId/complete` | `{ resultado?, costo? }` | `Tramite` |
| `DELETE` | `/cases/:id/tramites/:tramiteId` | - | 204 |
| `GET` | `/tramites/overdue` | - | `Tramite[]` (vencidos de toda la notaria) |
| `GET` | `/tramites/upcoming?days=7` | - | `Tramite[]` (proximos a vencer) |

**Semaforo:** `verde` (>5 dias) | `amarillo` (1-5 dias) | `rojo` (<1 dia) | `gris` (completado/sin fecha)

### 3.5 Timeline / Notas (`/api/cases/:id/...`)

| Metodo | Ruta | Body / Query | Response |
|--------|------|-------------|----------|
| `GET` | `/cases/:id/timeline?limit=50&offset=0` | - | `CaseTimeline` |
| `POST` | `/cases/:id/notes` | `{ note }` | `{ message, id }` |

### 3.6 Catalogos (`/api/catalogos`)

| Metodo | Ruta | Body / Query | Response |
|--------|------|-------------|----------|
| `GET` | `/catalogos/checklist-templates?document_type=` | - | `CatalogoChecklist[]` |
| `POST` | `/catalogos/checklist-templates` | `{ document_type, nombre, categoria, obligatorio?, orden? }` | `CatalogoChecklist` |
| `PUT` | `/catalogos/checklist-templates/:id` | Campos parciales | `CatalogoChecklist` |
| `DELETE` | `/catalogos/checklist-templates/:id` | - | 204 (403 si es template del sistema) |

---

## 4. Workflow State Machine

```
borrador ──────────────> en_revision ──────> checklist_pendiente
   │                        │    │                │
   │                        │    └── presupuesto <─┘
   │                        │           │
   │                        │    calculo_impuestos
   │                        │           │
   │                        │        en_firma
   │                        │           │
   │                        │        postfirma
   │                        │           │
   │                        │    tramites_gobierno
   │                        │           │
   │                        │      inscripcion
   │                        │           │
   │                        │      facturacion
   │                        │           │
   │                        │        entrega
   │                        │           │
   │                        │        cerrado  ← TERMINAL
   │                        │
   └── cancelado ←──────── (desde cualquier estado activo)
                            │
       suspendido ←──────── (desde cualquier estado activo)
            │
            └── resume() → restaura estado anterior
```

### Transiciones permitidas por estado

| Desde | Puede ir a |
|-------|-----------|
| `borrador` | `en_revision`, `cancelado` |
| `en_revision` | `checklist_pendiente`, `presupuesto`, `cancelado`, `suspendido` |
| `checklist_pendiente` | `en_revision`, `presupuesto`, `cancelado`, `suspendido` |
| `presupuesto` | `calculo_impuestos`, `cancelado`, `suspendido` |
| `calculo_impuestos` | `en_firma`, `cancelado`, `suspendido` |
| `en_firma` | `postfirma`, `cancelado`, `suspendido` |
| `postfirma` | `tramites_gobierno`, `cancelado`, `suspendido` |
| `tramites_gobierno` | `inscripcion`, `cancelado`, `suspendido` |
| `inscripcion` | `facturacion`, `cancelado`, `suspendido` |
| `facturacion` | `entrega`, `cancelado`, `suspendido` |
| `entrega` | `cerrado`, `cancelado`, `suspendido` |
| `suspendido` | Solo via `POST /resume` |
| `cancelado` | Terminal (ninguna) |
| `cerrado` | Terminal (ninguna) |

---

## 5. Funciones API Sugeridas

### `src/api/endpoints/cases-crm.ts`

```typescript
import { api } from '../client';
import type {
  Case, CaseWithClient, CaseDetail, CaseListResponse,
  CaseStatistics, CaseDashboard, TransitionResponse,
  CaseParty, ChecklistItem, Tramite, CaseTimeline,
  CatalogoChecklist,
} from '../types/cases-crm';

// === CASES ===

export const casesApi = {
  list: (params?: {
    status?: string;
    document_type?: string;
    priority?: string;
    assigned_to?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get<CaseListResponse>('/cases', { params }),

  get: (id: string) =>
    api.get<CaseDetail>(`/cases/${id}`),

  create: (data: {
    client_id: string;
    case_number: string;
    document_type: string;
    description?: string;
    priority?: string;
    assigned_to?: string;
    valor_operacion?: number;
    fecha_firma?: string;
    notas?: string;
    tags?: string[];
  }) => api.post<CaseWithClient>('/cases', data),

  update: (id: string, data: Record<string, any>) =>
    api.put<Case>(`/cases/${id}`, data),

  transition: (id: string, status: string, notes?: string) =>
    api.post<Case>(`/cases/${id}/transition`, { status, notes }),

  suspend: (id: string, reason: string) =>
    api.post<Case>(`/cases/${id}/suspend`, { reason }),

  resume: (id: string) =>
    api.post<Case>(`/cases/${id}/resume`),

  getTransitions: (id: string) =>
    api.get<TransitionResponse>(`/cases/${id}/transitions`),

  getDocuments: (id: string) =>
    api.get(`/cases/${id}/documents`),

  getStatistics: () =>
    api.get<CaseStatistics>('/cases/statistics'),

  getDashboard: () =>
    api.get<CaseDashboard>('/cases/dashboard'),
};

// === PARTIES ===

export const partiesApi = {
  list: (caseId: string) =>
    api.get<CaseParty[]>(`/cases/${caseId}/parties`),

  create: (caseId: string, data: {
    role: string;
    nombre: string;
    client_id?: string;
    rfc?: string;
    tipo_persona?: string;
    email?: string;
    telefono?: string;
    representante_legal?: string;
    poder_notarial?: string;
    orden?: number;
  }) => api.post<CaseParty>(`/cases/${caseId}/parties`, data),

  update: (caseId: string, partyId: string, data: Record<string, any>) =>
    api.put<CaseParty>(`/cases/${caseId}/parties/${partyId}`, data),

  remove: (caseId: string, partyId: string) =>
    api.delete(`/cases/${caseId}/parties/${partyId}`),
};

// === CHECKLIST ===

export const checklistApi = {
  list: (caseId: string) =>
    api.get<ChecklistItem[]>(`/cases/${caseId}/checklist`),

  initialize: (caseId: string, documentType?: string) =>
    api.post<ChecklistItem[]>(`/cases/${caseId}/checklist/initialize`, {
      document_type: documentType,
    }),

  create: (caseId: string, data: {
    nombre: string;
    categoria: string;
    obligatorio?: boolean;
    notas?: string;
  }) => api.post<ChecklistItem>(`/cases/${caseId}/checklist`, data),

  updateStatus: (caseId: string, itemId: string, status: string, notas?: string) =>
    api.put<ChecklistItem>(`/cases/${caseId}/checklist/${itemId}`, { status, notas }),

  remove: (caseId: string, itemId: string) =>
    api.delete(`/cases/${caseId}/checklist/${itemId}`),
};

// === TRAMITES ===

export const tramitesApi = {
  list: (caseId: string) =>
    api.get<Tramite[]>(`/cases/${caseId}/tramites`),

  create: (caseId: string, data: {
    tipo: string;
    nombre: string;
    assigned_to?: string;
    fecha_limite?: string;
    costo?: number;
    depende_de?: string;
    notas?: string;
  }) => api.post<Tramite>(`/cases/${caseId}/tramites`, data),

  update: (caseId: string, tramiteId: string, data: Record<string, any>) =>
    api.put<Tramite>(`/cases/${caseId}/tramites/${tramiteId}`, data),

  complete: (caseId: string, tramiteId: string, resultado?: string, costo?: number) =>
    api.post<Tramite>(`/cases/${caseId}/tramites/${tramiteId}/complete`, { resultado, costo }),

  remove: (caseId: string, tramiteId: string) =>
    api.delete(`/cases/${caseId}/tramites/${tramiteId}`),

  getOverdue: () =>
    api.get<Tramite[]>('/tramites/overdue'),

  getUpcoming: (days = 7) =>
    api.get<Tramite[]>('/tramites/upcoming', { params: { days } }),
};

// === TIMELINE ===

export const timelineApi = {
  get: (caseId: string, limit = 50, offset = 0) =>
    api.get<CaseTimeline>(`/cases/${caseId}/timeline`, { params: { limit, offset } }),

  addNote: (caseId: string, note: string) =>
    api.post(`/cases/${caseId}/notes`, { note }),
};

// === CATALOGOS ===

export const catalogosApi = {
  listTemplates: (documentType?: string) =>
    api.get<CatalogoChecklist[]>('/catalogos/checklist-templates', {
      params: documentType ? { document_type: documentType } : {},
    }),

  createTemplate: (data: {
    document_type: string;
    nombre: string;
    categoria: string;
    obligatorio?: boolean;
    orden?: number;
  }) => api.post<CatalogoChecklist>('/catalogos/checklist-templates', data),

  updateTemplate: (id: string, data: Record<string, any>) =>
    api.put<CatalogoChecklist>(`/catalogos/checklist-templates/${id}`, data),

  deleteTemplate: (id: string) =>
    api.delete(`/catalogos/checklist-templates/${id}`),
};
```

---

## 6. Paginas y Componentes a Crear

### 6.1 Rutas nuevas en `App.tsx`

```tsx
<Route path="/cases" element={<CasesPage />} />
<Route path="/cases/:caseId" element={<CaseDetailPage />} />
```

### 6.2 Estructura de archivos sugerida

```
src/
  pages/
    CasesPage.tsx              ← Lista de expedientes con filtros
    CaseDetailPage.tsx         ← Detalle con tabs
  components/
    cases/
      CaseStatusBadge.tsx      ← Badge con color por estado
      CasePriorityBadge.tsx    ← Badge baja/normal/alta/urgente
      CaseFilters.tsx          ← Filtros: status, tipo, prioridad, busqueda
      CaseTable.tsx            ← Tabla paginada de expedientes
      CaseCreateDialog.tsx     ← Dialog/modal para crear caso
      CaseEditForm.tsx         ← Form de edicion de campos
      WorkflowBar.tsx          ← Barra de progreso del workflow (paso actual)
      TransitionButtons.tsx    ← Botones de transicion disponibles
    parties/
      PartyList.tsx            ← Lista de partes del caso
      PartyForm.tsx            ← Form agregar/editar parte
    checklist/
      ChecklistPanel.tsx       ← Panel con items agrupados por categoria
      ChecklistProgress.tsx    ← Barra de progreso % completado
      ChecklistItemRow.tsx     ← Fila con toggle de status
    tramites/
      TramiteList.tsx          ← Lista con semaforo
      TramiteSemaforoPill.tsx  ← Pill verde/amarillo/rojo/gris
      TramiteForm.tsx          ← Form crear/editar tramite
    timeline/
      ActivityTimeline.tsx     ← Timeline vertical de eventos
      NoteInput.tsx            ← Input para agregar notas
    dashboard/
      CaseDashboardCards.tsx   ← Cards con stats
      SemaforoGlobal.tsx       ← Indicador semaforo global
  api/
    types/
      cases-crm.ts             ← Tipos TS (seccion 2 de este doc)
    endpoints/
      cases-crm.ts             ← Funciones API (seccion 5 de este doc)
```

### 6.3 `CasesPage` - Descripcion funcional

- **Header**: Titulo "Expedientes" + boton "Nuevo Expediente"
- **Filtros**: Status (multiselect), Tipo documento (select), Prioridad (select), Busqueda texto
- **Tabla**: case_number, tipo, status (badge color), prioridad, cliente, fecha, asignado
- **Paginacion**: Usa `page` y `page_size` del response
- **Click en fila**: Navega a `/cases/:caseId`

### 6.4 `CaseDetailPage` - Descripcion funcional

**Layout**: Header con info del caso + Tabs

**Header**:
- Case number + status badge + priority badge
- `WorkflowBar`: Barra horizontal mostrando los pasos del workflow, resaltando el actual
- `TransitionButtons`: Botones para cada transicion disponible (usa `available_transitions` del `CaseDetail`)
- Boton suspender/reanudar segun estado

**Tabs**:

| Tab | Contenido | Endpoint |
|-----|-----------|----------|
| **Resumen** | Info del caso, cliente, valor operacion, fecha firma, escritura, notas | `GET /cases/:id` |
| **Partes** | CRUD tabla de partes (role, nombre, RFC, tipo persona) | `/cases/:id/parties` |
| **Checklist** | Items agrupados por categoria, progress bar, boton "Inicializar desde catalogo" | `/cases/:id/checklist` |
| **Tramites** | Lista con semaforo, crear tramite, marcar completado | `/cases/:id/tramites` |
| **Documentos** | Documentos generados del caso | `/cases/:id/documents` |
| **Timeline** | Actividad cronologica + input para notas | `/cases/:id/timeline` + `/cases/:id/notes` |

---

## 7. Componentes Clave - Especificaciones

### `CaseStatusBadge`

```tsx
// Recibe status, renderiza badge con color y label
<CaseStatusBadge status="en_revision" />
// → <span class="bg-blue-100 text-blue-700 ...">En Revision</span>
```

### `WorkflowBar`

Barra horizontal con los 11 pasos activos del workflow (sin cancelado/suspendido). Marca el paso actual y los completados. Ejemplo visual:

```
[Borrador] → [En Revision] → [Checklist] → [Presupuesto] → ... → [Cerrado]
   ✓              ✓             ●
```

Pasos en orden: `borrador` → `en_revision` → `checklist_pendiente` → `presupuesto` → `calculo_impuestos` → `en_firma` → `postfirma` → `tramites_gobierno` → `inscripcion` → `facturacion` → `entrega` → `cerrado`

### `TransitionButtons`

```tsx
// Usa available_transitions del CaseDetail
// Cada boton llama POST /cases/:id/transition
// Cancelar y Suspender tienen confirmacion con razon
<TransitionButtons
  transitions={caseDetail.available_transitions}
  onTransition={(status, notes) => casesApi.transition(caseId, status, notes)}
/>
```

### `TramiteSemaforoPill`

```tsx
// verde = > 5 dias, amarillo = 1-5 dias, rojo = < 1 dia, gris = completado/sin fecha
<SemaforoPill semaforo="rojo" />  // → circulo rojo
```

### `ChecklistProgress`

```tsx
// Usa checklist_summary del CaseDetail
<ChecklistProgress
  total={summary.obligatorios}
  completed={summary.obligatorios_completados}
  pct={summary.completion_pct}
/>
// → Barra de progreso "8/12 obligatorios (67%)"
```

---

## 8. Flujo de Uso Principal

```
1. Usuario abre /cases
   → GET /api/cases?page=1&page_size=50
   → Tabla con expedientes

2. Click "Nuevo Expediente"
   → Dialog con form (case_number, document_type, client_id, priority, etc.)
   → POST /api/cases
   → Redirige a /cases/:id

3. En /cases/:id se carga el detalle
   → GET /api/cases/:id (retorna CaseDetail con todo incluido)

4. Tab Checklist → Click "Inicializar Checklist"
   → POST /api/cases/:id/checklist/initialize
   → Se crean ~8-10 items desde catalogo segun document_type

5. Tab Partes → Agregar vendedor, comprador, etc.
   → POST /api/cases/:id/parties (una por cada parte)

6. Click boton "En Revision" (transicion)
   → POST /api/cases/:id/transition { status: "en_revision" }
   → Se actualiza status y badge

7. Cuando todo el checklist esta completo
   → Transicionar a presupuesto → calculo_impuestos → en_firma → ...

8. Tab Tramites → Crear tramite "Pago ISR"
   → POST /api/cases/:id/tramites { tipo: "pago_impuestos", nombre: "Pago ISR", fecha_limite: "..." }
   → Se muestra con semaforo segun fecha

9. Completar tramite
   → POST /api/cases/:id/tramites/:tramiteId/complete { resultado: "Folio 12345" }

10. Llegar a "Entrega" → Click "Cerrado"
    → POST /api/cases/:id/transition { status: "cerrado" }
    → Caso terminado
```

---

## 9. Dashboard CRM

Endpoint: `GET /api/cases/dashboard`

Contenido sugerido para cards/widgets:

| Widget | Dato | Visual |
|--------|------|--------|
| Total expedientes | `total_cases` | Numero grande |
| Por estado | `by_status` | Barras horizontales o donut chart |
| Por prioridad | `by_priority` | Pills con conteo |
| Semaforo global | `semaforo_global` | 4 circulos (verde/amarillo/rojo/gris) con counts |
| Tramites vencidos | `overdue_tramites` | Numero en rojo si > 0 |
| Proximos a vencer | `upcoming_tramites` | Numero en amarillo si > 0 |

---

## 10. Catalogo de Checklist Templates (53 items seed)

El backend ya tiene 53 templates insertados para 6 tipos de documento. Al hacer `POST /cases/:id/checklist/initialize`, se copian los templates correspondientes al `document_type` del caso.

**Categorias disponibles**: `parte_a`, `parte_b`, `inmueble`, `fiscal`, `gobierno`, `general`

Para administrar templates custom del tenant: usar endpoints `/api/catalogos/checklist-templates`.

---

## 11. Notas de Integracion

1. **Auth header**: Todos los endpoints usan `tenant_id` del header de auth. El Axios client existente ya lo maneja.

2. **Usar `/transition` en vez de `/status`**: El endpoint `PUT /cases/:id/status` es legacy y no valida la state machine. Siempre usar `POST /cases/:id/transition`.

3. **El `GET /cases/:id` retorna todo**: No es necesario hacer llamadas separadas para parties, checklist summary, tramites summary y transiciones. Todo viene en `CaseDetail`.

4. **Para listas completas de checklist/tramites**: Si necesitas la lista completa (no solo el summary), usa los endpoints dedicados `/cases/:id/checklist` y `/cases/:id/tramites`.

5. **Semaforo se calcula server-side**: El backend ya calcula el semaforo de cada tramite. El frontend solo necesita mostrar el color.

6. **Timeline se llena automaticamente**: Cada transicion, cambio de checklist, y creacion de tramite genera entradas en el activity log. Solo las notas manuales requieren `POST /notes`.
