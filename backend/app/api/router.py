"""
ControlNot v2 - API Router Principal
Integra todos los endpoints de la API

Estructura de rutas:
- /api/clients/*              - Gestión de clientes
- /api/cases/*                - Gestión de casos/expedientes con workflow CRM
- /api/cases/{id}/parties/*   - Partes normalizadas
- /api/cases/{id}/checklist/* - Checklist documental
- /api/cases/{id}/tramites/*  - Trámites gubernamentales
- /api/cases/{id}/timeline    - Timeline de actividad
- /api/cases/{id}/notes       - Notas del caso
- /api/tramites/overdue       - Trámites vencidos
- /api/tramites/upcoming      - Trámites próximos
- /api/catalogos/*            - Catálogos de configuración
- /api/templates/*            - Templates Word
- /api/documents/*            - Documentos y generación
- /api/extraction/*           - OCR y AI
- /api/health                 - Health checks
- /api/models/*               - Modelos AI y tipos
- /api/cancelaciones/*        - Cancelaciones de hipotecas
- /api/auth/*                 - Logging de eventos de autenticación
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
    cancelaciones_router,
    auth_router,
    notary_profile_router,
    template_versions_router,
    case_parties_router,
    case_checklist_router,
    case_tramites_router,
    case_activity_router,
    catalogos_router,
    case_payments_router,
    calendar_router,
    reports_router,
    uif_router,
    whatsapp_router,
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

    # 9. Auth - Logging de eventos de autenticación
    api_router.include_router(
        auth_router,
        # prefix: /auth
        # tags: ["Auth"]
    )
    logger.debug("Router de auth incluido")

    # 10. Notary Profile - Perfil de notaría (datos del instrumento)
    api_router.include_router(
        notary_profile_router,
        # prefix: /notary-profile
        # tags: ["Notary Profile"]
    )
    logger.debug("Router de notary-profile incluido")

    # 11. Template Versions - Versionamiento de templates
    api_router.include_router(
        template_versions_router,
        # prefix: /templates (mismo que templates, endpoints anidados)
        # tags: ["Template Versions"]
    )
    logger.debug("Router de template-versions incluido")

    # 12. Case Parties - Partes normalizadas de un caso
    api_router.include_router(
        case_parties_router,
        # prefix: /cases/{case_id}/parties
        # tags: ["Case Parties"]
    )
    logger.debug("Router de case-parties incluido")

    # 13. Case Checklist - Checklist documental de un caso
    api_router.include_router(
        case_checklist_router,
        # prefix: /cases/{case_id}/checklist
        # tags: ["Case Checklist"]
    )
    logger.debug("Router de case-checklist incluido")

    # 14. Case Tramites - Trámites gubernamentales
    api_router.include_router(
        case_tramites_router,
        # prefix: routes defined inline (case-scoped + top-level)
        # tags: ["Tramites"]
    )
    logger.debug("Router de case-tramites incluido")

    # 15. Case Activity - Timeline y notas
    api_router.include_router(
        case_activity_router,
        # prefix: /cases/{case_id}
        # tags: ["Case Activity"]
    )
    logger.debug("Router de case-activity incluido")

    # 16. Catalogos - Catálogos de configuración
    api_router.include_router(
        catalogos_router,
        # prefix: /catalogos
        # tags: ["Catalogos"]
    )
    logger.debug("Router de catalogos incluido")

    # 17. Case Payments - Pagos de un expediente
    api_router.include_router(
        case_payments_router,
        # prefix: /cases/{case_id}/payments
        # tags: ["Case Payments"]
    )
    logger.debug("Router de case-payments incluido")

    # 18. Calendar - Calendario de eventos
    api_router.include_router(
        calendar_router,
        # prefix: /calendar
        # tags: ["Calendar"]
    )
    logger.debug("Router de calendar incluido")

    # 19. Reports - Reportes y análisis
    api_router.include_router(
        reports_router,
        # prefix: /reports
        # tags: ["Reports"]
    )
    logger.debug("Router de reports incluido")

    # 20. UIF/PLD - Operaciones vulnerables
    api_router.include_router(
        uif_router,
        # prefix: /uif
        # tags: ["UIF/PLD"]
    )
    logger.debug("Router de uif incluido")

    # 21. WhatsApp - Integracion WhatsApp Business
    api_router.include_router(
        whatsapp_router,
        # prefix: /whatsapp
        # tags: ["WhatsApp"]
    )
    logger.debug("Router de whatsapp incluido")

    logger.info("Todos los routers incluidos exitosamente (21 routers)")


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
        "version": "2.1.0",
        "description": "API para procesamiento de documentos notariales con IA y CRM de expedientes",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "endpoints": {
            "clients": "/api/clients",
            "cases": "/api/cases",
            "cases_dashboard": "/api/cases/dashboard",
            "templates": "/api/templates",
            "documents": "/api/documents",
            "extraction": "/api/extraction",
            "models": "/api/models",
            "cancelaciones": "/api/cancelaciones",
            "tramites_overdue": "/api/tramites/overdue",
            "tramites_upcoming": "/api/tramites/upcoming",
            "catalogos": "/api/catalogos/checklist-templates",
        },
        "features": [
            "Gestión completa de clientes (personas físicas y morales)",
            "CRM de expedientes con state machine (14 estados de workflow)",
            "Partes normalizadas por caso con roles",
            "Checklist documental configurable por tipo de documento",
            "Trámites gubernamentales con semáforo de vencimiento",
            "Timeline de actividad por caso",
            "Dashboard con semáforo global y trámites vencidos",
            "Upload y procesamiento de templates Word",
            "Auto-detección de tipo de documento",
            "OCR paralelo asíncrono (5-10x más rápido)",
            "Extracción con IA multi-provider (OpenRouter + OpenAI)",
            "Generación automática de documentos",
            "Soporte para 6 tipos de documentos notariales",
            "Base de datos PostgreSQL con Supabase",
            "Multi-tenancy con Row Level Security"
        ],
    }
