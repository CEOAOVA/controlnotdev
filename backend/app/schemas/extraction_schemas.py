"""
ControlNot v2 - Extraction Schemas
Schemas para OCR y extracción con IA

Basado en por_partes.py líneas 1745-1789, 1856-1866, 2293-2335
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.schemas.template_schemas import DocumentTypeEnum
from app.schemas.document_schemas import CategoryEnum


class OCRFileResult(BaseModel):
    """
    Resultado de OCR de un archivo individual

    Example:
        {
            "file_name": "INE_vendedor.jpg",
            "category": "parte_a",
            "text": "INSTITUTO NACIONAL ELECTORAL\\nNOMBRE: RAUL CERVANTES AREVALO...",
            "text_length": 1234,
            "success": true,
            "error": null
        }
    """
    file_name: str = Field(..., description="Nombre del archivo procesado")
    category: CategoryEnum = Field(..., description="Categoría del documento")
    text: str = Field(..., description="Texto extraído del OCR")
    text_length: int = Field(..., description="Longitud del texto extraído", ge=0)
    success: bool = Field(..., description="Si el OCR fue exitoso")
    error: Optional[str] = Field(None, description="Mensaje de error si falló")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_name": "INE_vendedor.jpg",
                    "category": "parte_a",
                    "text": "INSTITUTO NACIONAL ELECTORAL\nNOMBRE: RAUL CERVANTES AREVALO\nCURP: CEAR640813HMNRRL02",
                    "text_length": 1234,
                    "success": True,
                    "error": None
                }
            ]
        }
    }


class OCRResponse(BaseModel):
    """
    Respuesta completa del procesamiento OCR paralelo

    Basado en por_partes.py líneas 2306-2333
    MEJORA: Ahora incluye tiempos de procesamiento async

    Example:
        {
            "session_id": "session_xyz789",
            "extracted_text": "===CATEGORÍA: VENDEDOR===\\n...",
            "total_text_length": 10543,
            "files_processed": 9,
            "files_success": 8,
            "files_failed": 1,
            "processing_time_seconds": 6.8,
            "results_by_category": {
                "parte_a": [
                    {
                        "file_name": "INE_vendedor.jpg",
                        "text": "...",
                        "success": true
                    }
                ]
            }
        }
    """
    session_id: str = Field(..., description="ID de sesión del procesamiento")
    extracted_text: str = Field(
        ...,
        description="Texto consolidado de todos los documentos"
    )
    total_text_length: int = Field(
        ...,
        description="Longitud total del texto extraído",
        ge=0
    )
    files_processed: int = Field(..., description="Total de archivos procesados", ge=0)
    files_success: int = Field(..., description="Archivos procesados exitosamente", ge=0)
    files_failed: int = Field(..., description="Archivos que fallaron", ge=0)
    processing_time_seconds: float = Field(
        ...,
        description="Tiempo total de procesamiento (async paralelo)",
        ge=0
    )
    results_by_category: Dict[str, List[OCRFileResult]] = Field(
        ...,
        description="Resultados detallados por categoría"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session_xyz789",
                    "extracted_text": "===CATEGORÍA: DOCUMENTOS DEL VENDEDOR===\n--- DOC 1: INE_vendedor.jpg ---\n[texto OCR...]",
                    "total_text_length": 10543,
                    "files_processed": 9,
                    "files_success": 8,
                    "files_failed": 1,
                    "processing_time_seconds": 6.8,
                    "results_by_category": {
                        "parte_a": [
                            {
                                "file_name": "INE_vendedor.jpg",
                                "category": "parte_a",
                                "text": "INSTITUTO NACIONAL ELECTORAL...",
                                "text_length": 1234,
                                "success": True,
                                "error": None
                            }
                        ],
                        "parte_b": [],
                        "otros": []
                    }
                }
            ]
        }
    }


class AIExtractionRequest(BaseModel):
    """
    Solicitud de extracción con IA

    Basado en por_partes.py líneas 1745-1789

    Example:
        {
            "session_id": "session_xyz789",
            "text": "===CATEGORÍA: VENDEDOR===\\n...",
            "document_type": "compraventa",
            "template_placeholders": [
                "Parte_Vendedora_Nombre_Completo",
                "RFC_Parte_Vendedora"
            ],
            "model": "openai/gpt-4o"
        }
    """
    session_id: str = Field(..., description="ID de sesión")
    text: str = Field(
        ...,
        description="Texto del OCR para extraer datos",
        min_length=10
    )
    document_type: DocumentTypeEnum = Field(
        ...,
        description="Tipo de documento para determinar qué extraer"
    )
    template_placeholders: Optional[List[str]] = Field(
        None,
        description="Placeholders del template para guiar la extracción"
    )
    model: Optional[str] = Field(
        None,
        description="Modelo específico a usar (ej: 'openai/gpt-4o', 'anthropic/claude-3-opus')"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session_xyz789",
                    "text": "===CATEGORÍA: VENDEDOR===\nINSTITUTO NACIONAL ELECTORAL\nNOMBRE: RAUL CERVANTES AREVALO\nCURP: CEAR640813HMNRRL02\nRFC: CEAR640813JJ8",
                    "document_type": "compraventa",
                    "template_placeholders": [
                        "Parte_Vendedora_Nombre_Completo",
                        "RFC_Parte_Vendedora",
                        "CURP_Parte_Vendedora"
                    ],
                    "model": "openai/gpt-4o"
                }
            ]
        }
    }


class AIExtractionResponse(BaseModel):
    """
    Datos extraídos por la IA

    Basado en por_partes.py líneas 1776-1788

    Example:
        {
            "session_id": "session_xyz789",
            "extracted_data": {
                "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                "RFC_Parte_Vendedora": "CEAR640813JJ8",
                "CURP_Parte_Vendedora": "CEAR640813HMNRRL02"
            },
            "total_keys": 50,
            "keys_found": 47,
            "keys_missing": 3,
            "missing_list": [
                "Escritura_Antecedente_Fecha",
                "Valor_Catastral"
            ],
            "completeness_percent": 94.0,
            "model_used": "openai/gpt-4o",
            "tokens_used": 2847,
            "processing_time_seconds": 3.2
        }
    """
    session_id: str = Field(..., description="ID de sesión")
    extracted_data: Dict[str, str] = Field(
        ...,
        description="Datos extraídos (key: value)"
    )
    total_keys: int = Field(..., description="Total de claves del modelo", ge=0)
    keys_found: int = Field(..., description="Claves encontradas", ge=0)
    keys_missing: int = Field(..., description="Claves no encontradas", ge=0)
    missing_list: List[str] = Field(
        ...,
        description="Lista de claves no encontradas"
    )
    completeness_percent: float = Field(
        ...,
        description="Porcentaje de completitud (0-100)",
        ge=0,
        le=100
    )
    model_used: str = Field(..., description="Modelo de IA usado")
    tokens_used: int = Field(..., description="Tokens consumidos", ge=0)
    processing_time_seconds: float = Field(
        ...,
        description="Tiempo de procesamiento",
        ge=0
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session_xyz789",
                    "extracted_data": {
                        "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                        "RFC_Parte_Vendedora": "CEAR640813JJ8",
                        "CURP_Parte_Vendedora": "CEAR640813HMNRRL02",
                        "Edad_Parte_Vendedora": "sesenta años"
                    },
                    "total_keys": 50,
                    "keys_found": 47,
                    "keys_missing": 3,
                    "missing_list": [
                        "Escritura_Antecedente_Fecha",
                        "Valor_Catastral",
                        "Certificado_Libertad_Gravamen"
                    ],
                    "completeness_percent": 94.0,
                    "model_used": "openai/gpt-4o",
                    "tokens_used": 2847,
                    "processing_time_seconds": 3.2
                }
            ]
        }
    }


class DataEditRequest(BaseModel):
    """
    Usuario edita/confirma los datos extraídos

    El usuario puede corregir datos antes de generar el documento

    Example:
        {
            "session_id": "session_xyz789",
            "edited_data": {
                "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                "RFC_Parte_Vendedora": "CEAR640813JJ8",
                "Edad_Parte_Vendedora": "sesenta y un años"
            },
            "confirmed": true
        }
    """
    session_id: str = Field(..., description="ID de sesión")
    edited_data: Dict[str, str] = Field(
        ...,
        description="Datos editados/confirmados por el usuario"
    )
    confirmed: bool = Field(
        ...,
        description="Confirmación del usuario (debe ser true para continuar)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session_xyz789",
                    "edited_data": {
                        "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                        "RFC_Parte_Vendedora": "CEAR640813JJ8",
                        "CURP_Parte_Vendedora": "CEAR640813HMNRRL02",
                        "Edad_Parte_Vendedora": "sesenta y un años"
                    },
                    "confirmed": True
                }
            ]
        }
    }


class ModelInfo(BaseModel):
    """
    Información de un modelo de IA disponible

    Example:
        {
            "id": "openai/gpt-4o",
            "name": "GPT-4o (OpenAI via OpenRouter)",
            "provider": "openai",
            "supports_json": true,
            "max_tokens": 4096,
            "recommended": true
        }
    """
    id: str = Field(..., description="ID del modelo (para usar en requests)")
    name: str = Field(..., description="Nombre amigable del modelo")
    provider: str = Field(..., description="Proveedor (openai, anthropic, google, meta)")
    supports_json: bool = Field(..., description="Si soporta JSON mode")
    max_tokens: int = Field(..., description="Máximo de tokens de output", ge=0)
    recommended: bool = Field(
        default=False,
        description="Si es el modelo recomendado"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "openai/gpt-4o",
                    "name": "GPT-4o (OpenAI via OpenRouter)",
                    "provider": "openai",
                    "supports_json": True,
                    "max_tokens": 4096,
                    "recommended": True
                }
            ]
        }
    }


class ModelsListResponse(BaseModel):
    """
    Lista de modelos de IA disponibles

    Depende de la configuración (OpenRouter vs OpenAI directo)

    Example:
        {
            "models": [
                {
                    "id": "openai/gpt-4o",
                    "name": "GPT-4o",
                    "provider": "openai",
                    "recommended": true
                },
                {
                    "id": "anthropic/claude-3-opus",
                    "name": "Claude 3 Opus",
                    "provider": "anthropic",
                    "recommended": false
                }
            ],
            "total_models": 5,
            "using_openrouter": true,
            "default_model": "openai/gpt-4o"
        }
    """
    models: List[ModelInfo] = Field(..., description="Lista de modelos disponibles")
    total_models: int = Field(..., description="Cantidad total de modelos", ge=1)
    using_openrouter: bool = Field(
        ...,
        description="Si está usando OpenRouter (multi-provider) o OpenAI directo"
    )
    default_model: str = Field(..., description="Modelo por defecto configurado")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "models": [
                        {
                            "id": "openai/gpt-4o",
                            "name": "GPT-4o (OpenAI via OpenRouter)",
                            "provider": "openai",
                            "supports_json": True,
                            "max_tokens": 4096,
                            "recommended": True
                        },
                        {
                            "id": "anthropic/claude-3-opus",
                            "name": "Claude 3 Opus (Anthropic)",
                            "provider": "anthropic",
                            "supports_json": True,
                            "max_tokens": 4096,
                            "recommended": False
                        }
                    ],
                    "total_models": 5,
                    "using_openrouter": True,
                    "default_model": "openai/gpt-4o"
                }
            ]
        }
    }
