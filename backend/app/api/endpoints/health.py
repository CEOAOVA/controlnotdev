"""
ControlNot v2 - Health Endpoints
Endpoints para health checks y metadata del sistema

Rutas:
- GET    /api/health                     - Health check general
- GET    /api/health/services            - Estado de servicios externos
"""
from fastapi import APIRouter, Depends
import structlog

from app.schemas import HealthCheckResponse
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check general del sistema

    Verifica:
    - API está corriendo
    - Servicios externos están disponibles
    - Configuración es válida
    """
    logger.info("Health check solicitado")

    # Verificar servicios externos
    services_status = {}

    # 1. OpenAI/OpenRouter
    try:
        if settings.use_openrouter:
            if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "TU_OPENROUTER_API_KEY_AQUI":
                services_status['openrouter'] = 'ok'
            else:
                services_status['openrouter'] = 'not_configured'
        else:
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "TU_OPENAI_API_KEY_AQUI":
                services_status['openai'] = 'ok'
            else:
                services_status['openai'] = 'not_configured'
    except Exception as e:
        services_status['openai'] = 'error'
        logger.error("Error verificando OpenAI", error=str(e))

    # 2. Google Cloud Vision
    try:
        if hasattr(settings, 'GOOGLE_CREDENTIALS_PATH'):
            services_status['google_vision'] = 'ok'
        else:
            services_status['google_vision'] = 'not_configured'
    except Exception as e:
        services_status['google_vision'] = 'error'
        logger.error("Error verificando Google Vision", error=str(e))

    # 3. Google Drive (opcional)
    try:
        if hasattr(settings, 'GOOGLE_CREDENTIALS_PATH'):
            services_status['google_drive'] = 'ok'
        else:
            services_status['google_drive'] = 'not_configured'
    except Exception as e:
        services_status['google_drive'] = 'error'

    # 4. SMTP
    try:
        if settings.SMTP_SERVER and settings.SMTP_USER:
            services_status['smtp'] = 'ok'
        else:
            services_status['smtp'] = 'not_configured'
    except Exception as e:
        services_status['smtp'] = 'error'

    # Determinar estado general
    error_count = sum(1 for status in services_status.values() if status == 'error')
    not_configured_count = sum(1 for status in services_status.values() if status == 'not_configured')

    if error_count > 0:
        overall_status = 'unhealthy'
    elif not_configured_count > 0:
        overall_status = 'degraded'
    else:
        overall_status = 'healthy'

    logger.info(
        "Health check completado",
        status=overall_status,
        services=services_status
    )

    return HealthCheckResponse(
        status=overall_status,
        version="2.0.0",
        services=services_status
    )


@router.get("/services")
async def get_services_status():
    """
    Estado detallado de cada servicio externo

    Returns:
        Información detallada de cada servicio
    """
    logger.info("Solicitado estado de servicios")

    services = {
        "ai_provider": {
            "name": settings.active_ai_provider,
            "model": settings.active_model,
            "configured": settings.use_openrouter if hasattr(settings, 'use_openrouter') else False
        },
        "ocr": {
            "provider": "Google Cloud Vision",
            "max_concurrent": settings.MAX_CONCURRENT_OCR if hasattr(settings, 'MAX_CONCURRENT_OCR') else 5
        },
        "storage": {
            "templates_dir": str(settings.TEMPLATES_DIR) if hasattr(settings, 'TEMPLATES_DIR') else None,
            "output_dir": str(settings.OUTPUT_DIR) if hasattr(settings, 'OUTPUT_DIR') else None
        },
        "email": {
            "smtp_server": settings.SMTP_SERVER if hasattr(settings, 'SMTP_SERVER') else None,
            "smtp_port": settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else None
        }
    }

    return {
        "services": services,
        "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development"
    }


@router.get("/ai-ready")
async def check_ai_readiness():
    """
    Verifica que los servicios de IA estén correctamente configurados.

    Chequea:
    - ANTHROPIC_API_KEY configurado
    - OPENROUTER_API_KEY o OPENAI_API_KEY configurado
    - GOOGLE_CREDENTIALS_JSON configurado para OCR

    Returns:
        ai_ready: True si al menos un servicio de IA está listo
        ocr_ready: True si OCR está configurado
        services: Estado detallado de cada servicio
    """
    logger.info("Verificando readiness de servicios de IA")

    # Check AI services
    anthropic_configured = bool(
        getattr(settings, 'ANTHROPIC_API_KEY', None) and
        settings.ANTHROPIC_API_KEY != "TU_ANTHROPIC_API_KEY_AQUI"
    )

    openrouter_configured = bool(
        getattr(settings, 'OPENROUTER_API_KEY', None) and
        settings.OPENROUTER_API_KEY != "TU_OPENROUTER_API_KEY_AQUI"
    )

    openai_configured = bool(
        getattr(settings, 'OPENAI_API_KEY', None) and
        settings.OPENAI_API_KEY != "TU_OPENAI_API_KEY_AQUI"
    )

    # Check OCR (Google Vision)
    google_credentials = getattr(settings, 'GOOGLE_CREDENTIALS_JSON', None)
    ocr_configured = bool(
        google_credentials and
        google_credentials != "" and
        google_credentials != "{}"
    )

    # Determine readiness
    ai_ready = anthropic_configured or openrouter_configured or openai_configured
    ocr_ready = ocr_configured

    # Build response
    services = {
        "anthropic": {
            "configured": anthropic_configured,
            "model": getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        },
        "openrouter": {
            "configured": openrouter_configured,
            "model": getattr(settings, 'OPENROUTER_MODEL', None)
        },
        "openai": {
            "configured": openai_configured
        },
        "google_vision": {
            "configured": ocr_configured
        }
    }

    # Determine active AI provider
    active_provider = None
    if anthropic_configured:
        active_provider = "anthropic"
    elif openrouter_configured:
        active_provider = "openrouter"
    elif openai_configured:
        active_provider = "openai"

    logger.info(
        "AI readiness check completado",
        ai_ready=ai_ready,
        ocr_ready=ocr_ready,
        active_provider=active_provider
    )

    return {
        "ai_ready": ai_ready,
        "ocr_ready": ocr_ready,
        "all_ready": ai_ready and ocr_ready,
        "active_provider": active_provider,
        "services": services,
        "message": (
            "Sistema listo para procesar documentos" if (ai_ready and ocr_ready)
            else "Faltan configuraciones: " + ", ".join([
                s for s, ready in [
                    ("IA (ANTHROPIC/OPENROUTER/OPENAI)", not ai_ready),
                    ("OCR (GOOGLE_CREDENTIALS_JSON)", not ocr_ready)
                ] if ready
            ])
        )
    }
