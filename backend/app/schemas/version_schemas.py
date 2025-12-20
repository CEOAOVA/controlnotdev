"""
ControlNot v2 - Template Version Schemas
Schemas para gestión de versiones de templates

Sistema de versionamiento para tracking de cambios en templates .docx
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TemplateVersionCreate(BaseModel):
    """
    Request para crear una nueva versión de template

    Example:
        {
            "notas": "Actualizado formato de fechas"
        }
    """
    notas: Optional[str] = Field(
        None,
        description="Notas descriptivas del cambio en esta versión",
        max_length=500
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "notas": "Actualizado formato de fechas y agregado campo RFC"
                }
            ]
        }
    }


class TemplateVersionResponse(BaseModel):
    """
    Información completa de una versión de template

    Example:
        {
            "id": "uuid-version",
            "template_id": "uuid-template",
            "version_number": 2,
            "storage_path": "tenant-id/template-id_v2.docx",
            "placeholders": ["vendedor", "comprador"],
            "placeholder_mapping": {"Vendedor_Nombre": "vendedor"},
            "es_activa": true,
            "created_at": "2025-01-15T10:30:00Z",
            "notas": "Versión con nuevos campos"
        }
    """
    id: str = Field(..., description="UUID de la versión")
    template_id: str = Field(..., description="UUID del template padre")
    version_number: int = Field(..., description="Número secuencial de versión", ge=1)
    storage_path: str = Field(..., description="Path en Supabase Storage")
    placeholders: List[str] = Field(
        default_factory=list,
        description="Lista de placeholders en esta versión"
    )
    placeholder_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapeo de placeholders a claves estándar"
    )
    es_activa: bool = Field(..., description="Si esta es la versión activa del template")
    created_at: datetime = Field(..., description="Fecha de creación de la versión")
    created_by: Optional[str] = Field(None, description="UUID del usuario que creó la versión")
    notas: Optional[str] = Field(None, description="Notas descriptivas de la versión")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "template_id": "98765432-1234-5678-9abc-def012345678",
                    "version_number": 2,
                    "storage_path": "tenant-123/template-456_v2.docx",
                    "placeholders": ["Vendedor_Nombre", "Comprador_RFC", "Precio_Venta"],
                    "placeholder_mapping": {
                        "vendedor_nombre": "Vendedor_Nombre",
                        "comprador_rfc": "Comprador_RFC"
                    },
                    "es_activa": True,
                    "created_at": "2025-01-15T10:30:00Z",
                    "created_by": "user-uuid-123",
                    "notas": "Agregados campos de RFC y CURP"
                }
            ]
        }
    }


class TemplateVersionListResponse(BaseModel):
    """
    Lista de versiones de un template

    Example:
        {
            "template_id": "uuid-template",
            "template_name": "Compraventa_Template.docx",
            "versions": [...],
            "total_versions": 3,
            "active_version": 2
        }
    """
    template_id: str = Field(..., description="UUID del template")
    template_name: str = Field(..., description="Nombre del template")
    versions: List[TemplateVersionResponse] = Field(
        ...,
        description="Lista de versiones ordenadas por version_number DESC"
    )
    total_versions: int = Field(..., description="Total de versiones", ge=0)
    active_version: Optional[int] = Field(
        None,
        description="Número de la versión activa actual"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "98765432-1234-5678-9abc-def012345678",
                    "template_name": "Compraventa_Template.docx",
                    "versions": [],
                    "total_versions": 3,
                    "active_version": 2
                }
            ]
        }
    }


class VersionCompareRequest(BaseModel):
    """
    Request para comparar dos versiones

    Example:
        {
            "version_id_1": "uuid-version-1",
            "version_id_2": "uuid-version-2"
        }
    """
    version_id_1: str = Field(..., description="UUID de la primera versión")
    version_id_2: str = Field(..., description="UUID de la segunda versión")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version_id_1": "a1b2c3d4-version-1",
                    "version_id_2": "e5f6g7h8-version-2"
                }
            ]
        }
    }


class VersionCompareResponse(BaseModel):
    """
    Resultado de comparar dos versiones de template

    Muestra placeholders agregados, eliminados y sin cambios

    Example:
        {
            "version_1": {"id": "...", "version_number": 1},
            "version_2": {"id": "...", "version_number": 2},
            "added_placeholders": ["RFC_Comprador"],
            "removed_placeholders": ["Cedula_Fiscal"],
            "unchanged_placeholders": ["Vendedor_Nombre", "Precio_Venta"],
            "total_changes": 2
        }
    """
    version_1: Dict = Field(..., description="Info de la versión 1")
    version_2: Dict = Field(..., description="Info de la versión 2")
    added_placeholders: List[str] = Field(
        default_factory=list,
        description="Placeholders nuevos en versión 2"
    )
    removed_placeholders: List[str] = Field(
        default_factory=list,
        description="Placeholders eliminados en versión 2"
    )
    unchanged_placeholders: List[str] = Field(
        default_factory=list,
        description="Placeholders sin cambios"
    )
    total_changes: int = Field(
        ...,
        description="Total de cambios (agregados + eliminados)",
        ge=0
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version_1": {"id": "v1-uuid", "version_number": 1},
                    "version_2": {"id": "v2-uuid", "version_number": 2},
                    "added_placeholders": ["RFC_Comprador", "CURP_Vendedor"],
                    "removed_placeholders": ["Cedula_Fiscal"],
                    "unchanged_placeholders": ["Vendedor_Nombre", "Precio_Venta"],
                    "total_changes": 3
                }
            ]
        }
    }


class ActivateVersionRequest(BaseModel):
    """
    Request para activar una versión específica

    Example:
        {
            "version_id": "uuid-version"
        }
    """
    version_id: str = Field(..., description="UUID de la versión a activar")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version_id": "a1b2c3d4-version-to-activate"
                }
            ]
        }
    }


class ActivateVersionResponse(BaseModel):
    """
    Respuesta al activar una versión

    Example:
        {
            "success": true,
            "message": "Versión 2 activada exitosamente",
            "activated_version": {...},
            "previous_active_version": 1
        }
    """
    success: bool = Field(..., description="Si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    activated_version: TemplateVersionResponse = Field(
        ...,
        description="Versión que fue activada"
    )
    previous_active_version: Optional[int] = Field(
        None,
        description="Número de la versión que estaba activa antes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Versión 2 activada exitosamente",
                    "activated_version": {},
                    "previous_active_version": 3
                }
            ]
        }
    }
