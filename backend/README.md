# ControlNot v2 - Backend

API FastAPI para procesamiento documental notarial con IA.

## 🚀 Quick Start

### 1. Configurar entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env con tus credenciales:
# - OPENAI_API_KEY (obligatorio como fallback)
# - OPENROUTER_API_KEY (opcional pero recomendado)
# - GOOGLE_CREDENTIALS_JSON (obligatorio para OCR)
# - SMTP_EMAIL y SMTP_PASSWORD (obligatorio para envío)
```

### 4. Iniciar servidor

```bash
# Modo desarrollo (con hot-reload)
python -m app.main

# O usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Servidor disponible en: **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

## 📁 Estructura

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── core/
│   │   ├── config.py        # Settings con Pydantic
│   │   └── dependencies.py  # Dependency injection
│   ├── api/v1/
│   │   └── endpoints/       # REST endpoints (TODO)
│   ├── models/              # Pydantic models (TODO)
│   ├── schemas/             # Request/Response schemas (TODO)
│   ├── services/            # Business logic (TODO)
│   │   ├── categorization_service.py
│   │   ├── ocr_service.py
│   │   ├── ai_service.py
│   │   └── document_service.py
│   └── utils/               # Helpers (TODO)
├── data/                    # JSON storage (MVP)
├── templates/               # Plantillas .docx
├── uploads/                 # Archivos subidos (gitignored)
├── outputs/                 # Documentos generados (gitignored)
├── tests/                   # Tests
├── .env.example             # Template variables
└── requirements.txt         # Dependencies
```

## 🔧 Configuración Detallada

### AI Providers

**OpenRouter (Recomendado)**:
- Multi-provider: OpenAI, Anthropic, Google, Meta
- Sintaxis compatible con OpenAI
- Costo optimizado
- API Key: https://openrouter.ai/keys

```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o  # o anthropic/claude-3-opus
```

**OpenAI (Fallback)**:
```bash
OPENAI_API_KEY=sk-proj-...
```

### Google Cloud Vision (OCR)

1. Crear proyecto: https://console.cloud.google.com
2. Habilitar Vision API
3. Crear Service Account
4. Descargar JSON credentials
5. Copiar contenido completo del JSON a `.env`:

```bash
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

### Email (SMTP Gmail)

1. Generar App Password: https://myaccount.google.com/apppasswords
2. Configurar en `.env`:

```bash
SMTP_EMAIL=tu_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app tests/
```

## 📊 Endpoints (Roadmap)

### Phase 1 - Categorization
- `POST /api/v1/documents/categorize` - Categorizar documentos por rol

### Phase 2 - OCR
- `POST /api/v1/ocr/process` - Procesar OCR paralelo

### Phase 3 - AI Extraction
- `POST /api/v1/extract/{doc_type}` - Extraer datos con IA

### Phase 4 - Document Generation
- `POST /api/v1/documents/generate` - Generar documento final

### Phase 5 - Complete Workflow
- `POST /api/v1/process/complete` - Pipeline completo E2E

## 🔒 Seguridad

- ✅ Variables de entorno para secrets
- ✅ CORS configurado
- ✅ Validación con Pydantic
- 🚧 Rate limiting (futuro)
- 🚧 Authentication (futuro - Supabase)

## 📝 Logs

Usando `structlog` para logging estructurado:

```python
import structlog
logger = structlog.get_logger()

logger.info("Documento procesado", doc_id=123, tipo="compraventa")
```

## 🚀 Deploy

Ver guía completa en: `../docs/DEPLOYMENT_COOLIFY.md` (próximamente)

---

**ControlNot v2 Backend** - FastAPI + OpenRouter + Google Vision
