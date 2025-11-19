"""
ControlNot v2 - API Router Principal
Integra todos los endpoints de la API

Estructura de rutas:
- /api/templates/*        - Templates Word
- /api/documents/*        - Documentos y generación
- /api/extraction/*       - OCR y AI
- /api/health             - Health checks
- /api/models/*           - Modelos AI y tipos
"""
from fastapi import APIRouter
import structlog

from app.api.endpoints import (
    templates_router,
    documents_router,
    extraction_router,
    health_router,
    models_router
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

    # 1. Templates - Upload y procesamiento de templates Word
    api_router.include_router(
        templates_router,
        # prefix ya definido en el router: /templates
        # tags ya definidos en el router: ["Templates"]
    )
    logger.debug("Router de templates incluido")

    # 2. Documents - Categorización y generación de documentos
    api_router.include_router(
        documents_router,
        # prefix: /documents
        # tags: ["Documents"]
    )
    logger.debug("Router de documents incluido")

    # 3. Extraction - OCR y extracción con IA
    api_router.include_router(
        extraction_router,
        # prefix: /extraction
        # tags: ["Extraction"]
    )
    logger.debug("Router de extraction incluido")

    # 4. Health - Health checks y metadata
    api_router.include_router(
        health_router,
        # prefix: /health
        # tags: ["Health"]
    )
    logger.debug("Router de health incluido")

    # 5. Models - Modelos AI y tipos de documento
    api_router.include_router(
        models_router,
        # prefix: /models
        # tags: ["Models"]
    )
    logger.debug("Router de models incluido")

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
            "templates": "/api/templates",
            "documents": "/api/documents",
            "extraction": "/api/extraction",
            "models": "/api/models"
        },
        "features": [
            "Upload y procesamiento de templates Word",
            "Auto-detección de tipo de documento",
            "OCR paralelo asíncrono (5-10x más rápido)",
            "Extracción con IA multi-provider (OpenRouter + OpenAI)",
            "Generación automática de documentos",
            "Soporte para 5 tipos de documentos notariales"
        ],
        "migrated_from": "por_partes.py (2,550 líneas)",
        "improvements": [
            "Arquitectura modular con FastAPI",
            "OCR async paralelo",
            "OpenRouter multi-provider (GPT-4o, Claude, Gemini, Llama)",
            "Almacenamiento dual (Drive + Local)",
            "Type hints completos",
            "Logging estructurado"
        ]
    }
