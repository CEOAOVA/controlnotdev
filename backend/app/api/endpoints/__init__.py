"""
ControlNot v2 - API Endpoints Package
Exports de todos los routers de endpoints

Endpoints disponibles:
1. clients - Gestión de clientes (personas físicas y morales)
2. cases - Gestión de casos/expedientes
3. templates - Upload y procesamiento de templates Word
4. documents - Categorización y generación de documentos
5. extraction - OCR y extracción con IA
6. health - Health checks y metadata del sistema
7. models - Modelos AI y tipos de documento
8. cancelaciones - Procesamiento especializado de cancelaciones de hipotecas
9. auth - Logging de eventos de autenticación
10. notary_profile - Perfil de notaría (datos del instrumento)
"""

from app.api.endpoints.clients import router as clients_router
from app.api.endpoints.cases import router as cases_router
from app.api.endpoints.templates import router as templates_router
from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.extraction import router as extraction_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.models import router as models_router
from app.api.endpoints.cancelaciones import router as cancelaciones_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.notary_profile import router as notary_profile_router


__all__ = [
    "clients_router",
    "cases_router",
    "templates_router",
    "documents_router",
    "extraction_router",
    "health_router",
    "models_router",
    "cancelaciones_router",
    "auth_router",
    "notary_profile_router",
]
