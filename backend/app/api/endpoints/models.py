"""
ControlNot v2 - Models Endpoints
Endpoints para listar modelos AI y tipos de documento

Rutas:
- GET    /api/models                     - Listar modelos AI disponibles
- GET    /api/models/types               - Listar tipos de documento
- GET    /api/models/fields/{type}       - Obtener campos de un tipo de documento
"""
from fastapi import APIRouter, HTTPException
import structlog

from app.schemas import ModelsListResponse, DocumentTypesResponse, ModelInfo
from app.services import get_available_models, get_all_document_types
from app.services.model_service import get_fields_for_document_type
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=ModelsListResponse)
async def list_ai_models():
    """
    Lista modelos AI disponibles

    Depende de la configuración:
    - Si usa OpenRouter: GPT-4o, Claude, Gemini, Llama
    - Si usa OpenAI directo: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
    """
    logger.info("Listando modelos AI disponibles")

    try:
        # Obtener modelos disponibles
        available_models = get_available_models()

        # Convertir a ModelInfo schema
        models_info = []
        for model_dict in available_models:
            model_info = ModelInfo(
                id=model_dict['id'],
                name=model_dict['name'],
                provider=model_dict['id'].split('/')[0] if '/' in model_dict['id'] else 'openai',
                supports_json=True,  # Todos los modelos modernos soportan JSON
                max_tokens=4096,  # Default
                recommended=(model_dict['id'] == settings.active_model)
            )
            models_info.append(model_info)

        logger.info(
            "Modelos AI listados",
            total=len(models_info),
            using_openrouter=settings.use_openrouter if hasattr(settings, 'use_openrouter') else False
        )

        return ModelsListResponse(
            models=models_info,
            total_models=len(models_info),
            using_openrouter=settings.use_openrouter if hasattr(settings, 'use_openrouter') else False,
            default_model=settings.active_model
        )

    except Exception as e:
        logger.error(
            "Error al listar modelos AI",
            error=str(e),
            error_type=type(e).__name__
        )
        # Retornar lista mínima en caso de error
        return ModelsListResponse(
            models=[
                ModelInfo(
                    id="gpt-4o",
                    name="GPT-4o (fallback)",
                    provider="openai",
                    supports_json=True,
                    max_tokens=4096,
                    recommended=True
                )
            ],
            total_models=1,
            using_openrouter=False,
            default_model="gpt-4o"
        )


@router.get("/types", response_model=DocumentTypesResponse)
async def list_document_types():
    """
    Lista todos los tipos de documento soportados

    Returns:
        - compraventa: 47 campos
        - donacion: 49 campos (con lógica temporal)
        - testamento: 20 campos
        - poder: 20 campos
        - sociedad: 20 campos
    """
    logger.info("Listando tipos de documento")

    try:
        document_types = get_all_document_types()

        logger.info(
            "Tipos de documento listados",
            total=len(document_types)
        )

        return DocumentTypesResponse(
            document_types=document_types,
            total_types=len(document_types)
        )

    except Exception as e:
        logger.error(
            "Error al listar tipos de documento",
            error=str(e)
        )
        raise


@router.get("/fields/{document_type}")
async def get_document_fields(document_type: str):
    """
    Obtiene los campos con metadata para un tipo de documento

    Retorna información estructurada para el DataEditor del frontend:
    - Nombre del campo
    - Etiqueta legible
    - Categoría (agrupación)
    - Tipo de input
    - Si es requerido
    - Texto de ayuda

    Args:
        document_type: Tipo de documento (compraventa, donacion, testamento, poder, sociedad, cancelacion)

    Returns:
        {
            "document_type": "compraventa",
            "fields": [
                {
                    "name": "Parte_Vendedora_Nombre_Completo",
                    "label": "Nombre Completo del Vendedor",
                    "category": "Parte Vendedora",
                    "type": "text",
                    "required": false,
                    "help": "Nombre y apellidos en mayúsculas"
                },
                ...
            ],
            "categories": ["Datos del Instrumento", "Parte Vendedora", ...],
            "total_fields": 51
        }
    """
    logger.info("Solicitando campos de documento", document_type=document_type)

    try:
        # Normalizar tipo
        doc_type = document_type.lower().strip()

        # Tipos válidos
        valid_types = ["compraventa", "donacion", "testamento", "poder", "sociedad", "cancelacion"]

        if doc_type not in valid_types:
            raise HTTPException(
                status_code=404,
                detail=f"Tipo de documento '{document_type}' no soportado. Tipos válidos: {', '.join(valid_types)}"
            )

        # Obtener campos del servicio
        result = get_fields_for_document_type(doc_type)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        logger.info(
            "Campos de documento obtenidos",
            document_type=doc_type,
            total_fields=result["total_fields"]
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al obtener campos de documento",
            document_type=document_type,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener campos: {str(e)}"
        )
