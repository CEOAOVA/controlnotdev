"""
ControlNot v2 - Response Schemas
Schemas estándar para respuestas HTTP de la API

Basado en los mensajes st.success(), st.error(), st.info() de por_partes.py
"""
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ProcessingStatusEnum(str, Enum):
    """Estados de procesamiento asíncrono"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SuccessResponse(BaseModel):
    """
    Respuesta estándar de éxito

    Usado cuando una operación se completa exitosamente

    Example:
        {
            "success": true,
            "message": "Plantilla confirmada: Compraventa_Lote.docx",
            "data": {"template_id": "tpl_123"},
            "timestamp": "2025-01-13T10:30:00"
        }
    """
    success: bool = Field(True, description="Siempre true para respuestas exitosas")
    message: str = Field(..., description="Mensaje descriptivo del éxito")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales opcionales")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp ISO 8601 de la respuesta"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Documento generado: 47 placeholders reemplazados",
                    "data": {
                        "filename": "Compraventa_Final.docx",
                        "placeholders_replaced": 47
                    },
                    "timestamp": "2025-01-13T10:30:00"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    Respuesta estándar de error

    Usado cuando una operación falla

    Example:
        {
            "success": false,
            "error": "No se detectaron placeholders en la plantilla",
            "detail": "El archivo Word no contiene {{placeholders}}",
            "error_code": "NO_PLACEHOLDERS",
            "status_code": 400,
            "timestamp": "2025-01-13T10:30:00"
        }
    """
    success: bool = Field(False, description="Siempre false para errores")
    error: str = Field(..., description="Mensaje de error principal")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error")
    error_code: str = Field(..., description="Código único del error")
    status_code: int = Field(..., description="Código HTTP de status", ge=400, le=599)
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp ISO 8601 del error"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": "Error al generar documento",
                    "detail": "El template contiene placeholders inválidos",
                    "error_code": "DOCUMENT_GENERATION_FAILED",
                    "status_code": 500,
                    "timestamp": "2025-01-13T10:30:00"
                }
            ]
        }
    }


class ValidationError(BaseModel):
    """
    Error de validación individual de Pydantic

    Example:
        {
            "field": "template_name",
            "message": "Field required",
            "type": "missing"
        }
    """
    field: str = Field(..., description="Campo que falló la validación")
    message: str = Field(..., description="Mensaje de error")
    type: str = Field(..., description="Tipo de error de validación")


class ValidationErrorResponse(BaseModel):
    """
    Respuesta cuando hay errores de validación de Pydantic

    Example:
        {
            "success": false,
            "error": "Validation Error",
            "errors": [
                {
                    "field": "template_name",
                    "message": "Field required",
                    "type": "missing"
                }
            ],
            "status_code": 422,
            "timestamp": "2025-01-13T10:30:00"
        }
    """
    success: bool = Field(False, description="Siempre false para errores")
    error: str = Field("Validation Error", description="Tipo de error")
    errors: List[ValidationError] = Field(..., description="Lista de errores de validación")
    status_code: int = Field(422, description="HTTP 422 Unprocessable Entity")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp ISO 8601"
    )


class ProcessingStatus(BaseModel):
    """
    Estado de procesamiento asíncrono

    Útil para operaciones largas como OCR paralelo

    Example:
        {
            "status": "processing",
            "progress_percent": 65.0,
            "current_step": "Procesando archivo 13 de 20",
            "message": "Extrayendo texto de documentos...",
            "estimated_time_remaining_seconds": 3
        }
    """
    status: ProcessingStatusEnum = Field(..., description="Estado actual del procesamiento")
    progress_percent: float = Field(
        ...,
        description="Porcentaje de progreso (0-100)",
        ge=0,
        le=100
    )
    current_step: str = Field(..., description="Descripción del paso actual")
    message: str = Field(..., description="Mensaje descriptivo del estado")
    estimated_time_remaining_seconds: Optional[int] = Field(
        None,
        description="Tiempo estimado restante en segundos",
        ge=0
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "processing",
                    "progress_percent": 75.0,
                    "current_step": "Procesando documentos con OCR",
                    "message": "Extrayendo texto de 15 archivos en paralelo...",
                    "estimated_time_remaining_seconds": 2
                }
            ]
        }
    }


class HealthCheckResponse(BaseModel):
    """
    Health check del sistema

    Verifica estado de servicios externos (OpenAI, Vision, Drive, SMTP)

    Example:
        {
            "status": "healthy",
            "version": "2.0.0",
            "services": {
                "openai": "ok",
                "openrouter": "ok",
                "google_vision": "ok",
                "google_drive": "ok",
                "smtp": "ok"
            },
            "timestamp": "2025-01-13T10:30:00"
        }
    """
    status: str = Field(
        ...,
        description="Estado general del sistema",
        pattern="^(healthy|degraded|unhealthy)$"
    )
    version: str = Field(..., description="Versión de la API")
    services: Dict[str, str] = Field(
        ...,
        description="Estado de cada servicio externo (ok|degraded|error)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp ISO 8601"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "2.0.0",
                    "services": {
                        "openai": "ok",
                        "openrouter": "ok",
                        "google_vision": "ok",
                        "google_drive": "ok",
                        "smtp": "ok"
                    },
                    "timestamp": "2025-01-13T10:30:00"
                }
            ]
        }
    }


# Generic type for paginated responses
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica

    Para futuras implementaciones de listados paginados

    Example:
        {
            "items": [{...}, {...}],
            "total": 50,
            "page": 1,
            "page_size": 10,
            "total_pages": 5,
            "has_next": true,
            "has_previous": false
        }
    """
    items: List[T] = Field(..., description="Items de la página actual")
    total: int = Field(..., description="Total de items en todas las páginas", ge=0)
    page: int = Field(..., description="Número de página actual", ge=1)
    page_size: int = Field(..., description="Items por página", ge=1, le=100)
    total_pages: int = Field(..., description="Total de páginas", ge=0)
    has_next: bool = Field(..., description="Si existe página siguiente")
    has_previous: bool = Field(..., description="Si existe página anterior")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """
        Helper para crear respuesta paginada

        Args:
            items: Items de la página actual
            total: Total de items
            page: Página actual
            page_size: Items por página

        Returns:
            PaginatedResponse con metadata calculada
        """
        total_pages = (total + page_size - 1) // page_size

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
