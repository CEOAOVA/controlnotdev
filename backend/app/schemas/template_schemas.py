"""
ControlNot v2 - Template Schemas
Schemas para upload y procesamiento de templates Word

Basado en por_partes.py líneas 1458-1502, 1639-1684, 1814-1854
"""
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field


class DocumentTypeEnum(str, Enum):
    """
    Tipos de documento soportados

    Basado en por_partes.py líneas 1363-1384
    """
    COMPRAVENTA = "compraventa"
    DONACION = "donacion"
    TESTAMENTO = "testamento"
    PODER = "poder"
    SOCIEDAD = "sociedad"


class TemplateUploadResponse(BaseModel):
    """
    Respuesta al subir un template

    Confirma que el template fue recibido y procesado

    Example:
        {
            "template_id": "tpl_abc123",
            "template_name": "Compraventa_Lote_2025.docx",
            "size_bytes": 45678,
            "message": "Template recibido exitosamente"
        }
    """
    template_id: str = Field(..., description="ID único del template")
    template_name: str = Field(..., description="Nombre del archivo .docx")
    size_bytes: int = Field(..., description="Tamaño del archivo en bytes", ge=0)
    message: str = Field(..., description="Mensaje de confirmación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "tpl_abc123",
                    "template_name": "Compraventa_Lote_2025.docx",
                    "size_bytes": 45678,
                    "message": "Template recibido y procesando..."
                }
            ]
        }
    }


class PlaceholderExtractionResponse(BaseModel):
    """
    Resultado de extraer placeholders de un template

    Basado en por_partes.py líneas 1660-1665

    Retorna:
    - Lista de placeholders encontrados
    - Tipo de documento auto-detectado
    - Mapeo de placeholders a claves estándar

    Example:
        {
            "template_id": "tpl_abc123",
            "template_name": "Compraventa_Lote_2025.docx",
            "document_type": "compraventa",
            "placeholders": [
                "Certificado_Registro_Catastral",
                "Comprobante_Domicilio_Parte_Vendedora",
                "CURP_Parte_Compradora"
            ],
            "placeholder_mapping": {
                "Vendedor": "Parte_Vendedora_Nombre_Completo",
                "Comprador": "Parte_Compradora_Nombre_Completo"
            },
            "total_placeholders": 52
        }
    """
    template_id: str = Field(..., description="ID único del template")
    template_name: str = Field(..., description="Nombre del archivo")
    document_type: DocumentTypeEnum = Field(
        ...,
        description="Tipo de documento auto-detectado"
    )
    placeholders: List[str] = Field(
        ...,
        description="Lista ordenada de placeholders encontrados",
        min_length=1
    )
    placeholder_mapping: Dict[str, str] = Field(
        ...,
        description="Mapeo de placeholders a claves estándar del modelo"
    )
    total_placeholders: int = Field(
        ...,
        description="Cantidad total de placeholders",
        ge=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "tpl_abc123",
                    "template_name": "Compraventa_Lote.docx",
                    "document_type": "compraventa",
                    "placeholders": [
                        "Parte_Vendedora_Nombre_Completo",
                        "RFC_Parte_Compradora",
                        "Precio_Venta"
                    ],
                    "placeholder_mapping": {
                        "Vendedor_Nombre": "Parte_Vendedora_Nombre_Completo",
                        "Comprador_RFC": "RFC_Parte_Compradora"
                    },
                    "total_placeholders": 47
                }
            ]
        }
    }


class TemplateConfirmRequest(BaseModel):
    """
    Usuario confirma el template y tipo de documento

    Permite al usuario cambiar el tipo auto-detectado si es necesario

    Example:
        {
            "template_id": "tpl_abc123",
            "document_type": "compraventa",
            "confirmed": true
        }
    """
    template_id: str = Field(..., description="ID del template a confirmar")
    document_type: DocumentTypeEnum = Field(
        ...,
        description="Tipo de documento (puede ser diferente al auto-detectado)"
    )
    confirmed: bool = Field(
        ...,
        description="Confirmación del usuario (debe ser true)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "tpl_abc123",
                    "document_type": "compraventa",
                    "confirmed": True
                }
            ]
        }
    }


class TemplateInfo(BaseModel):
    """
    Información de un template individual

    Puede venir de Google Drive o almacenamiento local

    Basado en por_partes.py líneas 1814-1854

    Example:
        {
            "id": "1abc...xyz",
            "name": "Compraventa_Template.docx",
            "size": 45678,
            "modified": "2024-01-15T10:30:00Z",
            "source": "drive"
        }
    """
    id: str = Field(..., description="ID del template (file_id de Drive o nombre de archivo)")
    name: str = Field(..., description="Nombre del archivo .docx")
    size: int = Field(..., description="Tamaño en bytes", ge=0)
    modified: str = Field(..., description="Fecha de última modificación (ISO 8601)")
    source: str = Field(
        ...,
        description="Fuente del template",
        pattern="^(drive|local|supabase)$"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1abc...xyz",
                    "name": "Compraventa_Template.docx",
                    "size": 45678,
                    "modified": "2025-01-15T10:30:00Z",
                    "source": "drive"
                }
            ]
        }
    }


class TemplateListResponse(BaseModel):
    """
    Lista de templates disponibles

    Combina templates de Google Drive y almacenamiento local

    Example:
        {
            "templates": [
                {
                    "id": "1abc...xyz",
                    "name": "Compraventa_2025.docx",
                    "size": 45678,
                    "modified": "2025-01-15T10:30:00Z",
                    "source": "drive"
                },
                {
                    "id": "Donacion_Template.docx",
                    "name": "Donacion_Template.docx",
                    "size": 34567,
                    "modified": "2025-01-10T09:00:00Z",
                    "source": "local"
                }
            ],
            "total_count": 2,
            "sources": {
                "drive": 1,
                "local": 1
            }
        }
    """
    templates: List[TemplateInfo] = Field(..., description="Lista de templates")
    total_count: int = Field(..., description="Cantidad total de templates", ge=0)
    sources: Dict[str, int] = Field(
        ...,
        description="Conteo de templates por fuente"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "templates": [
                        {
                            "id": "1abc",
                            "name": "Compraventa.docx",
                            "size": 45678,
                            "modified": "2025-01-15T10:30:00Z",
                            "source": "drive"
                        }
                    ],
                    "total_count": 5,
                    "sources": {
                        "drive": 3,
                        "local": 2
                    }
                }
            ]
        }
    }


class DocumentTypeInfo(BaseModel):
    """
    Información de un tipo de documento

    Example:
        {
            "id": "compraventa",
            "nombre": "Compraventa",
            "descripcion": "Contrato de compraventa de bienes inmuebles",
            "total_fields": 47
        }
    """
    id: str = Field(..., description="ID del tipo de documento")
    nombre: str = Field(..., description="Nombre amigable del tipo")
    descripcion: Optional[str] = Field(None, description="Descripción del tipo")
    total_fields: int = Field(..., description="Total de campos del modelo", ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "compraventa",
                    "nombre": "Compraventa",
                    "descripcion": "Contrato de compraventa de bienes inmuebles",
                    "total_fields": 47
                }
            ]
        }
    }


class DocumentTypesResponse(BaseModel):
    """
    Lista de todos los tipos de documento soportados

    Example:
        {
            "document_types": [
                {
                    "id": "compraventa",
                    "nombre": "Compraventa",
                    "descripcion": "Contrato de compraventa...",
                    "total_fields": 47
                },
                {
                    "id": "donacion",
                    "nombre": "Donación",
                    "descripcion": "Contrato de donación...",
                    "total_fields": 49
                }
            ],
            "total_types": 5
        }
    """
    document_types: List[DocumentTypeInfo] = Field(
        ...,
        description="Lista de tipos de documento"
    )
    total_types: int = Field(..., description="Cantidad total de tipos", ge=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_types": [
                        {
                            "id": "compraventa",
                            "nombre": "Compraventa",
                            "descripcion": "Contrato de compraventa de bienes inmuebles",
                            "total_fields": 47
                        },
                        {
                            "id": "donacion",
                            "nombre": "Donación",
                            "descripcion": "Contrato de donación de bienes inmuebles",
                            "total_fields": 49
                        }
                    ],
                    "total_types": 5
                }
            ]
        }
    }
