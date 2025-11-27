"""
ControlNot v2 - Session DB Model
Modelo Pydantic para la tabla 'sessions'
"""
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class SessionDB(BaseModel):
    """
    Modelo que representa una sesión de procesamiento en la base de datos

    Mapea directamente a la tabla 'sessions'
    """

    id: UUID = Field(..., description="UUID de la sesión")
    tenant_id: UUID = Field(..., description="UUID de la notaría")
    user_id: Optional[UUID] = Field(None, description="UUID del usuario que creó la sesión")
    case_id: Optional[UUID] = Field(None, description="UUID del caso al que pertenece")

    # Información de la sesión
    tipo_documento: str = Field(..., description="Tipo de documento a procesar")
    estado: str = Field(
        default="iniciado",
        description="Estado: iniciado, procesando, completado, error, cancelado"
    )

    # Progreso
    total_archivos: int = Field(default=0, description="Total de archivos a procesar")
    archivos_procesados: int = Field(default=0, description="Archivos ya procesados")
    progreso_porcentaje: float = Field(default=0.0, description="Progreso porcentual (0-100)")

    # Datos de la sesión
    session_data: Dict = Field(default_factory=dict, description="Datos adicionales (JSONB)")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")

    # Timestamps
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "660e8400-e29b-41d4-a716-446655440000",
                "case_id": "770e8400-e29b-41d4-a716-446655440000",
                "tipo_documento": "cancelacion",
                "estado": "procesando",
                "total_archivos": 5,
                "archivos_procesados": 3,
                "progreso_porcentaje": 60.0
            }
        }
