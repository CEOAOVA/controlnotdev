# 🎨 ControlNot v2 - Plan de Implementación Frontend

**Fecha**: 2025-01-23
**Versión**: 2.0.0
**Stack**: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Requerimientos](#análisis-de-requerimientos)
3. [Arquitectura UX](#arquitectura-ux)
4. [Sistema de Diseño Visual](#sistema-de-diseño-visual)
5. [Patrones Preservados de Legacy](#patrones-preservados-de-legacy)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Roadmap de Implementación](#roadmap-de-implementación)
8. [Próximos Pasos](#próximos-pasos)

---

## 1. Resumen Ejecutivo

### Estado del Backend

✅ **Backend**: 85% completo - Listo para frontend
✅ **Base de Datos**: 100% completa - 11 tablas con RLS
✅ **Autenticación**: Infraestructura lista (Supabase Auth)
✅ **APIs**: 8 routers con 30+ endpoints

### Decisión de Inicio

**APROBADO**: Comenzar frontend YA con mocks iniciales
**Stack Elegido**: React 18 + TypeScript + Vite + TailwindCSS
**Enfoque**: Profesional y competente - cumplir 100% capacidades backend

### Proceso de Diseño Completado

✅ **Fase 1**: Análisis profundo de requerimientos (project-deep-analyzer)
✅ **Fase 2**: Diseño UX exhaustivo (ux-researcher)
✅ **Fase 3**: Identidad visual y componentes (ui-designer)
✅ **Fase 4**: Análisis de patrones legacy (explore agent)

---

## 2. Análisis de Requerimientos

### 2.1 Capacidades del Backend

#### **8 Módulos API Principales**

1. **Templates API** (`/api/templates`)
   - Upload, list, confirm, delete
   - Auto-detección de placeholders
   - Auto-detección de tipo de documento
   - Soporte Google Drive + Upload directo

2. **Documents API** (`/api/documents`)
   - Upload categorizado con validación
   - Generación .docx con placeholders
   - Download de documentos generados
   - Email con attachments

3. **Extraction API** (`/api/extraction`)
   - OCR paralelo asíncrono (5-10x más rápido)
   - AI extraction (OpenRouter: GPT-4o, Claude, Gemini, Llama)
   - Edit y confirmación de datos
   - SHA-256 cache de resultados

4. **Cases API** (`/api/cases`)
   - CRUD completo de expedientes
   - 9 estados de workflow
   - Estadísticas y reportes
   - Búsqueda y filtrado

5. **Clients API** (`/api/clients`)
   - CRUD de clientes (física/moral)
   - Validación RFC único
   - Multi-tenant isolation

6. **Cancelaciones API** (`/api/cancelaciones`)
   - Workflow específico de cancelación de hipoteca
   - 55 campos especializados
   - Validación de documentos requeridos

7. **Health API** (`/api/health`)
   - Status check del sistema
   - Versión de la API

8. **Models API** (`/api/models`)
   - Listado de modelos AI disponibles
   - Configuración de OpenRouter

#### **6 Tipos de Documentos Soportados**

1. **Compraventa**: 47 campos
2. **Donación**: ~49 campos
3. **Testamento**: Variable
4. **Poder**: Variable
5. **Sociedad**: Variable
6. **Cancelación de Hipoteca**: 55 campos

#### **Flujo de Generación de Documentos (7 pasos)**

```
1. Upload Template → 2. Upload Documents → 3. Categorize Files
     ↓
4. OCR Processing (Google Vision) → 5. AI Extraction (OpenRouter)
     ↓
6. User Review & Edit → 7. Generate Final .docx
```

### 2.2 Requerimientos del Usuario

#### **4 Secciones Principales Obligatorias**

1. **Generación de Documentos** (Producto principal)
   - Subida de archivos con categorización
   - OCR + AI extraction
   - **Mostrar campos encontrados vs vacíos**
   - **Validación obligatoria: llenar TODOS los campos**
   - **Preview OBLIGATORIO antes de generar**
   - Opciones: Email O Download

2. **Gestión de Plantillas**
   - Upload de plantillas .docx
   - Editar metadata
   - Eliminar plantillas
   - Renombrar plantillas
   - Vista previa de placeholders

3. **Historial**
   - Consulta de documentos generados
   - Filtros: Fecha, tipo, cliente
   - Re-descarga de documentos
   - Exportar reportes

4. **Configuración**
   - Perfil de usuario
   - Datos de la notaría
   - Preferencias de estilo
   - Cambio de contraseña

---

## 3. Arquitectura UX

### 3.1 Navegación

#### **Layout Principal**

```
┌─────────────────────────────────────────────────────────┐
│  Topbar: Logo | Breadcrumbs | Notificaciones | Avatar  │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │           Main Content Area                  │
│          │                                              │
│ - Inicio │                                              │
│ - Generar│                                              │
│ - Plant. │                                              │
│ - Histor.│                                              │
│ - Config │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

**Sidebar (240px)**
- Navegación principal colapsable
- Iconos + labels
- Estado activo destacado
- Footer con status de servicios

**Topbar (64px)**
- Logo de la notaría (izquierda)
- Breadcrumbs dinámicos (centro)
- Notificaciones badge (derecha)
- Avatar con dropdown (derecha)

### 3.2 Flujo de Generación de Documentos (6 Pasos)

#### **Paso 1: Seleccionar Plantilla**

```
┌─────────────────────────────────────────────────────┐
│  📋 Seleccionar Plantilla                           │
├─────────────────────────────────────────────────────┤
│  Tabs: [📁 Mis Plantillas] [☁️ Google Drive] [⬆️ Subir]│
│                                                     │
│  Grid (3 columnas):                                 │
│  ┌──────┐  ┌──────┐  ┌──────┐                      │
│  │ 📄   │  │ 📄   │  │ 📄   │                      │
│  │Compra│  │Donac.│  │Poder │                      │
│  │15 📌 │  │12 📌 │  │8 📌  │                      │
│  │[Usar]│  │[Usar]│  │[Usar]│                      │
│  └──────┘  └──────┘  └──────┘                      │
│                                                     │
│  [Siguiente →]                                      │
└─────────────────────────────────────────────────────┘
```

**Características**:
- Card con thumbnail + metadata
- Badge con count de placeholders
- Botón "Usar" por plantilla
- Búsqueda y filtros (tipo, fecha)

#### **Paso 2: Subir Documentos**

```
┌─────────────────────────────────────────────────────┐
│  📤 Subir Documentos                                │
├─────────────────────────────────────────────────────┤
│  Categorías (Tabs según tipo de documento):        │
│  [Parte A: Vendedor] [Parte B: Comprador] [Otros] │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  📁 Arrastra archivos aquí                 │    │
│  │  o haz clic para seleccionar              │    │
│  │                                            │    │
│  │  Formatos: PDF, JPG, PNG                  │    │
│  │  Máximo: 50MB por archivo                 │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  Archivos subidos (3):                             │
│  ✓ INE_vendedor.pdf (2.3 MB)           [×]         │
│  ✓ Escritura_anterior.pdf (4.1 MB)     [×]         │
│  ✓ Constancia_fiscal.pdf (1.8 MB)      [×]         │
│                                                     │
│  [← Anterior]  [Siguiente →]                       │
└─────────────────────────────────────────────────────┘
```

**Características CRÍTICAS** (del análisis legacy):
- **Categorización por roles**: Parte A / Parte B / Otros
- **Roles dinámicos** según tipo de documento:
  - Compraventa: Vendedor/Comprador
  - Poder: Poderdante/Apoderado
  - Sociedad: Socios/Administradores
- **Lista de documentos requeridos** por categoría (expandible)
- **Validación** de formatos y tamaños
- **Preview** de archivos subidos

#### **Paso 3: Extracción de Datos**

```
┌─────────────────────────────────────────────────────┐
│  🔍 Extrayendo Datos                                │
├─────────────────────────────────────────────────────┤
│  Progreso: Paso 2 de 3                              │
│  ████████████░░░░░░░░░░  60%                        │
│                                                     │
│  ✓ Procesando OCR (Google Vision)                  │
│  ⏳ Analizando con IA (GPT-4o)...                   │
│  ⏸ Finalizando extracción                          │
│                                                     │
│  Documentos procesados: 3/5                         │
│  Tiempo estimado: 15 segundos                       │
│                                                     │
│  [Cancelar]                                         │
└─────────────────────────────────────────────────────┘
```

**Características**:
- Progress bar visual
- Steps indicador (3 pasos: OCR → AI → Finalizar)
- Estado por documento
- Cancelación permitida
- Spinner animado

#### **Paso 4: Revisar y Completar Campos** ⚠️ **CRÍTICO**

```
┌─────────────────────────────────────────────────────┐
│  ✏️ Revisar y Completar Datos                       │
├─────────────────────────────────────────────────────┤
│  📊 Estadísticas                                    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
│  │   47   │ │   32   │ │   15   │ │  68%   │      │
│  │ Total  │ │Encontr.│ │ Vacíos │ │  Tasa  │      │
│  └────────┘ └────────┘ └────────┘ └────────┘      │
│                                                     │
│  Tabs: [Personas] [Inmueble] [Documentos] [Otros] │
│                                                     │
│  Personas (15 campos):                              │
│  ┌─────────────────────────────────────────────┐   │
│  │ Nombre Vendedor ✓                           │   │
│  │ [Juan Pérez García                        ] │   │
│  │                                             │   │
│  │ RFC Vendedor ⚠️ (No encontrado)             │   │
│  │ [                                         ] │   │
│  │                                             │   │
│  │ Edad Vendedor ✓                             │   │
│  │ [45 años                                  ] │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ⚠️ Faltan 15 campos por completar                  │
│                                                     │
│  [← Anterior]  [Re-extraer]  [Confirmar →]         │
└─────────────────────────────────────────────────────┘
```

**Características OBLIGATORIAS**:
- ✅ **Métricas en tiempo real**: Total, Encontrados, Vacíos, Tasa
- ✅ **Indicadores visuales**:
  - ✓ Verde: Campo encontrado
  - ⚠️ Amarillo: Campo vacío (requiere atención)
- ✅ **Categorización dinámica**: Tabs según tipo de documento
- ✅ **Validación estricta**: NO permitir "Confirmar" si hay campos vacíos
- ✅ **Botón "Re-extraer"**: Volver a procesar si datos incorrectos
- ✅ **Form único**: Todos los campos en un solo formulario (no recarga parcial)

**Categorías por Tipo**:
- **Compraventa**: Información General, Partes Involucradas, Inmueble, Antecedentes
- **Donación**: Similar a compraventa
- **Poder**: Poderdante, Apoderado, Facultades, Limitaciones
- **Testamento**: Testador, Herederos, Legados, Disposiciones
- **Sociedad**: Socios, Capital Social, Administración, Objeto Social
- **Cancelación**: Deudor, Intermediario, Inmueble, Documentos Hipotecarios

#### **Paso 5: Vista Previa** ⚠️ **OBLIGATORIO**

```
┌─────────────────────────────────────────────────────┐
│  👁️ Vista Previa del Documento                      │
├─────────────────────────────────────────────────────┤
│  Nombre: compraventa_juan_perez.docx                │
│  Tipo: Compraventa                                  │
│  Fecha: 23 enero 2025                               │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  [Preview del documento .docx renderizado] │    │
│  │                                            │    │
│  │  ESCRITURA PÚBLICA NÚMERO...               │    │
│  │                                            │    │
│  │  En la ciudad de Morelia, Michoacán...    │    │
│  │                                            │    │
│  │  Ante mí, Licenciada Patricia Servin...   │    │
│  │                                            │    │
│  │  Comparecen:                               │    │
│  │  I. Juan Pérez García...                   │    │
│  │  II. María López Ramírez...                │    │
│  │                                            │    │
│  │  [Scroll para ver más...]                 │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  [Descargar Preview PDF]                            │
│                                                     │
│  [← Editar]  [✓ Aprobar y Generar]                 │
└─────────────────────────────────────────────────────┘
```

**Características OBLIGATORIAS**:
- ✅ **Preview renderizado**: Mostrar documento real antes de generar
- ✅ **No salteable**: Usuario DEBE ver preview antes de generar
- ✅ **Botón destacado**: "Aprobar y Generar" solo después de ver preview
- ✅ **Opción de editar**: Volver a paso 4 si algo está mal
- ✅ **Descarga de preview**: PDF temporal para revisión offline

#### **Paso 6: Enviar/Descargar**

```
┌─────────────────────────────────────────────────────┐
│  ✅ ¡Documento Generado!                            │
├─────────────────────────────────────────────────────┤
│  📄 compraventa_juan_perez.docx                     │
│  📊 47 campos procesados • 100% completado          │
│  ⏱️ Generado hace 2 minutos                         │
│                                                     │
│  Acciones:                                          │
│  ┌────────────────────────────────────────────┐    │
│  │  ⬇️ Descargar Documento                    │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │  📧 Enviar por Email                       │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  [🔄 Generar Otro Documento]                        │
└─────────────────────────────────────────────────────┘

(Si selecciona "Enviar por Email" → Modal)

┌─────────────────────────────────────────────────────┐
│  📧 Enviar Documento por Email              [×]     │
├─────────────────────────────────────────────────────┤
│  Destinatario:                                      │
│  [cliente@ejemplo.com                           ]   │
│                                                     │
│  Asunto:                                            │
│  [Documento Notarial - Compraventa              ]   │
│                                                     │
│  Mensaje:                                           │
│  ┌────────────────────────────────────────────┐    │
│  │ Estimado/a cliente,                        │    │
│  │                                            │    │
│  │ Le adjunto el documento notarial...        │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ☑️ Incluir documento adjunto                       │
│                                                     │
│  [Cancelar]  [📤 Enviar]                            │
└─────────────────────────────────────────────────────┘
```

**Características**:
- ✅ **Celebración visual**: Mensaje de éxito + estadísticas
- ✅ **Dos acciones principales**: Download O Email
- ✅ **Email modal**: Formulario inline con preview
- ✅ **Botón "Generar Otro"**: Reiniciar flujo
- ✅ **Guardado automático**: Documento en historial

### 3.3 Gestión de Plantillas

```
┌─────────────────────────────────────────────────────┐
│  📋 Gestión de Plantillas                           │
├─────────────────────────────────────────────────────┤
│  [🔍 Buscar...]  [Tipo ▾]  [Ordenar ▾]  [+ Nueva]  │
│                                                     │
│  Grid (3 columnas):                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │ 📄 Preview   │ │ 📄 Preview   │ │ 📄 Preview   ││
│  │ (16:9 ratio) │ │ (16:9 ratio) │ │ (16:9 ratio) ││
│  ├──────────────┤ ├──────────────┤ ├──────────────┤│
│  │ Compraventa  │ │ Donación     │ │ Poder        ││
│  │ 🏷️ Estándar   │ │ 🏷️ Simple    │ │ 🏷️ General   ││
│  │ 📌 47 campos  │ │ 📌 49 campos  │ │ 📌 32 campos  ││
│  │ 📅 23 Ene     │ │ 📅 15 Ene     │ │ 📅 10 Ene     ││
│  │ [✏️] [🗑️]     │ │ [✏️] [🗑️]     │ │ [✏️] [🗑️]     ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│                                                     │
│  Paginación: [◀] 1 2 3 ... 10 [▶]                  │
└─────────────────────────────────────────────────────┘
```

**Características**:
- Card con preview thumbnail
- Metadata: Nombre, tipo (badge), campos, fecha
- Acciones: Editar (✏️), Eliminar (🗑️)
- Filtros: Búsqueda, tipo de documento, ordenamiento
- Botón "+ Nueva" destacado

### 3.4 Historial

```
┌─────────────────────────────────────────────────────┐
│  📜 Historial de Documentos                         │
├─────────────────────────────────────────────────────┤
│  Filtros: [Fecha ▾] [Tipo ▾] [Cliente ▾]  [📊 Exportar]│
│                                                     │
│  Tabla:                                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ Fecha      │Tipo  │Cliente    │Estado  │Accs  ││
│  ├───────────────────────────────────────────────┤ │
│  │ 23 Ene 2025│🏷️ CV │Juan Pérez │✅ OK   │⬇️ 📧  ││
│  │ 22 Ene 2025│🏷️ DON│Ana García │✅ OK   │⬇️ 📧  ││
│  │ 20 Ene 2025│🏷️ POD│Luis Rojas │✅ OK   │⬇️ 📧  ││
│  │ 18 Ene 2025│🏷️ CV │Marta Díaz │✅ OK   │⬇️ 📧  ││
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Mostrando 1-50 de 234   [◀] 1 2 3 ... 5 [▶]       │
└─────────────────────────────────────────────────────┘
```

**Características**:
- Tabla con filas alternas (bg-white / bg-neutral-50)
- Columnas: Fecha, Tipo (badge), Cliente, Estado (badge), Acciones
- Acciones: Download (⬇️), Email (📧)
- Filtros: Date range picker, tipo selector, búsqueda de cliente
- Paginación: Max 50 por página
- Exportar: Botón para Excel/PDF

### 3.5 Configuración

```
┌─────────────────────────────────────────────────────┐
│  ⚙️ Configuración                                   │
├─────────────────────────────────────────────────────┤
│  Tabs: [👤 Perfil] [🏢 Notaría] [🎨 Estilos] [🔒 Seguridad]│
│                                                     │
│  👤 Perfil:                                         │
│  ┌────────────────────────────────────────────┐    │
│  │ Nombre completo:                           │    │
│  │ [Lic. Patricia Servin Maldonado         ]  │    │
│  │                                            │    │
│  │ Email:                                     │    │
│  │ [admin@notaria14.mx                     ]  │    │
│  │                                            │    │
│  │ Teléfono:                                  │    │
│  │ [+52 443 123 4567                       ]  │    │
│  │                                            │    │
│  │ [Guardar Cambios]                          │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

**4 Tabs**:
1. **Perfil**: Nombre, email, teléfono, foto
2. **Notaría**: Razón social, RFC, dirección, logo
3. **Estilos**: Font family, size, line spacing, header style
4. **Seguridad**: Cambio de contraseña, 2FA, sesiones activas

---

## 4. Sistema de Diseño Visual

### 4.1 Identidad de Marca

**Personalidad**: Profesionalismo legal + Eficiencia moderna
**Tono Emocional**: Confianza, autoridad, precisión
**Valores**: Seguridad, exactitud, flujos optimizados

### 4.2 Paleta de Colores

```css
/* Primary - Deep Professional Blue */
--primary-50:  #EFF6FF
--primary-100: #DBEAFE
--primary-200: #BFDBFE
--primary-300: #93C5FD
--primary-400: #60A5FA
--primary-500: #1E40AF  /* Main brand color */
--primary-600: #1E3A8A
--primary-700: #1E3A8A
--primary-800: #1E3A8A
--primary-900: #172554

/* Secondary - Success Green */
--secondary-500: #059669
--secondary-600: #047857

/* Neutral Grays */
--neutral-50:  #F9FAFB
--neutral-100: #F3F4F6
--neutral-200: #E5E7EB
--neutral-400: #9CA3AF
--neutral-600: #4B5563
--neutral-700: #374151
--neutral-900: #111827

/* Semantic Colors */
--success:  #10B981
--warning:  #F59E0B
--error:    #EF4444
--info:     #3B82F6

/* Backgrounds */
--bg-light: #FFFFFF
--bg-subtle: #F9FAFB
--bg-dark:  #0F172A
--bg-dark-elevated: #1E293B
```

**Aplicación**:
- **Primary**: Botones principales, links, elementos interactivos
- **Secondary**: Estados de éxito, acciones positivas
- **Neutral**: Texto, bordes, backgrounds sutiles
- **Semantic**: Alerts, badges, feedback visual

### 4.3 Tipografía

**Font Family**: `'Inter', system-ui, sans-serif`
**Peso**: 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold)

**Escala de Tamaño**:
```
Display (h1): 36px / 44px / 700 / -0.02em
H2:           30px / 38px / 600 / -0.01em
H3:           24px / 32px / 600
H4:           20px / 28px / 600
H5:           18px / 26px / 600
Body Large:   16px / 26px / 400
Body:         14px / 22px / 400
Small:        13px / 20px / 400
Tiny:         12px / 18px / 500
```

**Instalación**:
```html
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
```

### 4.4 Sistema de Espaciado

**Base Unit**: 4px

```
xs:   4px   (0.25rem)
sm:   8px   (0.5rem)
md:   16px  (1rem)
lg:   24px  (1.5rem)
xl:   32px  (2rem)
2xl:  48px  (3rem)
3xl:  64px  (4rem)
```

### 4.5 Componentes UI

#### **Button**

**Tamaños**:
- sm: 32px altura, px-3 padding
- md: 40px altura, px-4 padding
- lg: 48px altura, px-6 padding

**Variantes**:
```tsx
// Primary
<Button variant="primary" size="md">
  Generar Documento
</Button>
// bg-primary-500, text-white, hover:bg-primary-600

// Secondary
<Button variant="secondary" size="md">
  Cancelar
</Button>
// border-2 border-primary-500, text-primary-500, hover:bg-primary-50

// Ghost
<Button variant="ghost" size="sm">
  Editar
</Button>
// transparent, text-primary-500, hover:bg-neutral-100
```

**Estados**:
- Default: Base styles
- Hover: Brighter + lift (`translateY(-1px)`)
- Active: Scale down (`scale-95`)
- Disabled: `opacity-40`, cursor-not-allowed
- Loading: Spinner + disabled

#### **Input**

**Base**:
- Altura: 40px (match md button)
- Padding: px-3, py-2
- Border: 1px solid neutral-200
- Border radius: 8px (rounded-lg)
- Font size: 14px

**Estados**:
```tsx
// Default
className="border border-neutral-200 bg-white rounded-lg"

// Focus
className="ring-2 ring-primary-500 border-primary-500"

// Error
className="border-error ring-error/20"

// Disabled
className="bg-neutral-50 text-neutral-400 cursor-not-allowed"
```

**Label**:
```tsx
<label className="text-sm font-medium text-neutral-700 mb-1.5">
  Nombre completo
</label>
```

#### **Card**

**Base**:
```tsx
<div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-card hover:shadow-card-hover transition-shadow">
  {children}
</div>
```

**Sombras**:
- Default: `0 1px 3px rgba(0,0,0,0.1)`
- Hover: `0 4px 12px rgba(0,0,0,0.15)`

**Variante Clickable**:
```tsx
<div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-card hover:shadow-card-hover hover:scale-101 transition-all cursor-pointer">
  {children}
</div>
```

#### **Badge/Tag**

**Tamaños**:
- sm: 20px altura, px-2.5 py-0.5
- md: 24px altura, px-3 py-1

**Variantes**:
```tsx
// Default
<Badge variant="default">Pendiente</Badge>
// bg-neutral-100, text-neutral-700

// Success
<Badge variant="success">Completado</Badge>
// bg-success/10, text-success-700

// Warning
<Badge variant="warning">En proceso</Badge>
// bg-warning/10, text-warning-700

// Error
<Badge variant="error">Error</Badge>
// bg-error/10, text-error-700
```

**Forma**: `rounded-full`

#### **Alert/Toast**

**Estructura**:
```tsx
<div className="flex items-start gap-3 p-4 rounded-lg border-l-4">
  <Icon className="w-5 h-5" />
  <div>
    <p className="font-medium">{title}</p>
    <p className="text-sm text-neutral-600">{message}</p>
  </div>
  <button>×</button>
</div>
```

**Variantes** (border-left color + background):
- Success: border-success, bg-success/10
- Warning: border-warning, bg-warning/10
- Error: border-error, bg-error/10
- Info: border-info, bg-info/10

**Toast Position**: top-right, 16px margin, slide-in animation

#### **Modal**

**Estructura**:
```tsx
<div className="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm z-50">
  <div className="max-w-lg bg-white rounded-xl shadow-modal animate-fade-in">
    <div className="px-6 py-4 border-b border-neutral-200">
      <h3>Título</h3>
    </div>
    <div className="px-6 py-4">
      {children}
    </div>
    <div className="px-6 py-4 border-t border-neutral-200 flex justify-end gap-3">
      <Button variant="secondary">Cancelar</Button>
      <Button variant="primary">Confirmar</Button>
    </div>
  </div>
</div>
```

**Animación**: scale-95 → scale-100, fade-in 200ms

#### **File Upload Dropzone**

**Estados**:
```tsx
// Default
<div className="border-2 border-dashed border-neutral-300 rounded-lg min-h-48 flex flex-col items-center justify-center p-6">
  <UploadIcon className="w-12 h-12 text-neutral-400" />
  <p className="text-sm text-neutral-600">Arrastra archivos o haz clic</p>
  <p className="text-xs text-neutral-400">PDF, JPG, PNG (max 50MB)</p>
</div>

// Hover/Drag
<div className="border-2 border-solid border-primary-400 bg-primary-50 rounded-lg ...">
```

---

## 5. Patrones Preservados de Legacy

### 5.1 Análisis de Aplicaciones Streamlit Legacy

Se analizaron 3 aplicaciones Streamlit existentes:
1. `escrituras.py` - App principal con Google Drive
2. `movil_cancelaciones.py` - Versión mobile-optimized
3. `por_partes.py` - Versión con categorización avanzada

### 5.2 Patrones Críticos Identificados

#### **1. Three-Stage Wizard Flow**

**Estado de sesión**:
```python
st.session_state.process_stage = 'upload' | 'edit' | 'completed'
```

**React Implementation**:
```tsx
type ProcessStage = 'upload' | 'edit' | 'completed';

const useGenerationFlow = () => {
  const [stage, setStage] = useState<ProcessStage>('upload');
  const [data, setData] = useState({
    template: null,
    documents: [],
    extractedData: {},
    editedData: {}
  });

  return { stage, setStage, data, setData };
};
```

#### **2. Categorized Document Upload** ⚠️ **MUY IMPORTANTE**

**Patrón de `por_partes.py`**:
```python
CATEGORIAS_POR_TIPO = {
    "compraventa": {
        "parte_a": {
            "nombre": "Vendedor",
            "icono": "👤",
            "descripcion": "Documentos del vendedor",
            "requeridos": ["INE", "Escritura anterior", "RFC"]
        },
        "parte_b": {
            "nombre": "Comprador",
            "icono": "👥",
            "descripcion": "Documentos del comprador",
            "requeridos": ["INE", "RFC", "Comprobante domicilio"]
        },
        "otros": {
            "nombre": "Inmueble",
            "icono": "🏠",
            "descripcion": "Documentos de la propiedad",
            "requeridos": ["Avalúo", "Predial", "Agua"]
        }
    },
    "poder": {
        "parte_a": {
            "nombre": "Poderdante",
            ...
        }
    }
}
```

**React Implementation**:
```tsx
interface DocumentCategory {
  key: 'parte_a' | 'parte_b' | 'otros';
  name: string;
  icon: string;
  description: string;
  required: string[];
}

const DOCUMENT_CATEGORIES: Record<DocumentType, DocumentCategory[]> = {
  compraventa: [
    {
      key: 'parte_a',
      name: 'Vendedor',
      icon: '👤',
      description: 'Documentos del vendedor',
      required: ['INE', 'Escritura anterior', 'RFC']
    },
    {
      key: 'parte_b',
      name: 'Comprador',
      icon: '👥',
      description: 'Documentos del comprador',
      required: ['INE', 'RFC', 'Comprobante domicilio']
    },
    {
      key: 'otros',
      name: 'Inmueble',
      icon: '🏠',
      description: 'Documentos de la propiedad',
      required: ['Avalúo', 'Predial', 'Agua']
    }
  ],
  // ... otros tipos
};

// Componente
const CategorizedUpload: React.FC<{ documentType: DocumentType }> = ({ documentType }) => {
  const categories = DOCUMENT_CATEGORIES[documentType];

  return (
    <Tabs>
      {categories.map(category => (
        <TabsContent key={category.key} value={category.key}>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{category.icon}</span>
              <div>
                <h3 className="font-semibold">{category.name}</h3>
                <p className="text-sm text-neutral-600">{category.description}</p>
              </div>
            </div>

            <Collapsible>
              <CollapsibleTrigger>
                📋 Documentos requeridos ({category.required.length})
              </CollapsibleTrigger>
              <CollapsibleContent>
                <ul className="list-disc pl-6">
                  {category.required.map(doc => (
                    <li key={doc}>{doc}</li>
                  ))}
                </ul>
              </CollapsibleContent>
            </Collapsible>

            <FileDropzone
              onUpload={(files) => handleCategoryUpload(category.key, files)}
              category={category.key}
            />
          </div>
        </TabsContent>
      ))}
    </Tabs>
  );
};
```

#### **3. Progress Step Component**

**Legacy pattern**:
```python
def show_progress_step(step, total_steps, title, description):
    st.markdown(f"### Paso {step} de {total_steps}")
    st.progress(step / total_steps)
    st.markdown(f"**{title}**")
    st.caption(description)
```

**React Implementation**:
```tsx
interface ProgressStepProps {
  currentStep: number;
  totalSteps: number;
  title: string;
  description?: string;
}

const ProgressStep: React.FC<ProgressStepProps> = ({
  currentStep,
  totalSteps,
  title,
  description
}) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-neutral-600">
          Paso {currentStep} de {totalSteps}
        </span>
        <span className="text-sm text-neutral-500">{progress}%</span>
      </div>

      <Progress value={progress} className="h-2" />

      <h3 className="text-lg font-semibold text-primary-500">{title}</h3>

      {description && (
        <p className="text-sm text-neutral-600">{description}</p>
      )}
    </div>
  );
};
```

#### **4. Dynamic Field Categorization**

**Legacy pattern** (categorías dinámicas):
```python
def categorize_fields(placeholders):
    categories = {
        'Personas': [],
        'Inmueble': [],
        'Documentos': [],
        'Otros': []
    }

    for placeholder in placeholders:
        placeholder_lower = placeholder.lower()

        if any(word in placeholder_lower for word in ['vendedor', 'comprador', 'nombre', 'rfc']):
            categories['Personas'].append(placeholder)
        elif any(word in placeholder_lower for word in ['inmueble', 'superficie', 'lote']):
            categories['Inmueble'].append(placeholder)
        elif any(word in placeholder_lower for word in ['escritura', 'registro', 'fecha']):
            categories['Documentos'].append(placeholder)
        else:
            categories['Otros'].append(placeholder)

    return {k: v for k, v in categories.items() if v}
```

**React Implementation**:
```tsx
const categorizeFields = (placeholders: string[]): Record<string, string[]> => {
  const categories: Record<string, string[]> = {
    'Personas': [],
    'Inmueble': [],
    'Documentos': [],
    'Otros': []
  };

  const rules: Record<string, string[]> = {
    'Personas': ['vendedor', 'comprador', 'nombre', 'rfc', 'edad', 'curp', 'ine'],
    'Inmueble': ['inmueble', 'superficie', 'lote', 'manzana', 'catastral', 'avaluo'],
    'Documentos': ['escritura', 'registro', 'notario', 'fecha', 'numero', 'constancia'],
  };

  placeholders.forEach(placeholder => {
    const lower = placeholder.toLowerCase();
    let categorized = false;

    for (const [category, keywords] of Object.entries(rules)) {
      if (keywords.some(keyword => lower.includes(keyword))) {
        categories[category].push(placeholder);
        categorized = true;
        break;
      }
    }

    if (!categorized) {
      categories['Otros'].push(placeholder);
    }
  });

  // Filtrar categorías vacías
  return Object.fromEntries(
    Object.entries(categories).filter(([_, fields]) => fields.length > 0)
  );
};
```

#### **5. Metrics Dashboard**

**Legacy pattern**:
```python
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_placeholders}</div>
        <div class="metric-label">Placeholders</div>
    </div>
    """, unsafe_allow_html=True)
```

**React Implementation**:
```tsx
interface MetricCardProps {
  value: number | string;
  label: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ value, label }) => {
  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-4 text-center shadow-card">
      <div className="text-3xl font-bold text-primary-500">
        {value}
      </div>
      <div className="text-sm text-neutral-600 font-medium mt-1">
        {label}
      </div>
    </div>
  );
};

// Uso
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  <MetricCard value={totalFields} label="Total Campos" />
  <MetricCard value={foundFields} label="Encontrados" />
  <MetricCard value={emptyFields} label="Vacíos" />
  <MetricCard value={`${completionRate}%`} label="Completado" />
</div>
```

#### **6. Status Pill Component**

**Legacy CSS**:
```css
.status-indicator {
    display: inline-flex;
    align-items: center;
    padding: 0.4rem 0.8rem;
    border-radius: 24px;
    font-weight: 500;
    font-size: clamp(0.75rem, 2vw, 0.9rem);
}

.status-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
```

**React Implementation**:
```tsx
interface StatusPillProps {
  status: 'success' | 'warning' | 'error' | 'info';
  children: React.ReactNode;
}

const StatusPill: React.FC<StatusPillProps> = ({ status, children }) => {
  const styles = {
    success: 'bg-success/10 text-success-700 border-success/20',
    warning: 'bg-warning/10 text-warning-700 border-warning/20',
    error: 'bg-error/10 text-error-700 border-error/20',
    info: 'bg-info/10 text-info-700 border-info/20',
  };

  return (
    <span className={`
      inline-flex items-center gap-1.5
      px-3 py-1 rounded-full
      text-xs font-medium border
      ${styles[status]}
    `}>
      {children}
    </span>
  );
};

// Uso
<StatusPill status="success">✓ Google Vision API</StatusPill>
<StatusPill status="warning">⚠ Google Drive (Limitado)</StatusPill>
```

#### **7. Mobile-First Responsive Patterns**

**Critical CSS from legacy**:
```css
/* Fluid typography */
.main-header h1 {
    font-size: clamp(1.8rem, 5vw, 3rem);
}

/* Touch-friendly inputs */
.stTextInput input {
    font-size: 16px !important; /* Evita zoom en iOS */
}

/* Mobile breakpoints */
@media (max-width: 768px) {
    .main-header {
        padding: 1rem;
    }

    .process-card {
        padding: 1rem;
    }

    /* Touch targets */
    .stTabs [data-baseweb="tab"] {
        padding: 1rem !important;
        min-height: 44px;
    }
}
```

**React/Tailwind Implementation**:
```tsx
// Componente responsive
<div className="
  bg-white
  rounded-xl
  p-4 md:p-6 lg:p-8
  shadow-card
">
  <h1 className="
    text-2xl md:text-3xl lg:text-4xl
    font-bold
    text-primary-500
  ">
    Título Responsivo
  </h1>

  <input
    type="text"
    className="
      w-full
      h-11 md:h-12
      px-3 md:px-4
      text-base
      border border-neutral-200
      rounded-lg
      focus:ring-2 focus:ring-primary-500
    "
    // font-size: 16px previene zoom en iOS
  />

  <button className="
    w-full md:w-auto
    h-11 md:h-12
    px-4 md:px-6
    text-sm md:text-base
    font-semibold
    bg-primary-500 text-white
    rounded-lg
    hover:bg-primary-600
    transition-colors
  ">
    Acción
  </button>
</div>
```

#### **8. Template Card with Hover Effect**

**Legacy pattern**:
```python
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border-radius: 12px;
    padding: 1.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
">
    <h4>{template['name']}</h4>
    <small>📦 {file_size:.1f} KB</small>
</div>
""", unsafe_allow_html=True)
```

**React Implementation**:
```tsx
interface TemplateCardProps {
  template: {
    id: string;
    name: string;
    size: number;
    placeholderCount: number;
    modifiedAt: string;
  };
  onSelect: (id: string) => void;
}

const TemplateCard: React.FC<TemplateCardProps> = ({ template, onSelect }) => {
  return (
    <div
      onClick={() => onSelect(template.id)}
      className="
        group
        bg-gradient-to-br from-primary-500 to-primary-700
        rounded-xl p-6
        text-white
        cursor-pointer
        transition-all duration-300
        hover:shadow-xl
        hover:-translate-y-1
      "
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
          <FileTextIcon className="w-6 h-6" />
        </div>
        <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
          {template.placeholderCount} campos
        </Badge>
      </div>

      <h3 className="font-semibold text-lg mb-1">
        {template.name}
      </h3>

      <div className="flex items-center gap-4 text-sm text-white/70">
        <span>📦 {(template.size / 1024).toFixed(1)} KB</span>
        <span>📅 {formatDate(template.modifiedAt)}</span>
      </div>

      <Button
        variant="ghost"
        className="mt-4 w-full bg-white/10 hover:bg-white/20 text-white"
      >
        Seleccionar →
      </Button>
    </div>
  );
};
```

#### **9. Email Sender Component**

**Legacy pattern**:
```python
with st.form("email_form"):
    to_email = st.text_input("📬 Destinatario")
    subject = st.text_input("📝 Asunto")
    include_attachment = st.checkbox("📎 Incluir documento adjunto", value=True)
    email_body = st.text_area("✉️ Mensaje", height=180)

    submitted = st.form_submit_button("📤 Enviar Email Ahora")
```

**React Implementation**:
```tsx
interface EmailFormProps {
  documentName: string;
  documentData: Blob;
  onSuccess: () => void;
}

const EmailForm: React.FC<EmailFormProps> = ({
  documentName,
  documentData,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    to: '',
    subject: `Documento Notarial - ${documentName}`,
    body: `Estimado/a cliente,\n\nLe adjunto el documento notarial solicitado...`,
    includeAttachment: true
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await sendEmail({
        ...formData,
        attachment: formData.includeAttachment ? documentData : null
      });

      toast.success('✅ Email enviado exitosamente');
      onSuccess();
    } catch (error) {
      toast.error('❌ Error al enviar email');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium text-neutral-700 mb-1.5 block">
          📬 Destinatario
        </label>
        <Input
          type="email"
          value={formData.to}
          onChange={(e) => setFormData({ ...formData, to: e.target.value })}
          placeholder="cliente@ejemplo.com"
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium text-neutral-700 mb-1.5 block">
          📝 Asunto
        </label>
        <Input
          type="text"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
        />
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          checked={formData.includeAttachment}
          onCheckedChange={(checked) =>
            setFormData({ ...formData, includeAttachment: !!checked })
          }
        />
        <label className="text-sm font-medium">
          📎 Incluir documento adjunto
        </label>
      </div>

      <div>
        <label className="text-sm font-medium text-neutral-700 mb-1.5 block">
          ✉️ Mensaje
        </label>
        <Textarea
          value={formData.body}
          onChange={(e) => setFormData({ ...formData, body: e.target.value })}
          rows={8}
        />
      </div>

      <div className="flex gap-3">
        <Button type="button" variant="secondary" className="flex-1">
          Cancelar
        </Button>
        <Button type="submit" variant="primary" className="flex-1">
          📤 Enviar Email
        </Button>
      </div>
    </form>
  );
};
```

#### **10. Service Status Sidebar**

**Legacy pattern**:
```python
with st.sidebar:
    st.markdown('<div class="status-indicator status-success">✓ Google Vision API</div>')
    if drive_service:
        st.markdown('<div class="status-indicator status-success">✓ Google Drive API</div>')
    else:
        st.markdown('<div class="status-indicator status-warning">⚠ Google Drive (Limitado)</div>')
```

**React Implementation**:
```tsx
const ServiceStatusSidebar: React.FC = () => {
  const { services } = useServices();

  return (
    <div className="space-y-2 p-4 bg-neutral-50 rounded-lg">
      <h4 className="text-sm font-semibold text-neutral-700 mb-3">
        Estado de Servicios
      </h4>

      <StatusPill status={services.vision ? 'success' : 'error'}>
        {services.vision ? '✓' : '✗'} Google Vision API
      </StatusPill>

      <StatusPill status={services.drive ? 'success' : 'warning'}>
        {services.drive ? '✓' : '⚠'} Google Drive
        {!services.drive && ' (Limitado)'}
      </StatusPill>

      <StatusPill status={services.openai ? 'success' : 'error'}>
        {services.openai ? '✓' : '✗'} OpenAI GPT-4
      </StatusPill>

      <StatusPill status={services.supabase ? 'success' : 'error'}>
        {services.supabase ? '✓' : '✗'} Supabase
      </StatusPill>
    </div>
  );
};
```

---

## 6. Estructura del Proyecto

```
controlnot-frontend/
├── public/
│   └── notaria-logo.svg
├── src/
│   ├── assets/
│   │   ├── fonts/
│   │   └── images/
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── alert.tsx
│   │   │   ├── modal.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── checkbox.tsx
│   │   │   └── dropdown.tsx
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Topbar.tsx
│   │   │   ├── Layout.tsx
│   │   │   └── ServiceStatus.tsx
│   │   ├── generation/              # Flujo de generación
│   │   │   ├── TemplateSelector.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── CategorizedUpload.tsx  # NUEVO - del análisis
│   │   │   ├── ExtractionProgress.tsx
│   │   │   ├── FieldEditor.tsx
│   │   │   ├── MetricsDashboard.tsx    # NUEVO - del análisis
│   │   │   ├── DocumentPreview.tsx
│   │   │   ├── DownloadEmail.tsx
│   │   │   └── Stepper.tsx
│   │   ├── templates/
│   │   │   ├── TemplateGrid.tsx
│   │   │   ├── TemplateCard.tsx       # Con hover effect legacy
│   │   │   ├── TemplateUpload.tsx
│   │   │   └── TemplateEditor.tsx
│   │   ├── history/
│   │   │   ├── DocumentTable.tsx
│   │   │   ├── Filters.tsx
│   │   │   └── Pagination.tsx
│   │   ├── settings/
│   │   │   ├── ProfileTab.tsx
│   │   │   ├── NotaryTab.tsx
│   │   │   ├── StylesTab.tsx
│   │   │   └── SecurityTab.tsx
│   │   └── shared/
│   │       ├── StatusPill.tsx         # NUEVO - del análisis
│   │       ├── MetricCard.tsx         # NUEVO - del análisis
│   │       ├── ProgressStep.tsx       # NUEVO - del análisis
│   │       ├── EmailForm.tsx          # NUEVO - del análisis
│   │       └── FileDropzone.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Generation.tsx
│   │   ├── Templates.tsx
│   │   ├── History.tsx
│   │   ├── Settings.tsx
│   │   └── Login.tsx
│   ├── services/
│   │   ├── api.ts                     # Axios instance
│   │   ├── templates.ts
│   │   ├── documents.ts
│   │   ├── extraction.ts
│   │   ├── clients.ts
│   │   ├── cases.ts
│   │   └── auth.ts
│   ├── stores/
│   │   ├── useAppStore.ts             # Zustand global state
│   │   ├── useAuthStore.ts
│   │   └── useGenerationStore.ts
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts
│   │   ├── document.ts
│   │   └── template.ts
│   ├── lib/
│   │   ├── utils.ts
│   │   ├── validations.ts
│   │   └── constants.ts               # Document categories, etc.
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useToast.ts
│   │   └── useServices.ts             # Service status check
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env.example
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

---

## 7. Roadmap de Implementación

### **Fase 1: Setup del Proyecto** (1-2 horas)

**Tareas**:
1. ✅ Crear proyecto Vite + React + TypeScript
2. ✅ Instalar dependencias
3. ✅ Configurar TailwindCSS con design tokens
4. ✅ Instalar shadcn/ui components
5. ✅ Setup folder structure
6. ✅ Configurar ESLint + Prettier

**Comandos**:
```bash
# Crear proyecto
npm create vite@latest controlnot-frontend -- --template react-ts

# Instalar dependencias
cd controlnot-frontend
npm install

# Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn/ui
npx shadcn-ui@latest init

# Routing
npm install react-router-dom

# State management
npm install zustand

# Forms
npm install react-hook-form zod @hookform/resolvers

# HTTP
npm install axios

# Utils
npm install clsx tailwind-merge date-fns

# Icons
npm install lucide-react
```

**Archivos clave**:
```typescript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          // ... (ver sección 4.2)
        },
        // ... resto de colores
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      // ... resto de configuración
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
```

### **Fase 2: Componentes Base** (3-4 horas)

**Tareas**:
1. ✅ Instalar shadcn/ui components necesarios
2. ✅ Crear Layout (Sidebar + Topbar)
3. ✅ Configurar React Router
4. ✅ Setup Zustand stores
5. ✅ Crear componentes compartidos (StatusPill, MetricCard, ProgressStep)

**shadcn/ui components a instalar**:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add select
npx shadcn-ui@latest add toast
```

**Prioridad alta - Componentes Legacy**:
```bash
# Crear componentes del análisis legacy
touch src/components/shared/StatusPill.tsx
touch src/components/shared/MetricCard.tsx
touch src/components/shared/ProgressStep.tsx
touch src/components/shared/EmailForm.tsx
touch src/components/generation/CategorizedUpload.tsx
touch src/components/generation/MetricsDashboard.tsx
```

### **Fase 3: Páginas Core** (6-8 horas)

**Prioridad 1: Generación de Documentos** (4 horas)
```bash
touch src/pages/Generation.tsx
touch src/components/generation/TemplateSelector.tsx
touch src/components/generation/CategorizedUpload.tsx  # CRÍTICO
touch src/components/generation/ExtractionProgress.tsx
touch src/components/generation/FieldEditor.tsx
touch src/components/generation/DocumentPreview.tsx
touch src/components/generation/DownloadEmail.tsx
```

**Características OBLIGATORIAS**:
- ✅ Wizard de 6 pasos
- ✅ **Categorización dinámica** según tipo de documento
- ✅ **Métricas en tiempo real** (Total, Encontrados, Vacíos, Tasa)
- ✅ **Validación estricta** antes de generar
- ✅ **Preview obligatorio**
- ✅ Email O Download

**Prioridad 2: Dashboard** (1 hora)
```bash
touch src/pages/Dashboard.tsx
```
- Métricas de uso
- Documentos recientes
- Actividad reciente

**Prioridad 3: Templates** (1.5 horas)
```bash
touch src/pages/Templates.tsx
touch src/components/templates/TemplateGrid.tsx
touch src/components/templates/TemplateCard.tsx  # Con hover effect
```

**Prioridad 4: History** (1.5 horas)
```bash
touch src/pages/History.tsx
touch src/components/history/DocumentTable.tsx
```

### **Fase 4: Integración API** (3-4 horas)

**Tareas**:
1. ✅ Configurar Axios con interceptors
2. ✅ Implementar servicios API
3. ✅ Conectar componentes a API real
4. ✅ Manejo de errores y loading states
5. ✅ Testing de flujos completos

**API Client Setup**:
```typescript
// src/services/api.ts
import axios from 'axios';
import { supabase } from '@/lib/supabase';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### **Fase 5: Autenticación** (2-3 horas)

**Tareas**:
1. ✅ Setup Supabase client
2. ✅ Implementar login/logout
3. ✅ Protected routes
4. ✅ Auth state management
5. ✅ Token refresh automático

**Supabase Setup**:
```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### **Fase 6: Polish & Testing** (2-3 horas)

**Tareas**:
1. ✅ Responsive testing (mobile/tablet/desktop)
2. ✅ Accessibility audit (WCAG AA mínimo)
3. ✅ Performance optimization
4. ✅ Error handling refinement
5. ✅ Loading states polish
6. ✅ Animation timing adjustments

---

## 8. Próximos Pasos

### **Paso 1: Confirmar Plan**

Usuario debe confirmar:
- ✅ Stack tecnológico (React + TypeScript + Vite + TailwindCSS)
- ✅ Enfoque de implementación (mocks iniciales → API real)
- ✅ Prioridades de features (Generación > Templates > History > Settings)
- ✅ Patrones preservados de legacy (especialmente categorización)

### **Paso 2: Setup Inicial**

Ejecutar Fase 1 completa:
```bash
# 1. Crear proyecto
npm create vite@latest controlnot-frontend -- --template react-ts

# 2. Instalar todas las dependencias
# (ver comandos en Fase 1)

# 3. Configurar Tailwind con design tokens
# (copiar configuración de sección 4)

# 4. Instalar shadcn/ui components
# (ver lista en Fase 2)

# 5. Crear estructura de carpetas
# (ver sección 6)
```

### **Paso 3: Implementación Incremental**

**Semana 1**:
- Día 1: Setup + Componentes base
- Día 2-3: Página de Generación (6 pasos)
- Día 4: Dashboard + Templates
- Día 5: History + Settings
- Día 6: Integración API + Testing

**Criterios de Éxito**:
- ✅ Flujo completo de generación funcional
- ✅ Categorización dinámica implementada
- ✅ Métricas en tiempo real
- ✅ Preview obligatorio
- ✅ Validación estricta
- ✅ Responsive mobile-first
- ✅ Patrones legacy preservados

---

## 9. Archivos de Referencia

### Documentación Backend:
- `backend/AUTHENTICATION.md` - Guía de autenticación
- `backend/API_EXAMPLES.md` - Ejemplos de uso de API
- `backend/database/migrations/` - Esquema de BD

### Aplicaciones Legacy:
- `escrituras.py` - App principal con Google Drive
- `movil_cancelaciones.py` - Versión mobile-optimized
- `por_partes.py` - **Categorización avanzada** ⭐

### Análisis de Agentes:
- **project-deep-analyzer**: Requerimientos backend completos
- **ux-researcher**: Arquitectura UX exhaustiva
- **ui-designer**: Sistema de diseño visual
- **explore (legacy)**: Patrones críticos preservados

---

## 10. Notas Finales

### ⚠️ **CRÍTICO - NO OLVIDAR**:

1. **Categorización de Documentos por Roles**
   - Sistema COMPLETO de `por_partes.py`
   - Tabs dinámicos según tipo de documento
   - Lista de documentos requeridos por categoría
   - Contexto para AI extraction

2. **Validación Estricta de Campos**
   - NO permitir generar con campos vacíos
   - Indicadores visuales claros (✓ / ⚠️)
   - Métricas en tiempo real
   - Botón "Re-extraer" disponible

3. **Preview Obligatorio**
   - NO salteable
   - Renderizado real del documento
   - Opción de volver a editar
   - Aprobación explícita antes de generar

4. **Mobile-First Design**
   - Touch targets mínimo 44px
   - Font size 16px en inputs (prevenir zoom iOS)
   - Layout responsivo con breakpoints
   - Horizontal scroll para tabs en móvil

5. **Patrones Visuales Legacy**
   - Colores exactos (`#1e3c72`, `#2a5298`)
   - Gradientes específicos
   - Sombras y hover effects
   - Status pills con colores semánticos
   - Métricas dashboard con grid 2x2/4-column

---

**Última actualización**: 2025-01-23
**Versión**: 2.0.0
**Autor**: ControlNot Development Team
**Status**: ✅ Listo para implementación
