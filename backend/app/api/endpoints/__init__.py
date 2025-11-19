"""
ControlNot v2 - API Endpoints Package
Exports de todos los routers de endpoints

Endpoints disponibles:
1. templates - Upload y procesamiento de templates Word
2. documents - Categorización y generación de documentos
3. extraction - OCR y extracción con IA
4. health - Health checks y metadata del sistema
5. models - Modelos AI y tipos de documento
"""

from app.api.endpoints.templates import router as templates_router
from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.extraction import router as extraction_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.models import router as models_router


__all__ = [
    "templates_router",
    "documents_router",
    "extraction_router",
    "health_router",
    "models_router",
]
