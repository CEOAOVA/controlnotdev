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
from app.services.categorization_service import get_categories_for_type
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


@router.get("/categories/{document_type}")
async def get_categories_for_document(document_type: str):
    """
    Obtiene las categorías de documentos para un tipo específico

    Args:
        document_type: compraventa, donacion, testamento, poder, sociedad, cancelacion

    Returns:
        {
            "categories": [
                {"name": "parte_a", "description": "Documentos del Vendedor", "icon": "📤"},
                {"name": "parte_b", "description": "Documentos del Comprador", "icon": "📥"},
                {"name": "otros", "description": "Otros documentos", "icon": "📄"}
            ],
            "document_type": "compraventa"
        }
    """
    logger.info("Solicitando categorías", document_type=document_type)

    try:
        doc_type = document_type.lower().strip()

        valid_types = ["compraventa", "donacion", "testamento", "poder", "sociedad", "cancelacion"]
        if doc_type not in valid_types:
            raise HTTPException(
                status_code=404,
                detail=f"Tipo de documento '{document_type}' no soportado. Tipos válidos: {', '.join(valid_types)}"
            )

        categories_data = get_categories_for_type(doc_type)

        # Formatear respuesta para frontend
        categories = [
            {
                "name": "parte_a",
                "description": categories_data.get('parte_a', {}).get('nombre', 'Parte A'),
                "icon": categories_data.get('parte_a', {}).get('icono', '📄'),
                "required": categories_data.get('parte_a', {}).get('required', True)
            },
            {
                "name": "parte_b",
                "description": categories_data.get('parte_b', {}).get('nombre', 'Parte B'),
                "icon": categories_data.get('parte_b', {}).get('icono', '📄'),
                "required": categories_data.get('parte_b', {}).get('required', True)
            },
            {
                "name": "otros",
                "description": categories_data.get('otros', {}).get('nombre', 'Otros'),
                "icon": categories_data.get('otros', {}).get('icono', '📋'),
                "required": categories_data.get('otros', {}).get('required', True)
            }
        ]

        logger.info(
            "Categorías obtenidas",
            document_type=doc_type,
            total_categories=len(categories)
        )

        return {
            "categories": categories,
            "document_type": doc_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error al obtener categorías",
            document_type=document_type,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener categorías: {str(e)}"
        )


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


@router.get("/fields/cancelacion/legacy")
async def get_cancelacion_legacy_fields():
    """
    Obtiene los campos LEGACY para cancelaciones (movil_cancelaciones.py)

    Estos son los 31 campos que funcionan al 100% en extracción.
    Usar cuando se extrae con el endpoint /api/cancelaciones/legacy/extract

    Returns:
        {
            "document_type": "cancelacion",
            "fields": [...],  // 31 campos legacy
            "categories": ["Datos Generales", "Datos del Crédito", ...],
            "total_fields": 31,
            "source": "movil_cancelaciones.py"
        }
    """
    from app.services.cancelacion_service import CLAVES_ESTANDARIZADAS_LEGACY

    logger.info("Solicitando campos LEGACY de cancelación")

    # Mapeo de campos a categorías
    category_mapping = {
        # Datos Generales
        "intermediario_financiero": "Datos Generales",
        "deudor": "Datos Generales",

        # Datos de la Escritura Original
        "numero_escritura": "Datos de la Escritura",
        "fecha_escritura": "Datos de la Escritura",
        "notario": "Datos de la Escritura",
        "numero_notario": "Datos de la Escritura",
        "ciudad_residencia": "Datos de la Escritura",

        # Datos del Registro
        "numero_registro_libro_propiedad": "Datos del Registro",
        "tomo_libro_propiedad": "Datos del Registro",
        "numero_registro_libro_gravamen": "Datos del Registro",
        "tomo_libro_gravamen": "Datos del Registro",

        # Datos del Crédito
        "suma_credito": "Datos del Crédito",
        "suma_credito_letras": "Datos del Crédito",
        "equivalente_salario_minimo": "Datos del Crédito",
        "equivalente_salario_minimo_letras": "Datos del Crédito",
        "ubicacion_inmueble": "Datos del Crédito",

        # Cesión de Crédito
        "cesion_credito_fecha": "Cesión de Crédito",
        "cesion_credito_valor": "Cesión de Crédito",

        # Constancia de Finiquito
        "constancia_finiquito_numero_oficio": "Constancia de Finiquito",
        "constancia_finiquito_fecha_emision": "Constancia de Finiquito",

        # Carta de Instrucciones
        "carta_instrucciones_numero_oficio": "Carta de Instrucciones",
        "carta_instrucciones_fecha_constancia_liquidacion": "Carta de Instrucciones",
        "carta_instrucciones_nombre_titular_credito": "Carta de Instrucciones",
        "carta_instrucciones_numero_credito": "Carta de Instrucciones",
        "carta_instrucciones_tipo_credito": "Carta de Instrucciones",
        "carta_instrucciones_fecha_adjudicacion": "Carta de Instrucciones",
        "carta_instrucciones_ubicacion_inmueble": "Carta de Instrucciones",
        "carta_instrucciones_valor_credito": "Carta de Instrucciones",
        "carta_instrucciones_valor_credito_letras": "Carta de Instrucciones",
        "carta_instrucciones_numero_registro": "Carta de Instrucciones",
        "carta_instrucciones_tomo": "Carta de Instrucciones",
    }

    # Mapeo de campos a labels legibles
    label_mapping = {
        "intermediario_financiero": "Intermediario Financiero",
        "deudor": "Nombre del Deudor",
        "numero_escritura": "Número de Escritura (letras)",
        "fecha_escritura": "Fecha de Escritura",
        "notario": "Nombre del Notario",
        "numero_notario": "Número de Notario (letras)",
        "ciudad_residencia": "Ciudad de Residencia",
        "numero_registro_libro_propiedad": "Número Registro Libro Propiedad",
        "tomo_libro_propiedad": "Tomo Libro Propiedad",
        "numero_registro_libro_gravamen": "Número Registro Libro Gravamen",
        "tomo_libro_gravamen": "Tomo Libro Gravamen",
        "suma_credito": "Suma del Crédito",
        "suma_credito_letras": "Suma del Crédito (letras)",
        "equivalente_salario_minimo": "Equivalente Salario Mínimo",
        "equivalente_salario_minimo_letras": "Equivalente Salario Mínimo (letras)",
        "ubicacion_inmueble": "Ubicación del Inmueble",
        "cesion_credito_fecha": "Fecha Cesión de Crédito",
        "cesion_credito_valor": "Valor Cesión de Crédito",
        "constancia_finiquito_numero_oficio": "Número Oficio Finiquito",
        "constancia_finiquito_fecha_emision": "Fecha Emisión Finiquito",
        "carta_instrucciones_numero_oficio": "Número Oficio Carta Instrucciones",
        "carta_instrucciones_fecha_constancia_liquidacion": "Fecha Constancia Liquidación",
        "carta_instrucciones_nombre_titular_credito": "Nombre Titular del Crédito",
        "carta_instrucciones_numero_credito": "Número de Crédito",
        "carta_instrucciones_tipo_credito": "Tipo de Crédito",
        "carta_instrucciones_fecha_adjudicacion": "Fecha de Adjudicación",
        "carta_instrucciones_ubicacion_inmueble": "Ubicación Inmueble (Carta)",
        "carta_instrucciones_valor_credito": "Valor del Crédito",
        "carta_instrucciones_valor_credito_letras": "Valor del Crédito (letras)",
        "carta_instrucciones_numero_registro": "Número de Registro (Carta)",
        "carta_instrucciones_tomo": "Tomo (Carta)",
    }

    # Construir lista de campos
    fields = []
    for key, description in CLAVES_ESTANDARIZADAS_LEGACY.items():
        fields.append({
            "name": key,
            "label": label_mapping.get(key, key.replace("_", " ").title()),
            "type": "text",
            "category": category_mapping.get(key, "Otros Datos"),
            "help": description,
            "required": key in ["deudor", "intermediario_financiero", "suma_credito"],
            "optional": key not in ["deudor", "intermediario_financiero", "suma_credito"],
            "source": "documento"
        })

    # Obtener categorías únicas en orden
    categories_order = [
        "Datos Generales",
        "Datos de la Escritura",
        "Datos del Registro",
        "Datos del Crédito",
        "Cesión de Crédito",
        "Constancia de Finiquito",
        "Carta de Instrucciones"
    ]

    logger.info(
        "Campos LEGACY de cancelación obtenidos",
        total_fields=len(fields),
        categories=len(categories_order)
    )

    return {
        "document_type": "cancelacion",
        "fields": fields,
        "categories": categories_order,
        "total_fields": len(fields),
        "source": "movil_cancelaciones.py (CLAVES_ESTANDARIZADAS_LEGACY)",
        "note": "Usar con endpoint POST /api/cancelaciones/legacy/extract"
    }
