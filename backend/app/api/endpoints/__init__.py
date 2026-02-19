"""
ControlNot v2 - API Endpoints Package
Exports de todos los routers de endpoints

Endpoints disponibles:
1. clients - Gestión de clientes (personas físicas y morales)
2. cases - Gestión de casos/expedientes con workflow CRM
3. templates - Upload y procesamiento de templates Word
4. documents - Categorización y generación de documentos
5. extraction - OCR y extracción con IA
6. health - Health checks y metadata del sistema
7. models - Modelos AI y tipos de documento
8. cancelaciones - Procesamiento especializado de cancelaciones de hipotecas
9. auth - Logging de eventos de autenticación
10. notary_profile - Perfil de notaría (datos del instrumento)
11. template_versions - Versionamiento de templates
12. case_parties - Partes normalizadas de un caso
13. case_checklist - Checklist documental de un caso
14. case_tramites - Trámites gubernamentales de un caso
15. case_activity - Timeline de actividad de un caso
16. catalogos - Catálogos de configuración (checklist templates)
17. case_payments - Pagos de un expediente
18. calendar - Calendario de eventos
19. reports - Reportes y análisis
20. uif - UIF/PLD Operaciones vulnerables
21. whatsapp - WhatsApp Business integration
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
from app.api.endpoints.template_versions import router as template_versions_router
from app.api.endpoints.case_parties import router as case_parties_router
from app.api.endpoints.case_checklist import router as case_checklist_router
from app.api.endpoints.case_tramites import router as case_tramites_router
from app.api.endpoints.case_activity import router as case_activity_router
from app.api.endpoints.catalogos import router as catalogos_router
from app.api.endpoints.case_payments import router as case_payments_router
from app.api.endpoints.calendar import router as calendar_router
from app.api.endpoints.reports import router as reports_router
from app.api.endpoints.uif import router as uif_router
from app.api.endpoints.whatsapp import router as whatsapp_router


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
    "template_versions_router",
    "case_parties_router",
    "case_checklist_router",
    "case_tramites_router",
    "case_activity_router",
    "catalogos_router",
    "case_payments_router",
    "calendar_router",
    "reports_router",
    "uif_router",
    "whatsapp_router",
]
