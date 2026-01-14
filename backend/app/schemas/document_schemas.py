"""
ControlNot v2 - Document Schemas
Schemas para categorización y generación de documentos

Basado en por_partes.py líneas 1688-1743, 1959-2182, 2184-2291
"""
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
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
            "required": true,
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
    required: bool = Field(default=True, description="Si la categoría es obligatoria para el tipo de documento")
    documentos: List[str] = Field(..., description="Documentos esperados en esta categoría")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Documentos del Vendedor",
                    "icono": "📤",
                    "descripcion": "Documentos de identificación y propiedad del vendedor",
                    "required": True,
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


# ===== SCHEMAS PARA HISTORIAL DE DOCUMENTOS =====

class DocumentListItem(BaseModel):
    """
    Item individual en la lista de documentos

    Representa un documento generado almacenado en la base de datos
    """
    id: str = Field(..., description="UUID del documento")
    nombre_documento: str = Field(..., description="Nombre del documento")
    tipo_documento: str = Field(..., description="Tipo de documento (compraventa, donacion, etc.)")
    estado: str = Field(..., description="Estado del documento (borrador, procesando, completado, etc.)")
    created_at: datetime = Field(..., description="Fecha de creación")
    storage_path: Optional[str] = Field(None, description="Ruta en Supabase Storage")
    confidence_score: Optional[float] = Field(None, description="Score de confianza de la extracción")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "nombre_documento": "Compraventa_Lote_145.docx",
                    "tipo_documento": "compraventa",
                    "estado": "completado",
                    "created_at": "2024-01-15T10:30:00Z",
                    "storage_path": "documentos/tenant_123/doc_abc.docx",
                    "confidence_score": 0.95
                }
            ]
        }
    }


class DocumentListResponse(BaseModel):
    """
    Respuesta paginada de lista de documentos

    Usada por GET /api/documents
    """
    documents: List[DocumentListItem] = Field(..., description="Lista de documentos")
    total: int = Field(..., description="Total de documentos en la base de datos")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Documentos por página")
    total_pages: int = Field(..., description="Total de páginas")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "documents": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "nombre_documento": "Compraventa_Lote_145.docx",
                            "tipo_documento": "compraventa",
                            "estado": "completado",
                            "created_at": "2024-01-15T10:30:00Z",
                            "storage_path": "documentos/tenant_123/doc_abc.docx"
                        }
                    ],
                    "total": 42,
                    "page": 1,
                    "per_page": 25,
                    "total_pages": 2
                }
            ]
        }
    }


class DocumentStatsResponse(BaseModel):
    """
    Estadísticas de documentos del tenant

    Usada por GET /api/documents/stats
    """
    total_documents: int = Field(..., description="Total de documentos")
    by_type: Dict[str, int] = Field(..., description="Conteo por tipo de documento")
    by_status: Dict[str, int] = Field(..., description="Conteo por estado")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_documents": 42,
                    "by_type": {
                        "compraventa": 25,
                        "donacion": 8,
                        "testamento": 5,
                        "poder": 4
                    },
                    "by_status": {
                        "completado": 30,
                        "borrador": 10,
                        "error": 2
                    }
                }
            ]
        }
    }


class GetDocumentResponse(BaseModel):
    """
    Detalle completo de un documento

    Usada por GET /api/documents/{document_id}
    """
    id: str = Field(..., description="UUID del documento")
    tenant_id: str = Field(..., description="UUID del tenant")
    nombre_documento: str = Field(..., description="Nombre del documento")
    tipo_documento: str = Field(..., description="Tipo de documento")
    estado: str = Field(..., description="Estado del documento")
    storage_path: Optional[str] = Field(None, description="Ruta en Storage")
    download_url: Optional[str] = Field(None, description="URL firmada para descarga")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Datos extraídos por IA")
    edited_data: Optional[Dict[str, Any]] = Field(None, description="Datos editados por usuario")
    confidence_score: Optional[float] = Field(None, description="Score de confianza")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "tenant_id": "tenant_123",
                    "nombre_documento": "Compraventa_Lote_145.docx",
                    "tipo_documento": "compraventa",
                    "estado": "completado",
                    "storage_path": "documentos/tenant_123/doc_abc.docx",
                    "download_url": "https://...",
                    "extracted_data": {"Parte_Vendedora": "RAUL CERVANTES"},
                    "confidence_score": 0.95,
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }


# ===== SCHEMAS PARA PREVIEW DE DOCUMENTO =====

class DocumentPreviewRequest(BaseModel):
    """
    Solicitud para generar preview del documento antes de la generación final

    El preview permite al usuario ver cómo quedará el documento
    con los datos extraídos antes de confirmar la generación.
    """
    template_id: str = Field(..., description="ID del template a usar")
    data: Dict[str, str] = Field(
        ...,
        description="Diccionario con valores para cada placeholder"
    )
    session_id: Optional[str] = Field(
        None,
        description="ID de sesión opcional para tracking"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "tpl_abc123",
                    "data": {
                        "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
                        "RFC_Parte_Vendedora": "CEAR640813JJ8",
                        "Edad_Parte_Vendedora": "sesenta años"
                    },
                    "session_id": "session_xyz789"
                }
            ]
        }
    }


class DocumentPreviewResponse(BaseModel):
    """
    Respuesta del preview del documento

    Incluye el contenido HTML renderizado del documento
    y estadísticas sobre los placeholders.

    El HTML permite mostrar una vista previa en el frontend
    sin necesidad de generar el documento final.
    """
    html_content: str = Field(
        ...,
        description="Contenido HTML renderizado del documento"
    )
    total_placeholders: int = Field(
        ...,
        description="Total de placeholders en el template",
        ge=0
    )
    filled_placeholders: int = Field(
        ...,
        description="Placeholders con valor asignado",
        ge=0
    )
    fill_percentage: float = Field(
        ...,
        description="Porcentaje de completitud (0-100)",
        ge=0,
        le=100
    )
    missing_placeholders: List[str] = Field(
        default_factory=list,
        description="Lista de placeholders sin valor"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Advertencias sobre campos incompletos o sospechosos"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "html_content": "<div class='document'>...</div>",
                    "total_placeholders": 50,
                    "filled_placeholders": 47,
                    "fill_percentage": 94.0,
                    "missing_placeholders": [
                        "Escritura_Antecedente_Fecha",
                        "Valor_Catastral",
                        "Certificado_Libertad_Gravamen"
                    ],
                    "warnings": [
                        "Campo 'RFC_Parte_Vendedora' parece tener formato incorrecto"
                    ]
                }
            ]
        }
    }
