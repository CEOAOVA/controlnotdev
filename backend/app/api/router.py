"""
ControlNot v2 - API Router Principal
Integra todos los endpoints de la API

Estructura de rutas:
- /api/clients/*          - Gestión de clientes
- /api/cases/*            - Gestión de casos/expedientes
- /api/templates/*        - Templates Word
- /api/documents/*        - Documentos y generación
- /api/extraction/*       - OCR y AI
- /api/health             - Health checks
- /api/models/*           - Modelos AI y tipos
- /api/cancelaciones/*    - Cancelaciones de hipotecas
"""
from fastapi import APIRouter
import structlog

from app.api.endpoints import (
    clients_router,
    cases_router,
    templates_router,
    documents_router,
    extraction_router,
    health_router,
    models_router,
    cancelaciones_router
)

logger = structlog.get_logger()

# Router principal de la API
api_router = APIRouter(prefix="/api")


def include_all_routers():
    """
    Incluye todos los routers de endpoints en el router principal

    Cada router tiene su propio prefix y tags para organización en Swagger
    """
    logger.info("Configurando routers de la API")

    # 1. Clients - Gestión de clientes
    api_router.include_router(
        clients_router,
        # prefix ya definido en el router: /clients
        # tags ya definidos en el router: ["Clients"]
    )
    logger.debug("Router de clients incluido")

    # 2. Cases - Gestión de casos/expedientes
    api_router.include_router(
        cases_router,
        # prefix: /cases
        # tags: ["Cases"]
    )
    logger.debug("Router de cases incluido")

    # 3. Templates - Upload y procesamiento de templates Word
    api_router.include_router(
        templates_router,
        # prefix: /templates
        # tags: ["Templates"]
    )
    logger.debug("Router de templates incluido")

    # 4. Documents - Categorización y generación de documentos
    api_router.include_router(
        documents_router,
        # prefix: /documents
        # tags: ["Documents"]
    )
    logger.debug("Router de documents incluido")

    # 5. Extraction - OCR y extracción con IA
    api_router.include_router(
        extraction_router,
        # prefix: /extraction
        # tags: ["Extraction"]
    )
    logger.debug("Router de extraction incluido")

    # 6. Health - Health checks y metadata
    api_router.include_router(
        health_router,
        # prefix: /health
        # tags: ["Health"]
    )
    logger.debug("Router de health incluido")

    # 7. Models - Modelos AI y tipos de documento
    api_router.include_router(
        models_router,
        # prefix: /models
        # tags: ["Models"]
    )
    logger.debug("Router de models incluido")

    # 8. Cancelaciones - Procesamiento especializado de cancelaciones de hipotecas
    api_router.include_router(
        cancelaciones_router,
        # prefix: /cancelaciones
        # tags: ["Cancelaciones"]
    )
    logger.debug("Router de cancelaciones incluido")

    logger.info("Todos los routers incluidos exitosamente")


# Incluir todos los routers al importar este módulo
include_all_routers()


# Endpoint raíz de la API
@api_router.get("/", tags=["Root"])
async def api_root():
    """
    Endpoint raíz de la API

    Retorna información básica de la API
    """
    return {
        "name": "ControlNot v2 API",
        "version": "2.0.0",
        "description": "API para procesamiento de documentos notariales con IA",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "endpoints": {
            "clients": "/api/clients",
            "cases": "/api/cases",
            "templates": "/api/templates",
            "documents": "/api/documents",
            "extraction": "/api/extraction",
            "models": "/api/models",
            "cancelaciones": "/api/cancelaciones"
        },
        "features": [
            "Gestión completa de clientes (personas físicas y morales)",
            "Gestión de casos/expedientes con seguimiento de estado",
            "Upload y procesamiento de templates Word",
            "Auto-detección de tipo de documento",
            "OCR paralelo asíncrono (5-10x más rápido)",
            "Extracción con IA multi-provider (OpenRouter + OpenAI)",
            "Generación automática de documentos",
            "Soporte para 6 tipos de documentos notariales (incluyendo cancelaciones)",
            "Procesamiento especializado de cancelaciones de hipotecas (50 campos)",
            "Base de datos PostgreSQL con Supabase",
            "Multi-tenancy con Row Level Security"
        ],
        "migrated_from": "por_partes.py (2,550 líneas)",
        "improvements": [
            "Arquitectura modular con FastAPI",
            "PostgreSQL con Supabase para persistencia",
            "Repository pattern para acceso a datos",
            "Multi-tenancy con RLS",
            "OCR async paralelo",
            "OpenRouter multi-provider (GPT-4o, Claude, Gemini, Llama)",
            "Almacenamiento dual (Drive + Local)",
            "Type hints completos",
            "Logging estructurado"
        ]
    }
