"""
ControlNot v2 - FastAPI Application
Aplicación principal con configuración de CORS, middleware y routers

Migrado desde por_partes.py (2,550 líneas) a arquitectura FastAPI modular

Mejoras críticas:
- OCR asíncrono paralelo (5-10x más rápido)
- OpenRouter multi-provider (GPT-4o, Claude, Gemini, Llama)
- Arquitectura limpia y modular
- Type hints completos
- Logging estructurado
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time
import uuid
import logging

from collections import defaultdict

from app.core.config import settings
from app.api.router import api_router
from app.middleware.audit import audit_middleware

# Configurar structlog correctamente
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.ENVIRONMENT == "development" else structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

# Rutas que NO deben loguearse (health checks, docs)
SILENT_ROUTES = {"/ping", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager para startup y shutdown de la aplicación

    Startup:
    - Verificar directorios necesarios
    - Cargar configuración
    - Inicializar servicios

    Shutdown:
    - Cerrar conexiones
    - Cleanup de recursos
    """
    logger.info("[START] Iniciando ControlNot v2...")

    # Startup
    try:
        # Verificar que los directorios existan
        Path(settings.TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        logger.info(
            "Directorios verificados",
            templates_dir=str(settings.TEMPLATES_DIR),
            output_dir=str(settings.OUTPUT_DIR)
        )

        # Log configuración activa
        logger.info(
            "Configuración cargada",
            environment=settings.ENVIRONMENT,
            ai_provider=settings.active_ai_provider,
            model=settings.active_model,
            use_openrouter=settings.use_openrouter if hasattr(settings, 'use_openrouter') else False
        )

        logger.info("[OK] ControlNot v2 iniciado exitosamente")

    except Exception as e:
        logger.error(
            "Error en startup",
            error=str(e),
            error_type=type(e).__name__
        )
        raise

    yield

    # Shutdown
    logger.info("Deteniendo ControlNot v2...")

    # Close WhatsApp httpx connection pool
    try:
        from app.services.whatsapp_service import whatsapp_service
        await whatsapp_service.close()
        logger.info("WhatsApp HTTP client closed")
    except Exception as e:
        logger.warning("whatsapp_client_close_failed", error=str(e))

    logger.info("Shutdown completado")


# Crear aplicación FastAPI
app = FastAPI(
    title="ControlNot v2 API",
    description="""
    API para procesamiento de documentos notariales con IA

    ## Características principales

    * **Templates**: Upload y procesamiento de templates Word con auto-detección
    * **OCR Paralelo**: Procesamiento asíncrono 5-10x más rápido
    * **IA Multi-Provider**: OpenRouter (GPT-4o, Claude, Gemini, Llama) + OpenAI
    * **Generación Automática**: Documentos Word con reemplazo inteligente
    * **5 Tipos de Documentos**: Compraventa, Donación, Testamento, Poder, Sociedad

    ## Migración desde por_partes.py

    Este backend reemplaza el script monolítico de 2,550 líneas con:
    - Arquitectura modular con separación de responsabilidades
    - Type hints completos para mejor desarrollo
    - Logging estructurado para debugging
    - Tests automatizados
    - Documentación OpenAPI/Swagger automática

    ## Stack Tecnológico

    - **FastAPI**: Framework web moderno y rápido
    - **Pydantic v2**: Validación de datos robusta
    - **Google Cloud Vision**: OCR de alta calidad
    - **OpenRouter/OpenAI**: Extracción con IA
    - **python-docx**: Procesamiento de documentos Word
    - **structlog**: Logging JSON estructurado
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# In-memory rate limiter (per IP, per route)
_rate_limit_buckets: dict = defaultdict(list)

# Rate limits: path prefix → max requests per 60s window
RATE_LIMIT_RULES: dict[str, int] = {
    "/api/extraction/ocr": 10,
    "/api/extraction/vision": 10,
    "/api/extraction/ai": 20,
    "/whatsapp/send-template": 20,
    "/whatsapp/send": 30,
}

# CORS Middleware
# Permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Middleware para rate limiting en endpoints costosos
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple in-memory rate limiter for expensive endpoints (per IP, 60s window)"""
    if request.method == "POST":
        path = request.url.path
        for rule_path, max_requests in RATE_LIMIT_RULES.items():
            if path.startswith(rule_path):
                client_ip = request.client.host if request.client else "unknown"
                bucket_key = f"{client_ip}:{rule_path}"
                now = time.time()
                # Prune old entries (older than 60s)
                _rate_limit_buckets[bucket_key] = [
                    t for t in _rate_limit_buckets[bucket_key] if now - t < 60
                ]
                if len(_rate_limit_buckets[bucket_key]) >= max_requests:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "error": "Rate limit exceeded",
                            "detail": f"Demasiadas solicitudes. Límite: {max_requests}/minuto",
                            "error_code": "RATE_LIMIT_EXCEEDED",
                            "status_code": 429,
                        }
                    )
                _rate_limit_buckets[bucket_key].append(now)
                break
    return await call_next(request)


# Middleware para logging de requests (con filtrado inteligente)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para loguear requests importantes

    Registra:
    - Método HTTP y ruta (excluyendo health checks)
    - Tiempo de procesamiento
    - Status code de respuesta
    - Correlation ID para trazabilidad

    NO registra:
    - /ping, /health (health checks)
    - /docs, /redoc, /openapi.json (documentación)
    """
    start_time = time.time()
    path = request.url.path

    # Generar correlation ID para trazabilidad
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())[:8]

    # Almacenar en request.state para uso en otros middlewares/endpoints
    request.state.correlation_id = correlation_id

    # Verificar si es una ruta silenciosa
    is_silent = path in SILENT_ROUTES or path.startswith("/docs") or path.startswith("/api/health")

    if not is_silent:
        logger.info(
            "Request",
            correlation_id=correlation_id,
            method=request.method,
            path=path,
            client=request.client.host if request.client else None
        )

    try:
        response = await call_next(request)
    except RuntimeError as e:
        if "No response returned" in str(e):
            logger.warning("middleware_no_response", path=path, correlation_id=correlation_id)
            from starlette.responses import Response as StarletteResponse
            response = StarletteResponse(status_code=500)
        else:
            raise

    process_time = time.time() - start_time

    # Solo loguear respuestas de rutas no silenciosas o errores
    if not is_silent or response.status_code >= 400:
        log_level = "warning" if response.status_code >= 400 else "info"
        getattr(logger, log_level)(
            "Response",
            correlation_id=correlation_id,
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2)
        )

    # Headers de respuesta
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Correlation-ID"] = correlation_id

    return response


# Middleware para auditoría de operaciones
@app.middleware("http")
async def audit_operations(request: Request, call_next):
    """
    Middleware para registrar operaciones importantes en audit_logs

    Registra:
    - Todas las operaciones de modificación (POST, PUT, DELETE)
    - Usuario, tenant, IP, user-agent
    - Duración y resultado de la operación

    NO registra operaciones de solo lectura (GET)
    """
    return await audit_middleware(request, call_next)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler global para errores de validación de Pydantic

    Convierte ValidationError en respuesta JSON estructurada
    """
    logger.warning(
        "Error de validación",
        path=request.url.path,
        errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Error de validación",
            "detail": "Los datos enviados no cumplen con el formato esperado",
            "error_code": "VALIDATION_ERROR",
            "status_code": 422,
            "validation_errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para excepciones no manejadas

    Previene que errores internos expongan detalles sensibles
    """
    logger.error(
        "Error no manejado",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": "Ocurrió un error inesperado. Por favor contacte al administrador.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": 500
        }
    )


# Incluir router principal de la API
app.include_router(api_router)


# Endpoints raíz
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la aplicación

    Retorna información básica y enlaces útiles
    """
    return {
        "name": "ControlNot v2",
        "version": "2.0.0",
        "status": "running",
        "description": "API para procesamiento de documentos notariales con IA",
        "migrated_from": "por_partes.py (2,550 líneas)",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "api": {
            "base_url": "/api",
            "endpoints": {
                "templates": "/api/templates",
                "documents": "/api/documents",
                "extraction": "/api/extraction",
                "health": "/api/health",
                "models": "/api/models"
            }
        },
        "improvements": [
            "OCR asíncrono paralelo (5-10x más rápido)",
            "OpenRouter multi-provider (GPT-4o, Claude, Gemini, Llama)",
            "Arquitectura modular con FastAPI",
            "Almacenamiento dual (Drive + Local)",
            "Type hints completos",
            "Logging estructurado",
            "Tests automatizados"
        ]
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """
    Endpoint simple para verificar que la API responde

    Útil para health checks de Docker, Kubernetes, etc.
    """
    return {"ping": "pong", "status": "ok"}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de health check para Docker/Kubernetes

    Retorna estado de salud de la aplicación y sus dependencias
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "controlnot-backend"
    }


# Punto de entrada para uvicorn
if __name__ == "__main__":
    import uvicorn

    logger.info(
        "Iniciando servidor Uvicorn",
        host="0.0.0.0",
        port=8000
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )
