"""
ControlNot v2 - Document Schemas
Schemas para categorización y generación de documentos

Basado en por_partes.py líneas 1688-1743, 1959-2182, 2184-2291
"""
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.template_schemas import DocumentTypeEnum


class CategoryEnum(str, Enum):
    """
    Categorías de documentos por rol

    Basado en por_partes.py líneas 1959-2182
    """
    PARTE_A = "parte_a"  # Vendedor, Donador, Testador, Otorgante, Socios
    PARTE_B = "parte_b"  # Comprador, Donatario, Herederos, Apoderado, Administradores
    OTROS = "otros"      # Documentos del inmueble, patrimonio, corporativos


class CategoryInfo(BaseModel):
    """
    Información de una categoría de documentos

    Cada tipo de documento tiene 3 categorías con nombres dinámicos

    Basado en categories.json y por_partes.py líneas 1959-2182

    Example:
        {
            "nombre": "Documentos del Vendedor",
            "icono": "📤",
            "descripcion": "Documentos de identificación y propiedad del vendedor",
            "documentos": [
                "INE/IFE del Vendedor",
                "Acta de Nacimiento del Vendedor",
                "CURP del Vendedor"
            ]
        }
    """
    nombre: str = Field(..., description="Nombre de la categoría")
    icono: str = Field(..., description="Emoji icono de la categoría")
    descripcion: str = Field(..., description="Descripción de la categoría")
    documentos: List[str] = Field(..., description="Documentos esperados en esta categoría")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Documentos del Vendedor",
                    "icono": "📤",
                    "descripcion": "Documentos de identificación y propiedad del vendedor",
                    "documentos": [
                        "INE/IFE del Vendedor",
                        "Acta de Nacimiento del Vendedor",
                        "CURP del Vendedor",
                        "RFC/Constancia SAT del Vendedor"
                    ]
                }
            ]
        }
    }


class CategoriesResponse(BaseModel):
    """
    Las 3 categorías para un tipo de documento

    Basado en por_partes.py función categorize_documents_by_role()

    Example:
        {
            "parte_a": {
                "nombre": "Documentos del Vendedor",
                "icono": "📤",
                "descripcion": "...",
                "documentos": [...]
            },
            "parte_b": {
                "nombre": "Documentos del Comprador",
                "icono": "📥",
                "descripcion": "...",
                "documentos": [...]
            },
            "otros": {
                "nombre": "Documentos del Inmueble",
                "icono": "📋",
                "descripcion": "...",
                "documentos": [...]
            },
            "document_type": "compraventa"
        }
    """
    parte_a: CategoryInfo = Field(..., description="Primera categoría (Vendedor, Donador, etc.)")
    parte_b: CategoryInfo = Field(..., description="Segunda categoría (Comprador, Donatario, etc.)")
    otros: CategoryInfo = Field(..., description="Tercera categoría (Inmueble, Patrimonio, etc.)")
    document_type: DocumentTypeEnum = Field(..., description="Tipo de documento")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "parte_a": {
                        "nombre": "Documentos del Vendedor",
                        "icono": "📤",
                        "descripcion": "Documentos de identificación del vendedor",
                        "documentos": ["INE/IFE", "CURP", "RFC"]
                    },
                    "parte_b": {
                        "nombre": "Documentos del Comprador",
                        "icono": "📥",
                        "descripcion": "Documentos de identificación del comprador",
                        "documentos": ["INE/IFE", "CURP", "RFC"]
                    },
                    "otros": {
                        "nombre": "Documentos del Inmueble",
                        "icono": "📋",
                        "descripcion": "Documentación legal del inmueble",
                        "documentos": ["Escritura Antecedente", "Certificado Catastral"]
                    },
                    "document_type": "compraventa"
                }
            ]
        }
    }


class DocumentGenerationRequest(BaseModel):
    """
    Solicitud para generar documento final

    Basado en por_partes.py líneas 1688-1743

    Example:
        {
            "template_id": "tpl_abc123",
            "responses": {
                "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                "RFC_Parte_Vendedora": "CEAR640813JJ8",
                "Edad_Parte_Vendedora": "sesenta años"
            },
            "placeholders": [
                "Parte_Vendedora_Nombre_Completo",
                "RFC_Parte_Vendedora",
                "Edad_Parte_Vendedora"
            ],
            "output_filename": "Compraventa_Lote_145"
        }
    """
    template_id: str = Field(..., description="ID del template a usar")
    responses: Dict[str, str] = Field(
        ...,
        description="Diccionario con valores para cada placeholder"
    )
    placeholders: List[str] = Field(
        ...,
        description="Lista de placeholders del template",
        min_length=1
    )
    output_filename: str = Field(
        ...,
        description="Nombre del archivo de salida (sin extensión)",
        min_length=1,
        max_length=100
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "tpl_abc123",
                    "responses": {
                        "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                        "RFC_Parte_Vendedora": "CEAR640813JJ8",
                        "CURP_Parte_Vendedora": "CEAR640813HMNRRL02",
                        "Edad_Parte_Vendedora": "sesenta años"
                    },
                    "placeholders": [
                        "Parte_Vendedora_Nombre_Completo",
                        "RFC_Parte_Vendedora",
                        "CURP_Parte_Vendedora"
                    ],
                    "output_filename": "Compraventa_Lote_145_Final"
                }
            ]
        }
    }


class DocumentGenerationStats(BaseModel):
    """
    Estadísticas del proceso de generación

    Basado en por_partes.py línea 1738 y document_service.py

    Example:
        {
            "placeholders_replaced": 47,
            "placeholders_missing": 3,
            "missing_list": [
                "Escritura_Antecedente_Fecha",
                "Valor_Catastral",
                "Certificado_Libertad_Gravamen"
            ],
            "replaced_in_body": 30,
            "replaced_in_tables": 15,
            "replaced_in_headers": 1,
            "replaced_in_footers": 1,
            "bold_conversions": 12
        }
    """
    placeholders_replaced: int = Field(..., description="Placeholders reemplazados", ge=0)
    placeholders_missing: int = Field(..., description="Placeholders no encontrados", ge=0)
    missing_list: List[str] = Field(
        default_factory=list,
        description="Lista de placeholders que no se encontraron"
    )
    replaced_in_body: int = Field(default=0, description="Reemplazos en párrafos del body", ge=0)
    replaced_in_tables: int = Field(default=0, description="Reemplazos en tablas", ge=0)
    replaced_in_headers: int = Field(default=0, description="Reemplazos en headers", ge=0)
    replaced_in_footers: int = Field(default=0, description="Reemplazos en footers", ge=0)
    bold_conversions: int = Field(default=0, description="Conversiones de **negrita**", ge=0)


class DocumentGenerationResponse(BaseModel):
    """
    Resultado de la generación de documento

    Incluye URL de descarga y estadísticas

    Example:
        {
            "success": true,
            "document_id": "doc_789",
            "filename": "Compraventa_Lote_145.docx",
            "download_url": "/api/documents/download/doc_789",
            "size_bytes": 45678,
            "stats": {
                "placeholders_replaced": 47,
                "placeholders_missing": 3,
                "missing_list": ["Escritura_Antecedente_Fecha"]
            },
            "message": "Documento generado: 47 de 50 placeholders reemplazados"
        }
    """
    success: bool = Field(..., description="Si la generación fue exitosa")
    document_id: str = Field(..., description="ID único del documento generado")
    filename: str = Field(..., description="Nombre del archivo generado")
    download_url: str = Field(..., description="URL para descargar el documento")
    size_bytes: int = Field(..., description="Tamaño del documento en bytes", ge=0)
    stats: DocumentGenerationStats = Field(..., description="Estadísticas de generación")
    message: str = Field(..., description="Mensaje descriptivo del resultado")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "filename": "Compraventa_Lote_145.docx",
                    "download_url": "/api/documents/download/doc_789",
                    "size_bytes": 45678,
                    "stats": {
                        "placeholders_replaced": 47,
                        "placeholders_missing": 3,
                        "missing_list": [
                            "Escritura_Antecedente_Fecha",
                            "Valor_Catastral"
                        ],
                        "replaced_in_body": 30,
                        "replaced_in_tables": 15,
                        "replaced_in_headers": 1,
                        "replaced_in_footers": 1,
                        "bold_conversions": 12
                    },
                    "message": "Documento generado: 47 de 50 placeholders reemplazados"
                }
            ]
        }
    }


class UploadedFileInfo(BaseModel):
    """
    Información de un archivo subido por categoría

    Example:
        {
            "filename": "INE_vendedor.jpg",
            "size_bytes": 234567,
            "content_type": "image/jpeg",
            "category": "parte_a"
        }
    """
    filename: str = Field(..., description="Nombre del archivo")
    size_bytes: int = Field(..., description="Tamaño en bytes", ge=0)
    content_type: str = Field(..., description="MIME type del archivo")
    category: CategoryEnum = Field(..., description="Categoría asignada")


class CategorizedDocumentsUploadResponse(BaseModel):
    """
    Confirmación de upload de documentos categorizados

    Basado en por_partes.py líneas 2184-2291

    Example:
        {
            "session_id": "session_xyz789",
            "files_received": {
                "parte_a": 3,
                "parte_b": 2,
                "otros": 4
            },
            "total_files": 9,
            "files": [
                {
                    "filename": "INE_vendedor.jpg",
                    "size_bytes": 234567,
                    "content_type": "image/jpeg",
                    "category": "parte_a"
                }
            ],
            "message": "9 archivos recibidos y listos para procesar"
        }
    """
    session_id: str = Field(..., description="ID de sesión para trackear el proceso")
    files_received: Dict[str, int] = Field(
        ...,
        description="Cantidad de archivos por categoría"
    )
    total_files: int = Field(..., description="Total de archivos recibidos", ge=0)
    files: List[UploadedFileInfo] = Field(
        ...,
        description="Lista de archivos con su info"
    )
    message: str = Field(..., description="Mensaje de confirmación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session_xyz789",
                    "files_received": {
                        "parte_a": 3,
                        "parte_b": 2,
                        "otros": 4
                    },
                    "total_files": 9,
                    "files": [
                        {
                            "filename": "INE_vendedor.jpg",
                            "size_bytes": 234567,
                            "content_type": "image/jpeg",
                            "category": "parte_a"
                        }
                    ],
                    "message": "9 archivos recibidos, iniciando procesamiento..."
                }
            ]
        }
    }
