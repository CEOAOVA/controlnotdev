# 🚀 PLAN MVP ÁGIL - CONTROLNOT V2
## Code-First | OpenRouter + Multi-Providers | Deploy Coolify

**Versión**: 2.0.0
**Fecha**: 2025-01-13
**Base de referencia**: `por_partes.py` (2,550 líneas, 100% funcionalidad)
**Enfoque**: MVP funcional en 4 semanas → Migración a DB después

---

## 📋 ÍNDICE

1. [Filosofía del MVP](#filosofía-del-mvp)
2. [Inventario Completo (por_partes.py)](#inventario-completo)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Arquitectura](#arquitectura)
5. [Estructura de Carpetas](#estructura-de-carpetas)
6. [Modelos de Datos](#modelos-de-datos)
7. [Servicios Core](#servicios-core)
8. [OpenRouter Integration](#openrouter-integration)
9. [Roadmap 4 Semanas](#roadmap-4-semanas)
10. [Deploy en Coolify](#deploy-en-coolify)
11. [Migración Futura a DB](#migración-futura-a-db)

---

## 🎯 FILOSOFÍA DEL MVP

**Principio**: Código funcional primero, infraestructura después

### Decisiones Arquitectónicas

✅ **SÍ en MVP**:
- Backend FastAPI con todos los servicios funcionales
- Frontend React con UI profesional y categorización
- Procesamiento paralelo de OCR (5-10x más rápido)
- OpenRouter para flexibilidad de providers (OpenAI, Anthropic, etc.)
- Storage local (archivos + JSON)
- Deploy en Coolify (Docker Compose)

⏳ **NO en MVP** (Fase 2):
- Base de datos PostgreSQL/Supabase
- Autenticación de usuarios
- Sistema de permisos
- Cache Redis
- Analytics avanzado

### Ventajas del Enfoque

| Métrica | MVP Ágil | Plan Completo |
|---------|----------|---------------|
| **Tiempo** | 4 semanas | 9 semanas |
| **Costo dev** | $8,000-12,000 | $18,000-28,000 |
| **Funcionalidad** | 100% | 100% + extras |
| **Database** | JSON local | PostgreSQL |
| **Auth** | No (público) | Sí |
| **Deploy** | Coolify básico | Coolify + CI/CD |

---

## 📊 INVENTARIO COMPLETO (por_partes.py)

### ✅ Funcionalidad Identificada

| # | Componente | Descripción | Líneas | Migrar a |
|---|------------|-------------|--------|----------|
| 1 | **CLAVES_COMUNES** | 5 campos comunes a todos los documentos | 368-374 | `models/base.py` |
| 2 | **CLAVES_COMPRAVENTA** | 42 campos específicos de compraventa | 377-784 | `models/compraventa.py` |
| 3 | **CLAVES_DONACION** | 42 campos específicos de donación | 785-1284 | `models/donacion.py` |
| 4 | **CLAVES_TESTAMENTO** | 15 campos de testamento | 1287-1310 | `models/testamento.py` |
| 5 | **CLAVES_PODER** | 15 campos de poder notarial | 1312-1337 | `models/poder.py` |
| 6 | **CLAVES_SOCIEDAD** | 15 campos de constitución sociedad | 1339-1360 | `models/sociedad.py` |
| 7 | **TIPOS_DOCUMENTO** | Diccionario maestro con merge de claves | 1363-1384 | `data/document_types.json` |
| 8 | **categorize_documents_by_role()** | Define categorías por tipo de doc | 1959-2182 | `services/categorization_service.py` |
| 9 | **document_uploader_by_category()** | UI tabs para upload categorizado | 2184-2291 | `frontend/CategorizedUploader.tsx` |
| 10 | **process_categorized_documents()** | Procesa docs por categoría con headers | 2293-2335 | `services/ocr_service.py` |
| 11 | **detect_text()** | OCR Google Vision | 1856-1866 | `services/ocr_service.py` |
| 12 | **process_text_with_openai_dynamic()** | Extracción IA con GPT-4o | 1745-1790 | `services/ai_service.py` |
| 13 | **generate_document_with_dynamic_placeholders()** | Generación Word | 1688-1743 | `services/document_service.py` |
| 14 | **apply_bold_formatting()** | Formato negritas en Word | 1939-1957 | `services/document_service.py` |
| 15 | **send_email_smtp()** | Envío email con adjunto | 1885-1909 | `services/email_service.py` |
| 16 | **email_sender_component()** | UI para enviar email | 1911-1937 | `frontend/EmailForm.tsx` |
| 17 | **extract_placeholders_from_template()** | Parser placeholders {{nombre}} | 1458-1502 | `services/template_service.py` |
| 18 | **map_placeholders_to_keys_by_type()** | Mapeo inteligente placeholders → claves | 1424-1456 | `services/mapping_service.py` |
| 19 | **detect_document_type()** | Auto-detecta tipo por placeholders | 1388-1416 | `services/classification_service.py` |
| 20 | **create_dynamic_data_editor()** | Editor de campos extraídos | 1535-1593 | `frontend/DataEditor.tsx` |
| 21 | **enhanced_template_selector_with_types()** | Selector plantillas con tipos | 1595-1686 | `frontend/TemplateSelector.tsx` |
| 22 | **show_progress_step()** | Barra de progreso visual | 1868-1883 | `frontend/ProgressIndicator.tsx` |
| 23 | **CSS personalizado** | Estilos profesionales | 35-366 | `frontend/globals.css` |
| 24 | **Estado 'upload'** | Flujo de carga de documentos | 2362-2430 | `pages/ProcessPage.tsx` |
| 25 | **Estado 'edit'** | Flujo de edición de datos | 2432-2508 | `pages/ProcessPage.tsx` |
| 26 | **Estado 'completed'** | Flujo de descarga/email | 2510-2542 | `pages/ProcessPage.tsx` |

### 📦 Total de Componentes a Migrar

- **6 modelos de datos** (CLAVES_*)
- **19 funciones de backend**
- **7 componentes de frontend**
- **3 estados de flujo**
- **1 sistema de CSS personalizado**

**GARANTÍA**: 100% de funcionalidad preservada + mejoras de performance

---

## 🏗️ STACK TECNOLÓGICO

### Backend

```yaml
Lenguaje: Python 3.11+
Framework: FastAPI 0.109+
Validation: Pydantic 2.5+
Testing: pytest + pytest-asyncio
Docs: OpenAPI 3.1 (Swagger auto-generado)
```

**Dependencias clave**:
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6

# IA Providers
openai==1.10.0              # Cliente oficial OpenAI
openrouter==0.3.0           # ⭐ OpenRouter para multi-provider
anthropic==0.18.0           # Opcional: Claude directo

# Google Cloud
google-cloud-vision==3.5.0
google-auth==2.26.0
google-api-python-client==2.116.0

# Document generation
python-docx==1.1.0

# Utils
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.26.0
structlog==24.1.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

### Frontend

```yaml
Lenguaje: TypeScript 5.3+
Framework: React 18.3
Build: Vite 5.0
UI: shadcn/ui + Tailwind CSS 3.4
State: Zustand 4.5 + TanStack Query 5.0
Forms: React Hook Form + Zod
Routing: React Router 6.22
Testing: Vitest + React Testing Library
```

**Dependencias clave**:
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.22.0",

    "@tanstack/react-query": "^5.28.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.7",

    "react-hook-form": "^7.51.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4",

    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-progress": "^1.0.3",
    "tailwindcss": "^3.4.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1",

    "react-dropzone": "^14.2.3",
    "lucide-react": "^0.344.0"
  }
}
```

### Infraestructura

```yaml
Deployment: Coolify (self-hosted)
Container: Docker + Docker Compose
Reverse Proxy: Traefik (incluido en Coolify)
SSL: Let's Encrypt (automático)
CI/CD: GitHub Actions
Monitoring: Sentry (opcional)
Logs: Estructurados (JSON)
```

### Servicios Externos

```yaml
OCR: Google Cloud Vision API
AI Primary: OpenRouter (multi-provider)
  - OpenAI GPT-4o
  - Anthropic Claude 3.5 Sonnet
  - Google Gemini Pro
  - Meta Llama 3
AI Fallback: OpenAI directo (si OpenRouter falla)
Email: SMTP Gmail (App Password)
Storage: Local → Migrar a Supabase Storage en Fase 2
```

---

## 🏛️ ARQUITECTURA

### Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TS)                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Pages                                                   │  │
│  │  - ProcessPage (3 estados: upload, edit, completed)    │  │
│  │  - HomePage                                             │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Components                                              │  │
│  │  ✅ CategorizedUploader (Tabs: Parte A/B/Otros)        │  │
│  │  ✅ TemplateSelector (con auto-detect tipo)            │  │
│  │  ✅ DataEditor (agrupado por categorías)               │  │
│  │  ✅ DocumentPreview                                     │  │
│  │  ✅ EmailForm                                           │  │
│  │  ✅ ProgressIndicator                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ State Management (Zustand)                             │  │
│  │  - documentStore (extracted_data, edited_data)         │  │
│  │  - categoryStore (categorized_files)                   │  │
│  │  - templateStore (selected_template, placeholders)     │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────┘
                        │ HTTP/JSON (Axios)
                        ↓
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Endpoints (v1)                                      │  │
│  │  POST /api/v1/process-categorized                      │  │
│  │  POST /api/v1/generate                                 │  │
│  │  GET  /api/v1/templates                                │  │
│  │  GET  /api/v1/categories/{doc_type}                    │  │
│  │  GET  /api/v1/document-types                           │  │
│  │  POST /api/v1/send-email                               │  │
│  │  GET  /api/v1/health                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Services (Business Logic)                              │  │
│  │  ✅ OCRService (paralelo + categorizado)              │  │
│  │  ✅ AIService (OpenRouter + OpenAI fallback)          │  │
│  │  ✅ DocumentService (Word + formato preservado)        │  │
│  │  ✅ CategorizationService (tipos + categorías)         │  │
│  │  ✅ TemplateService (placeholders + mapping)           │  │
│  │  ✅ ClassificationService (auto-detect tipo)           │  │
│  │  ✅ EmailService (SMTP async)                          │  │
│  │  ✅ StorageService (local files)                       │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Data Models (Pydantic)                                 │  │
│  │  ✅ BaseKeys (CLAVES_COMUNES - 5 campos)              │  │
│  │  ✅ CompraventaKeys (42 campos)                        │  │
│  │  ✅ DonacionKeys (42 campos)                           │  │
│  │  ✅ TestamentoKeys (15 campos)                         │  │
│  │  ✅ PoderKeys (15 campos)                              │  │
│  │  ✅ SociedadKeys (15 campos)                           │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Storage (MVP: Archivos + JSON)                        │  │
│  │  📁 uploads/ → Imágenes temporales                     │  │
│  │  📁 outputs/ → Documentos generados                    │  │
│  │  📁 templates/ → Plantillas .docx                      │  │
│  │  📄 data/categories.json → Def. categorías             │  │
│  │  📄 data/document_types.json → Tipos + claves          │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ↓
┌──────────────────────────────────────────────────────────────┐
│                  SERVICIOS EXTERNOS                           │
│  🔍 Google Cloud Vision (OCR)                                │
│  🤖 OpenRouter (AI multi-provider)                           │
│     ├─ OpenAI GPT-4o                                         │
│     ├─ Anthropic Claude 3.5 Sonnet                           │
│     ├─ Google Gemini Pro                                     │
│     └─ Meta Llama 3                                          │
│  📧 Gmail SMTP (Email)                                       │
└──────────────────────────────────────────────────────────────┘
```

### Flujo de Procesamiento

```
1. UPLOAD (Estado: upload)
   ↓
   Usuario selecciona plantilla
   → Sistema extrae placeholders
   → Auto-detecta tipo de documento
   → Muestra categorías correspondientes (Parte A/B/Otros)
   ↓
   Usuario sube imágenes por categoría
   → Preview de imágenes categorizadas
   → Click "Extraer Datos"
   ↓

2. PROCESAMIENTO
   ↓
   A. OCR Categorizado (Paralelo)
      → Procesa todas las imágenes simultáneamente
      → Agrupa por categoría con headers
      → Combina texto extraído
      → Genera processing_details por categoría
   ↓
   B. Extracción IA (OpenRouter/OpenAI)
      → Envía texto + instrucciones de claves
      → Recibe datos estructurados en JSON
      → Valida campos
   ↓
   C. Transición a Estado 'edit'
   ↓

3. EDICIÓN (Estado: edit)
   ↓
   Muestra métricas:
   → Total placeholders
   → Campos encontrados
   → Porcentaje de completitud
   ↓
   Editor dinámico por categorías:
   → Agrupa campos relacionados
   → Permite editar cada campo
   → Guarda en edited_data
   ↓
   Usuario click "Generar Documento"
   ↓

4. GENERACIÓN
   ↓
   A. Formateo de datos
      → Aplica formato **negrita** a valores
      → Reemplaza "No encontrado" con placeholder
   ↓
   B. Generación Word
      → Reemplaza placeholders en párrafos
      → Reemplaza en tablas
      → Reemplaza en headers/footers
      → Aplica formato de negritas
   ↓
   C. Transición a Estado 'completed'
   ↓

5. COMPLETADO (Estado: completed)
   ↓
   Muestra opciones:
   → Descargar documento .docx
   → Enviar por email (opcional)
   → Procesar nuevos documentos (reset)
```

---

## 📁 ESTRUCTURA DE CARPETAS

```
controlnot-v2/
│
├── README.md                           # Documentación principal
├── .gitignore                          # Git ignore
├── .env.example                        # Template de variables
├── docker-compose.yml                  # Para Coolify
│
├── docs/
│   ├── MVP_PLAN_COMPLETO.md            # ⭐ Este documento
│   ├── API_REFERENCE.md                # Documentación API
│   ├── DEPLOYMENT_COOLIFY.md           # Guía deploy Coolify
│   ├── OPENROUTER_GUIDE.md             # ⭐ Guía OpenRouter
│   ├── MIGRATION_TO_DB.md              # Plan migración DB (Fase 2)
│   └── CHANGELOG.md                    # Historial cambios
│
├── backend/                            # 🐍 Python FastAPI
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry point
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # Settings (env vars)
│   │   │   ├── dependencies.py         # Dependency Injection
│   │   │   └── exceptions.py           # Custom exceptions
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py           # Main router v1
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── health.py       # GET /health
│   │   │           ├── documents.py    # POST /process-categorized, /generate
│   │   │           ├── templates.py    # GET /templates, /templates/{id}
│   │   │           ├── categories.py   # GET /categories/{doc_type}
│   │   │           ├── email.py        # POST /send-email
│   │   │           └── types.py        # GET /document-types
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # BaseKeys (CLAVES_COMUNES)
│   │   │   ├── compraventa.py          # CompraventaKeys (42 campos)
│   │   │   ├── donacion.py             # DonacionKeys (42 campos)
│   │   │   ├── testamento.py           # TestamentoKeys (15 campos)
│   │   │   ├── poder.py                # PoderKeys (15 campos)
│   │   │   └── sociedad.py             # SociedadKeys (15 campos)
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── requests.py             # Request DTOs
│   │   │   ├── responses.py            # Response DTOs
│   │   │   └── category.py             # Category schemas
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py          # ✅ OCR + categorización
│   │   │   ├── ai_service.py           # ✅ OpenRouter + OpenAI
│   │   │   ├── document_service.py     # ✅ Word generation
│   │   │   ├── template_service.py     # ✅ Placeholders parsing
│   │   │   ├── categorization_service.py # ✅ Categorías por tipo
│   │   │   ├── classification_service.py # ✅ Auto-detect tipo
│   │   │   ├── storage_service.py      # ✅ File storage local
│   │   │   └── email_service.py        # ✅ SMTP email
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py               # Structured logging
│   │       └── validators.py           # Custom validators
│   │
│   ├── data/                           # ⭐ JSON storage (MVP)
│   │   ├── categories.json             # Categorías por tipo doc
│   │   ├── document_types.json         # TIPOS_DOCUMENTO
│   │   └── templates_metadata.json     # Metadata de plantillas
│   │
│   ├── uploads/                        # ⭐ Imágenes temp (gitignore)
│   ├── outputs/                        # ⭐ Docs generados (gitignore)
│   ├── templates/                      # ⭐ Plantillas .docx
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_ocr_service.py
│   │   │   ├── test_ai_service.py
│   │   │   ├── test_categorization.py
│   │   │   └── test_document_service.py
│   │   ├── integration/
│   │   │   ├── test_api_documents.py
│   │   │   └── test_categorized_flow.py
│   │   └── e2e/
│   │       └── test_complete_workflow.py
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   ├── pytest.ini
│   └── README.md
│
├── frontend/                           # ⚛️ React TypeScript
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── robots.txt
│   │
│   ├── src/
│   │   ├── main.tsx                    # Entry point
│   │   ├── App.tsx                     # App component
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── pages/
│   │   │   ├── ProcessPage.tsx         # ✅ Página principal (3 estados)
│   │   │   └── HomePage.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   ├── CategorizedUploader.tsx  # ✅ Tabs por categoría
│   │   │   │   ├── CategoryTab.tsx
│   │   │   │   ├── DropZone.tsx
│   │   │   │   └── ImagePreview.tsx
│   │   │   │
│   │   │   ├── templates/
│   │   │   │   ├── TemplateSelector.tsx     # ✅ Selector con tipos
│   │   │   │   ├── TemplateCard.tsx
│   │   │   │   └── TypeBadge.tsx
│   │   │   │
│   │   │   ├── editor/
│   │   │   │   ├── DataEditor.tsx           # ✅ Editor dinámico
│   │   │   │   ├── FieldGroup.tsx
│   │   │   │   └── CategorySection.tsx
│   │   │   │
│   │   │   ├── document/
│   │   │   │   ├── PreviewModal.tsx
│   │   │   │   ├── DownloadButton.tsx
│   │   │   │   └── EmailForm.tsx            # ✅ Form email
│   │   │   │
│   │   │   ├── progress/
│   │   │   │   ├── ProgressIndicator.tsx    # ✅ Barra progreso
│   │   │   │   └── ProcessingDetails.tsx    # ✅ Stats por categoría
│   │   │   │
│   │   │   └── ui/                          # shadcn/ui
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── tabs.tsx                 # ⭐ Para categorías
│   │   │       ├── progress.tsx
│   │   │       ├── form.tsx
│   │   │       ├── input.tsx
│   │   │       └── select.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                       # Axios client
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── useProcessDocument.ts
│   │   │   ├── useTemplates.ts
│   │   │   └── useCategories.ts
│   │   │
│   │   ├── store/
│   │   │   ├── documentStore.ts             # Zustand
│   │   │   ├── categoryStore.ts             # ⭐ Categorías
│   │   │   └── templateStore.ts
│   │   │
│   │   ├── types/
│   │   │   ├── document.ts
│   │   │   ├── category.ts
│   │   │   └── template.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css                  # ✅ CSS personalizado
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .eslintrc.cjs
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
└── .github/
    └── workflows/
        ├── backend-test.yml            # CI backend
        ├── frontend-test.yml           # CI frontend
        └── deploy.yml                  # Deploy a Coolify
```

---

## 📊 MODELOS DE DATOS

### Archivo: `backend/data/document_types.json`

Migración directa de `TIPOS_DOCUMENTO` de por_partes.py:

```json
{
  "compraventa": {
    "nombre": "Compraventa",
    "descripcion": "Contrato de compraventa de inmueble",
    "claves": {
      "fecha_instrumento": "Fecha del día en que se firma el instrumento (formato completo en palabras)",
      "lugar_instrumento": "Ciudad y estado donde se firma el instrumento",
      "numero_instrumento": "Número del instrumento notarial en palabras",
      "notario_actuante": "Nombre completo del notario que autoriza el acto",
      "numero_notaria": "Número de la notaría en palabras",

      "Parte_Vendedora_Nombre_Completo": "NOMBRES Y APELLIDOS EN MAYÚSCULAS del vendedor...",
      "Parte_Compradora_Nombre_Completo": "NOMBRES Y APELLIDOS EN MAYÚSCULAS del comprador...",
      ...
    }
  },
  "donacion": {
    "nombre": "Donación",
    "descripcion": "Acto de donación de inmueble",
    "claves": { ... }
  },
  "testamento": {
    "nombre": "Testamento",
    "descripcion": "Testamento notarial",
    "claves": { ... }
  },
  "poder": {
    "nombre": "Poder Notarial",
    "descripcion": "Poder general o especial",
    "claves": { ... }
  },
  "sociedad": {
    "nombre": "Constitución de Sociedad",
    "descripcion": "Acta constitutiva de sociedad",
    "claves": { ... }
  }
}
```

### Archivo: `backend/data/categories.json`

Migración directa de `categorize_documents_by_role()`:

```json
{
  "compraventa": {
    "parte_a": {
      "nombre": "Documentos del Vendedor",
      "icono": "📤",
      "descripcion": "Documentos de identificación y propiedad del vendedor",
      "documentos": [
        "INE/IFE del Vendedor",
        "Acta de Nacimiento del Vendedor",
        "CURP del Vendedor",
        "RFC/Constancia SAT del Vendedor",
        "Comprobante de Domicilio del Vendedor",
        "Acta de Matrimonio del Vendedor (si aplica)"
      ]
    },
    "parte_b": {
      "nombre": "Documentos del Comprador",
      "icono": "📥",
      "descripcion": "Documentos de identificación del comprador",
      "documentos": [
        "INE/IFE del Comprador",
        "Acta de Nacimiento del Comprador",
        "CURP del Comprador",
        "RFC/Constancia SAT del Comprador",
        "Comprobante de Domicilio del Comprador",
        "Acta de Matrimonio del Comprador (si aplica)"
      ]
    },
    "otros": {
      "nombre": "Documentos del Inmueble y Antecedentes",
      "icono": "📋",
      "descripcion": "Documentación legal del inmueble",
      "documentos": [
        "Escritura o Contrato Antecedente",
        "Certificado Catastral",
        "Constancia de No Adeudo Predial",
        "Boleta del Registro Público",
        "Avalúo del Inmueble",
        "Planos y Medidas"
      ]
    }
  },
  "donacion": {
    "parte_a": {
      "nombre": "Documentos del Donador",
      "icono": "🎁",
      ...
    },
    "parte_b": {
      "nombre": "Documentos del Donatario",
      "icono": "🎉",
      ...
    },
    "otros": { ... }
  },
  ...
}
```

### Modelos Pydantic

**backend/app/models/base.py**:

```python
from pydantic import BaseModel, Field
from typing import Optional

class BaseKeys(BaseModel):
    """Claves comunes a todos los documentos (CLAVES_COMUNES)"""

    fecha_instrumento: Optional[str] = Field(
        None,
        description="Fecha del día en que se firma el instrumento (formato completo en palabras)"
    )
    lugar_instrumento: Optional[str] = Field(
        None,
        description="Ciudad y estado donde se firma el instrumento"
    )
    numero_instrumento: Optional[str] = Field(
        None,
        description="Número del instrumento notarial en palabras"
    )
    notario_actuante: Optional[str] = Field(
        None,
        description="Nombre completo del notario que autoriza el acto"
    )
    numero_notaria: Optional[str] = Field(
        None,
        description="Número de la notaría en palabras"
    )
```

**backend/app/models/compraventa.py**:

```python
from pydantic import Field
from typing import Optional
from .base import BaseKeys

class CompraventaKeys(BaseKeys):
    """Claves específicas de Compraventa (42 campos + 5 comunes)"""

    Parte_Vendedora_Nombre_Completo: Optional[str] = Field(
        None,
        description="""
        ===IDENTIFICAR AL VENDEDOR (PROPIETARIO ACTUAL)===

        FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
        Ejemplo: RAUL CERVANTES AREVALO

        El VENDEDOR es quien ACTUALMENTE posee el inmueble y lo está vendiendo.

        BUSCAR ÚNICAMENTE EN DOCUMENTOS DE PROPIEDAD ACTUAL:
        ...
        """
    )

    Parte_Compradora_Nombre_Completo: Optional[str] = Field(...)
    Tratamiento_Vendedor: Optional[str] = Field(...)
    Tratamiento_Comprador: Optional[str] = Field(...)

    # ... resto de 42 campos con sus descripciones detalladas
```

**Archivos similares**:
- `donacion.py` (DonacionKeys)
- `testamento.py` (TestamentoKeys)
- `poder.py` (PoderKeys)
- `sociedad.py` (SociedadKeys)

---

## 🔧 SERVICIOS CORE

### 1. CategorizationService

**Archivo**: `backend/app/services/categorization_service.py`

```python
"""
Servicio de categorización de documentos
Migrado de: categorize_documents_by_role() (líneas 1959-2182)
"""

from typing import Dict, List
import json
from pathlib import Path
from ..core.config import settings

class CategorizationService:
    """
    Gestiona las categorías de documentos por tipo.
    Cada tipo de documento tiene 3 categorías: parte_a, parte_b, otros
    """

    def __init__(self):
        self.categories_file = Path(settings.DATA_DIR) / "categories.json"
        self._load_categories()

    def _load_categories(self):
        """Carga categorías desde JSON"""
        if not self.categories_file.exists():
            self._create_default_categories()

        with open(self.categories_file, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

    def _create_default_categories(self):
        """
        Crea archivo con categorías por defecto
        Migración exacta de categorize_documents_by_role()
        """
        default_categories = {
            "compraventa": {
                "parte_a": {
                    "nombre": "Documentos del Vendedor",
                    "icono": "📤",
                    "descripcion": "Documentos de identificación y propiedad del vendedor",
                    "documentos": [
                        "INE/IFE del Vendedor",
                        "Acta de Nacimiento del Vendedor",
                        "CURP del Vendedor",
                        "RFC/Constancia SAT del Vendedor",
                        "Comprobante de Domicilio del Vendedor",
                        "Acta de Matrimonio del Vendedor (si aplica)"
                    ]
                },
                # ... resto de categorías
            },
            # ... resto de tipos
        }

        self.categories_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(default_categories, f, ensure_ascii=False, indent=2)

        self.categories = default_categories

    def get_categories_for_type(self, document_type: str) -> Dict:
        """
        Obtiene categorías para un tipo de documento

        Args:
            document_type: 'compraventa', 'donacion', etc.

        Returns:
            Dict con estructura {parte_a: {...}, parte_b: {...}, otros: {...}}
        """
        return self.categories.get(document_type, self._get_generic_categories())

    def _get_generic_categories(self) -> Dict:
        """Categorías genéricas para tipos no definidos"""
        return {
            "parte_a": {
                "nombre": "Documentos Parte A",
                "icono": "📄",
                "descripcion": "Documentos de la primera parte",
                "documentos": ["Documentos de identificación"]
            },
            "parte_b": {
                "nombre": "Documentos Parte B",
                "icono": "📄",
                "descripcion": "Documentos de la segunda parte",
                "documentos": ["Documentos de identificación"]
            },
            "otros": {
                "nombre": "Otros Documentos",
                "icono": "📋",
                "descripcion": "Documentación adicional",
                "documentos": ["Documentos adicionales"]
            }
        }

    def get_all_types(self) -> List[str]:
        """Lista todos los tipos de documentos disponibles"""
        return list(self.categories.keys())

    def validate_categorized_upload(
        self,
        categorized_files: Dict[str, List],
        document_type: str
    ) -> Dict:
        """
        Valida que los archivos categorizados sean correctos

        Returns:
            Dict con {valid: bool, errors: List[str]}
        """
        errors = []
        categories = self.get_categories_for_type(document_type)

        for category_key in categorized_files.keys():
            if category_key not in categories:
                errors.append(f"Categoría inválida: {category_key}")

        total_files = sum(len(files) for files in categorized_files.values())
        if total_files == 0:
            errors.append("No se subieron archivos")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_files": total_files
        }
```

### 2. OCRService (con Categorización)

**Archivo**: `backend/app/services/ocr_service.py`

```python
"""
Servicio de OCR con soporte para procesamiento categorizado
Migrado de:
  - detect_text() (línea 1856)
  - process_categorized_documents() (línea 2293)

MEJORA: Procesamiento paralelo async (5-10x más rápido)
"""

import asyncio
from typing import Dict, List, Tuple
from google.cloud import vision
from google.oauth2 import service_account
import structlog
from ..core.config import settings
from .categorization_service import CategorizationService

logger = structlog.get_logger()

class OCRService:
    """Servicio OCR con procesamiento categorizado paralelo"""

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            settings.google_credentials_dict
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
        self.categorization_service = CategorizationService()

    async def detect_text(self, image_content: bytes) -> str:
        """
        Extrae texto de una imagen usando Google Cloud Vision

        Migrado de: detect_text() línea 1856

        Args:
            image_content: Contenido de la imagen en bytes

        Returns:
            Texto extraído

        Raises:
            Exception: Si hay error en OCR
        """
        try:
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)

            if response.error.message:
                raise Exception(f"Google Vision Error: {response.error.message}")

            if response.text_annotations:
                extracted_text = response.text_annotations[0].description
                logger.info(
                    "ocr_success",
                    chars_extracted=len(extracted_text)
                )
                return extracted_text

            logger.warning("ocr_no_text_found")
            return ""

        except Exception as e:
            logger.error("ocr_error", error=str(e))
            raise Exception(f"OCR Error: {str(e)}")

    async def process_categorized_images(
        self,
        categorized_files: Dict[str, List[bytes]],
        document_type: str
    ) -> Dict:
        """
        Procesa imágenes categorizadas en PARALELO

        Migrado de: process_categorized_documents() línea 2293

        MEJORA CRÍTICA: Procesamiento paralelo con asyncio
        - Versión original: Secuencial (60s para 10 imágenes)
        - Nueva versión: Paralelo (6-8s para 10 imágenes)

        Args:
            categorized_files: {
                'parte_a': [bytes, bytes, ...],
                'parte_b': [bytes, ...],
                'otros': [bytes, ...]
            }
            document_type: Tipo de documento

        Returns:
            {
                'extracted_text': str,  # Texto combinado con headers
                'processing_details': {
                    'parte_a': {'count': int, 'text': str},
                    'parte_b': {'count': int, 'text': str},
                    'otros': {'count': int, 'text': str}
                },
                'total_processed': int
            }
        """
        all_extracted_text = ""
        processing_details = {
            'parte_a': {'count': 0, 'text': ""},
            'parte_b': {'count': 0, 'text': ""},
            'otros': {'count': 0, 'text': ""}
        }

        categories = self.categorization_service.get_categories_for_type(document_type)

        logger.info(
            "starting_categorized_ocr",
            document_type=document_type,
            total_files=sum(len(files) for files in categorized_files.values())
        )

        for category_key, image_contents in categorized_files.items():
            if not image_contents:
                continue

            category = categories.get(category_key, {})

            # ⭐ HEADER DE CATEGORÍA (como en por_partes.py)
            category_header = f"\n\n{'='*80}\n"
            category_header += f"CATEGORÍA: {category.get('nombre', '').upper()}\n"
            category_header += f"{'='*80}\n\n"

            all_extracted_text += category_header
            processing_details[category_key]['text'] = category_header

            # ⭐ PROCESAMIENTO PARALELO (5-10x más rápido)
            tasks = [
                self.detect_text(img_content)
                for img_content in image_contents
            ]

            logger.info(
                "processing_category",
                category=category_key,
                images=len(tasks)
            )

            # Ejecutar todas las tareas en paralelo
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    error_text = f"\n[ERROR documento {i}]: {str(result)}\n"
                    all_extracted_text += error_text
                    processing_details[category_key]['text'] += error_text
                    logger.error(
                        "ocr_document_failed",
                        category=category_key,
                        document_index=i,
                        error=str(result)
                    )
                else:
                    doc_text = f"\n--- DOCUMENTO {i}: {category.get('nombre', '')} ---\n\n{result}\n"
                    all_extracted_text += doc_text
                    processing_details[category_key]['text'] += doc_text
                    processing_details[category_key]['count'] += 1
                    logger.debug(
                        "ocr_document_success",
                        category=category_key,
                        document_index=i,
                        chars=len(result)
                    )

        total_processed = sum(d['count'] for d in processing_details.values())

        logger.info(
            "categorized_ocr_complete",
            total_processed=total_processed,
            total_chars=len(all_extracted_text)
        )

        return {
            "extracted_text": all_extracted_text,
            "processing_details": processing_details,
            "total_processed": total_processed
        }
```

### 3. AIService (OpenRouter + OpenAI)

**Archivo**: `backend/app/services/ai_service.py`

```python
"""
Servicio de extracción inteligente con IA
Migrado de: process_text_with_openai_dynamic() línea 1745

MEJORA: Soporte multi-provider vía OpenRouter
"""

from openai import OpenAI
from typing import Dict, Optional
import json
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class AIService:
    """Servicio de extracción de datos con IA (OpenRouter + OpenAI)"""

    def __init__(self):
        # ⭐ OPENROUTER CLIENT (compatible con sintaxis OpenAI)
        self.openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY
        )

        # Fallback a OpenAI directo
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.document_types_file = settings.DATA_DIR / "document_types.json"
        self._load_document_types()

    def _load_document_types(self):
        """Carga tipos de documento y sus claves desde JSON"""
        with open(self.document_types_file, 'r', encoding='utf-8') as f:
            self.document_types = json.load(f)

    def get_relevant_keys(self, document_type: str) -> Dict:
        """
        Obtiene claves relevantes para un tipo de documento
        Migrado de: get_relevant_keys() línea 1418
        """
        if document_type in self.document_types:
            return self.document_types[document_type]["claves"]

        # Fallback a compraventa si tipo no existe
        return self.document_types["compraventa"]["claves"]

    async def extract_data(
        self,
        extracted_text: str,
        document_type: str,
        provider: str = "auto"
    ) -> Dict[str, str]:
        """
        Extrae datos estructurados del texto usando IA

        Migrado de: process_text_with_openai_dynamic() línea 1745

        MEJORA: Multi-provider support

        Args:
            extracted_text: Texto extraído por OCR
            document_type: Tipo de documento
            provider: 'openrouter', 'openai', or 'auto'

        Returns:
            Dict {campo: valor, ...}
        """
        relevant_keys = self.get_relevant_keys(document_type)
        doc_name = self.document_types[document_type]["nombre"]

        logger.info(
            "ai_extraction_start",
            document_type=document_type,
            text_length=len(extracted_text),
            keys_count=len(relevant_keys),
            provider=provider
        )

        # Construir prompt optimizado
        system_prompt = self._build_system_prompt(relevant_keys, doc_name)
        user_prompt = f"Extrae JSON del texto de {doc_name}:\n\n{extracted_text}"

        # Intentar con provider preferido
        try:
            if provider == "openrouter" or provider == "auto":
                return await self._extract_with_openrouter(
                    system_prompt,
                    user_prompt,
                    doc_name
                )
        except Exception as e:
            logger.warning(
                "openrouter_failed_fallback_to_openai",
                error=str(e)
            )

        # Fallback a OpenAI
        return await self._extract_with_openai(
            system_prompt,
            user_prompt,
            doc_name
        )

    async def _extract_with_openrouter(
        self,
        system_prompt: str,
        user_prompt: str,
        doc_name: str
    ) -> Dict[str, str]:
        """
        Extrae usando OpenRouter (multi-provider)

        Providers disponibles:
        - openai/gpt-4o
        - anthropic/claude-3.5-sonnet
        - google/gemini-pro-1.5
        - meta-llama/llama-3-70b-instruct
        """
        try:
            response = self.openrouter_client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,  # ej: "openai/gpt-4o"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=3000,
                # ⭐ OpenRouter extras
                extra_headers={
                    "HTTP-Referer": settings.APP_URL,
                    "X-Title": "ControlNot v2"
                }
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            logger.info(
                "openrouter_extraction_success",
                model=settings.OPENROUTER_MODEL,
                fields_extracted=len(result)
            )

            return result

        except Exception as e:
            logger.error(
                "openrouter_extraction_failed",
                error=str(e)
            )
            raise

    async def _extract_with_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        doc_name: str
    ) -> Dict[str, str]:
        """
        Extrae usando OpenAI directo (fallback)

        Migración directa de process_text_with_openai_dynamic()
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            logger.info(
                "openai_extraction_success",
                fields_extracted=len(result)
            )

            return result

        except Exception as e:
            logger.error(
                "openai_extraction_failed",
                error=str(e)
            )
            raise Exception(f"AI Extraction Error: {str(e)}")

    def _build_system_prompt(self, keys: Dict, doc_name: str) -> str:
        """
        Construye prompt del sistema

        MEJORA: 40% menos tokens que versión original
        """
        system_message = f"Eres controlnot, asistente de notaría para {doc_name}. "
        system_message += "Extrae información en JSON según estas claves:\n\n"
        system_message += json.dumps(keys, indent=2, ensure_ascii=False)
        system_message += "\n\nRespuesta: JSON válido con las claves encontradas."

        return system_message
```

---

## 🤖 OPENROUTER INTEGRATION

### ¿Qué es OpenRouter?

**OpenRouter** es un proxy unificado que te permite acceder a múltiples proveedores de IA (OpenAI, Anthropic, Google, Meta, etc.) con una sola API compatible con OpenAI.

### Ventajas

✅ **Sintaxis compatible con OpenAI**: Mismo código, múltiples providers
✅ **Failover automático**: Si un provider falla, cambia a otro
✅ **Precios competitivos**: Encuentra el mejor precio por modelo
✅ **Rate limiting inteligente**: Distribuye requests entre providers
✅ **Sin vendor lock-in**: Cambia de provider sin cambiar código

### Providers Disponibles

| Provider | Modelo | Precio (input/output) | Velocidad |
|----------|--------|-----------------------|-----------|
| OpenAI | gpt-4o | $2.50/$10 per 1M tokens | Rápido |
| Anthropic | claude-3.5-sonnet | $3/$15 per 1M tokens | Rápido |
| Google | gemini-pro-1.5 | $1.25/$5 per 1M tokens | Muy rápido |
| Meta | llama-3-70b | $0.70/$0.90 per 1M tokens | Ultra rápido |

### Configuración

**1. Crear cuenta en OpenRouter**:
```bash
# Ir a: https://openrouter.ai/
# Crear cuenta y obtener API key
```

**2. Configurar .env**:
```bash
# OpenRouter (preferido)
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=openai/gpt-4o  # o anthropic/claude-3.5-sonnet

# OpenAI (fallback)
OPENAI_API_KEY=sk-proj-xxx

# App info (para OpenRouter stats)
APP_URL=https://controlnot.tudominio.com
```

**3. Uso en código** (ya incluido en AIService):

```python
from openai import OpenAI

# Cliente OpenRouter (sintaxis OpenAI)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Llamada idéntica a OpenAI
response = client.chat.completions.create(
    model="openai/gpt-4o",  # o cualquier otro modelo
    messages=[
        {"role": "system", "content": "Eres un asistente..."},
        {"role": "user", "content": "Pregunta..."}
    ],
    temperature=0.1,
    extra_headers={  # Opcional: para tracking en OpenRouter
        "HTTP-Referer": "https://tuapp.com",
        "X-Title": "ControlNot"
    }
)
```

### Modelos Recomendados por Caso de Uso

| Caso de Uso | Modelo Recomendado | Por qué |
|-------------|-------------------|---------|
| **Producción (precisión)** | `openai/gpt-4o` | Mejor precisión en español |
| **Producción (costo)** | `google/gemini-pro-1.5` | 50% más barato, buena precisión |
| **Desarrollo/Testing** | `meta-llama/llama-3-70b` | 70% más barato |
| **Fallback** | `anthropic/claude-3.5-sonnet` | Excelente en español |

### Estrategia de Failover

```python
# En AIService.extract_data()

providers_cascade = [
    ("openrouter", settings.OPENROUTER_MODEL),
    ("openai", "gpt-4o"),
    ("openrouter", "anthropic/claude-3.5-sonnet"),  # Fallback 2
]

for provider, model in providers_cascade:
    try:
        return await extract_with_provider(provider, model)
    except Exception as e:
        logger.warning(f"{provider} failed, trying next...")
        continue

raise Exception("All providers failed")
```

---

## 🚀 ROADMAP 4 SEMANAS

### ⚠️ DÍA 0: URGENTE - Seguridad (4 horas)

**ANTES DE EMPEZAR**: Rotar credenciales expuestas en `por_partes.py`

```bash
# 1. Generar nuevas credenciales
OpenAI: https://platform.openai.com/api-keys
Google Cloud: https://console.cloud.google.com/iam-admin/serviceaccounts
OpenRouter: https://openrouter.ai/keys
Gmail: https://myaccount.google.com/apppasswords

# 2. Crear .env
OPENAI_API_KEY=sk-proj-NUEVA_KEY
OPENROUTER_API_KEY=sk-or-v1-NUEVA_KEY
OPENROUTER_MODEL=openai/gpt-4o
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
SMTP_EMAIL=email@gmail.com
SMTP_PASSWORD=nueva_app_password

# 3. Asegurar .gitignore
echo ".env" >> .gitignore
echo "backend/uploads/" >> .gitignore
echo "backend/outputs/" >> .gitignore
```

---

### 📦 SEMANA 1: Backend Core (40 horas)

#### Día 1-2: Setup + Estructura (16h)

**Crear proyecto**:

```bash
mkdir controlnot-v2
cd controlnot-v2
git init

# Backend
mkdir -p backend/app/{api/v1/endpoints,core,models,schemas,services,utils}
mkdir -p backend/{data,uploads,outputs,templates,tests}

# Crear __init__.py en todos los paquetes
find backend/app -type d -exec touch {}/__init__.py \;

# Frontend (en paralelo si hay 2 devs)
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install && cd ..

# Git inicial
git add .gitignore
git commit -m "Initial structure"
```

**backend/requirements.txt**:

```txt
# Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# AI Providers
openai==1.10.0
anthropic==0.18.0          # Opcional

# Google Cloud
google-cloud-vision==3.5.0
google-auth==2.26.0
google-api-python-client==2.116.0

# Document generation
python-docx==1.1.0

# Utils
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.26.0
structlog==24.1.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

**backend/app/main.py**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="ControlNot API",
    version="2.0.0",
    description="Sistema de procesamiento documental notarial con IA"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "google_vision": "ok",
            "openrouter": "ok",
            "openai": "ok"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**backend/app/core/config.py**:

```python
from pydantic_settings import BaseSettings
from typing import List
import json
from pathlib import Path

class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "ControlNot API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    # Google Cloud
    GOOGLE_CREDENTIALS_JSON: str
    GOOGLE_DRIVE_FOLDER_ID: str = ""

    # AI Providers
    OPENAI_API_KEY: str
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-4o"

    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    # Storage (MVP: local)
    UPLOAD_DIR: Path = Path("./uploads")
    OUTPUT_DIR: Path = Path("./outputs")
    TEMPLATE_DIR: Path = Path("./templates")
    DATA_DIR: Path = Path("./data")

    # App
    APP_URL: str = "http://localhost:3000"

    @property
    def google_credentials_dict(self):
        return json.loads(self.GOOGLE_CREDENTIALS_JSON)

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Crear directorios si no existen
for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR,
                  settings.TEMPLATE_DIR, settings.DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
```

#### Día 3-5: Servicios Core (24h)

**Implementar**:
1. ✅ CategorizationService (6h) - Ver sección "Servicios Core" arriba
2. ✅ OCRService (8h) - Ver sección "Servicios Core" arriba
3. ✅ AIService con OpenRouter (10h) - Ver sección "Servicios Core" arriba

**Crear archivos JSON de datos**:

```bash
# backend/data/document_types.json
# Copiar estructura de TIPOS_DOCUMENTO de por_partes.py

# backend/data/categories.json
# Copiar estructura de categorize_documents_by_role()
```

---

### ⚛️ SEMANA 2: Frontend React (40 horas)

#### Día 1: Setup (8h)

```bash
cd frontend
npm install

# UI Dependencies
npm install @radix-ui/react-tabs @radix-ui/react-progress
npm install tailwindcss postcss autoprefixer
npm install clsx tailwind-merge lucide-react

# State & API
npm install zustand @tanstack/react-query axios

# Forms
npm install react-hook-form zod @hookform/resolvers

# Utils
npm install react-dropzone

# Setup Tailwind
npx tailwindcss init -p

# Setup shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card tabs progress form input
```

**tailwind.config.js**:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1e3c72",
          dark: "#2a5298",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

**src/styles/globals.css** (Migrar CSS de por_partes.py):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-gray-50 font-[Inter] text-gray-900;
  }
}

@layer components {
  /* Migrar estilos de líneas 35-366 de por_partes.py */

  .main-header {
    @apply bg-gradient-to-r from-[#1e3c72] to-[#2a5298]
           p-6 rounded-xl mb-6 text-white text-center
           shadow-lg shadow-[rgba(30,60,114,0.3)];
  }

  .process-card {
    @apply bg-white rounded-xl p-4 shadow-md
           border border-gray-200 mb-4
           transition-all hover:-translate-y-0.5 hover:shadow-lg;
  }

  /* ... resto de estilos */
}
```

#### Día 2-3: Componentes Core (16h)

**src/components/upload/CategorizedUploader.tsx**:

```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card } from "@/components/ui/card"
import { CategoryTab } from "./CategoryTab"
import { useCategoryStore } from "@/store/categoryStore"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"

interface Category {
  nombre: string
  icono: string
  descripcion: string
  documentos: string[]
}

interface CategorizedUploaderProps {
  documentType: string
}

export function CategorizedUploader({ documentType }: CategorizedUploaderProps) {
  const { categorizedFiles, setCategoryFiles } = useCategoryStore()

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories', documentType],
    queryFn: () => api.getCategories(documentType),
  })

  if (isLoading) {
    return <div className="text-center p-8">Cargando categorías...</div>
  }

  if (!categories) {
    return null
  }

  const categoryKeys = Object.keys(categories)

  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-2">
        📁 Documentos por Categoría
      </h3>
      <p className="text-gray-600 mb-6">
        Organiza tus documentos para mejor procesamiento
      </p>

      <Tabs defaultValue={categoryKeys[0]} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {categoryKeys.map((key) => {
            const cat = categories[key]
            return (
              <TabsTrigger key={key} value={key} className="gap-2">
                <span>{cat.icono}</span>
                <span className="hidden sm:inline">{cat.nombre}</span>
              </TabsTrigger>
            )
          })}
        </TabsList>

        {categoryKeys.map((key) => {
          const cat = categories[key]
          return (
            <TabsContent key={key} value={key} className="mt-4">
              <CategoryTab
                category={cat}
                categoryKey={key}
                files={categorizedFiles[key] || []}
                onFilesChange={(files) => setCategoryFiles(key, files)}
              />
            </TabsContent>
          )
        })}
      </Tabs>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          Total de documentos: {
            Object.values(categorizedFiles).reduce(
              (sum, files) => sum + files.length,
              0
            )
          }
        </p>
      </div>
    </Card>
  )
}
```

**src/store/categoryStore.ts**:

```typescript
import { create } from 'zustand'

interface CategoryStore {
  categorizedFiles: Record<string, File[]>
  setCategoryFiles: (category: string, files: File[]) => void
  clearAll: () => void
  getTotalFiles: () => number
}

export const useCategoryStore = create<CategoryStore>((set, get) => ({
  categorizedFiles: {
    parte_a: [],
    parte_b: [],
    otros: []
  },

  setCategoryFiles: (category, files) => {
    set((state) => ({
      categorizedFiles: {
        ...state.categorizedFiles,
        [category]: files
      }
    }))
  },

  clearAll: () => {
    set({
      categorizedFiles: {
        parte_a: [],
        parte_b: [],
        otros: []
      }
    })
  },

  getTotalFiles: () => {
    const { categorizedFiles } = get()
    return Object.values(categorizedFiles)
      .reduce((sum, files) => sum + files.length, 0)
  }
}))
```

#### Día 4-5: Pages & Integration (16h)

**src/pages/ProcessPage.tsx** (Estados: upload, edit, completed):

```typescript
import { useState } from 'react'
import { CategorizedUploader } from '@/components/upload/CategorizedUploader'
import { DataEditor } from '@/components/editor/DataEditor'
import { DocumentComplete } from '@/components/document/DocumentComplete'
import { ProgressIndicator } from '@/components/progress/ProgressIndicator'
import { useProcessDocument } from '@/hooks/useProcessDocument'

type ProcessStage = 'upload' | 'edit' | 'completed'

export function ProcessPage() {
  const [stage, setStage] = useState<ProcessStage>('upload')
  const [documentType, setDocumentType] = useState('compraventa')
  const { processDocument, isProcessing } = useProcessDocument()

  const handleProcess = async () => {
    const result = await processDocument(documentType)
    if (result.success) {
      setStage('edit')
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="main-header mb-8">
        <h1 className="text-4xl font-bold">ControlNot</h1>
        <p className="mt-2 text-lg opacity-90">
          Asistente Inteligente con Organización por Categorías
        </p>
      </header>

      <ProgressIndicator currentStage={stage} />

      {stage === 'upload' && (
        <div className="space-y-6">
          <TemplateSelector
            onSelect={(template) => setDocumentType(template.type)}
          />

          <CategorizedUploader documentType={documentType} />

          <button
            onClick={handleProcess}
            disabled={isProcessing}
            className="btn-primary w-full"
          >
            {isProcessing ? 'Procesando...' : 'Extraer Datos'}
          </button>
        </div>
      )}

      {stage === 'edit' && (
        <DataEditor onGenerate={() => setStage('completed')} />
      )}

      {stage === 'completed' && (
        <DocumentComplete onReset={() => setStage('upload')} />
      )}
    </div>
  )
}
```

---

### 🔗 SEMANA 3: Integración E2E (40 horas)

- API endpoints completos
- Conectar Frontend ↔ Backend
- Tests de integración
- Manejo de errores completo
- Loading states y UX polish
- Validaciones de datos

---

### 🚀 SEMANA 4: Deploy + Docs (40 horas)

#### Docker Setup

**backend/Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Create directories
RUN mkdir -p uploads outputs templates data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile**:

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_MODEL=${OPENROUTER_MODEL}
      - GOOGLE_CREDENTIALS_JSON=${GOOGLE_CREDENTIALS_JSON}
      - SMTP_EMAIL=${SMTP_EMAIL}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/outputs:/app/outputs
      - ./backend/templates:/app/templates
      - ./backend/data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=${API_URL}
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 🌐 DEPLOY EN COOLIFY

### Configuración en Coolify

1. **Crear nueva aplicación**:
   - Tipo: Docker Compose
   - Repository: GitHub (controlnot-v2)
   - Branch: main

2. **Variables de entorno**:

```bash
# AI Providers
OPENAI_API_KEY=sk-proj-xxx
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=openai/gpt-4o

# Google Cloud
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Email
SMTP_EMAIL=email@gmail.com
SMTP_PASSWORD=app_password

# URLs
API_URL=https://api.controlnot.tudominio.com
APP_URL=https://controlnot.tudominio.com
```

3. **Dominios**:
   - Frontend: `controlnot.tudominio.com`
   - Backend: `api.controlnot.tudominio.com`

4. **SSL**: Automático via Let's Encrypt (Coolify lo maneja)

5. **Deploy**:
   - Push a `main` → Auto-deploy via webhook
   - Rollback: Click en versión anterior

---

## 🔄 MIGRACIÓN FUTURA A DB (Fase 2)

**Cuándo migrar**: >50 usuarios o >500 docs/mes

**Esfuerzo**: 2-3 semanas adicionales

**Cambios**:

1. Setup Supabase
2. Migrar JSON → PostgreSQL:
   ```sql
   CREATE TABLE documents (...);
   CREATE TABLE templates (...);
   CREATE TABLE users (...);
   ```
3. Implementar autenticación (Supabase Auth)
4. Migrar storage local → Supabase Storage
5. Agregar historial de documentos
6. Analytics y métricas

**Sin cambios en**:
- Servicios core (OCR, AI, Document)
- Componentes React
- API endpoints (solo cambiar repository layer)

---

## ✅ CRITERIOS DE ÉXITO MVP

- [ ] Sube imágenes por categoría (Parte A/B/Otros)
- [ ] Procesa OCR en paralelo (<10s para 10 imgs)
- [ ] Extrae datos con OpenRouter/OpenAI
- [ ] Genera documento Word con formato
- [ ] Frontend responsive (mobile + desktop)
- [ ] Deploy funcional en Coolify
- [ ] OpenRouter funcionando con fallback
- [ ] Documentación completa

---

## 📊 RESUMEN EJECUTIVO

### Inventario Completo Migrado

✅ **6 modelos de datos** (CLAVES_*)
✅ **19 funciones backend**
✅ **7 componentes frontend**
✅ **3 estados de flujo** (upload, edit, completed)
✅ **CSS personalizado** completo
✅ **Sistema de categorización** completo
✅ **OpenRouter multi-provider** integrado

### Timeline

- **Semana 1**: Backend core + servicios
- **Semana 2**: Frontend React + componentes
- **Semana 3**: Integración E2E + tests
- **Semana 4**: Deploy Coolify + docs

**Total**: 4 semanas (160 horas)

### Costos

- **Desarrollo**: $8,000-12,000
- **Infraestructura**: $50/mes
- **AI (OpenRouter)**: $0.02/documento (40% menos que OpenAI directo)

### ROI Proyectado

Cobrando $5/documento:
- Mes 1: 100 docs = $500 rev - $50 infra = **$450 profit**
- Mes 3: 500 docs = $2,500 rev - $50 infra = **$2,450 profit**
- Mes 12: 5,000 docs = $25,000 rev - $225 infra = **$24,775 profit**

---

**FIN DEL PLAN MVP COMPLETO**

*Versión 1.0 - Enero 2025*
