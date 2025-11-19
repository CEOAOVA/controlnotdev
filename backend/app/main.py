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
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time

from app.core.config import settings
from app.api.router import api_router

# Configurar logger estructurado
logger = structlog.get_logger()


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
    logger.info("🚀 Iniciando ControlNot v2...")

    # Startup
    try:
        # Verificar que los directorios existan
        settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

        logger.info("✅ ControlNot v2 iniciado exitosamente")

    except Exception as e:
        logger.error(
            "Error en startup",
            error=str(e),
            error_type=type(e).__name__
        )
        raise

    yield

    # Shutdown
    logger.info("🛑 Deteniendo ControlNot v2...")
    logger.info("✅ Shutdown completado")


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


# CORS Middleware
# Permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev
        "http://localhost:5173",  # Vite dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para loguear todas las requests

    Registra:
    - Método HTTP y ruta
    - Tiempo de procesamiento
    - Status code de respuesta
    """
    start_time = time.time()

    logger.info(
        "Request recibido",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "Request procesado",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time_seconds=f"{process_time:.3f}"
    )

    # Agregar header con tiempo de procesamiento
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    return response


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
