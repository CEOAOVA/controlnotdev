"""
ControlNot v2 - Document DB Model
Modelo Pydantic para la tabla 'documentos'
"""
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentDB(BaseModel):
    """
    Modelo que representa un documento generado en la base de datos

    Mapea directamente a la tabla 'documentos'
    """

    id: UUID = Field(..., description="UUID del documento")
    tenant_id: UUID = Field(..., description="UUID de la notaría")
    user_id: Optional[UUID] = Field(None, description="UUID del usuario que generó el documento")

    # Relaciones
    case_id: Optional[UUID] = Field(None, description="UUID del caso al que pertenece")
    session_id: Optional[UUID] = Field(None, description="UUID de la sesión que lo generó")
    template_id: Optional[UUID] = Field(None, description="UUID del template usado")

    # Información del documento
    tipo_documento: str = Field(..., description="Tipo de documento")
    nombre_documento: Optional[str] = Field(None, description="Nombre del documento")
    estado: str = Field(
        default="borrador",
        description="Estado: borrador, procesando, revisado, completado, error"
    )

    # Storage
    storage_path: Optional[str] = Field(None, description="Ruta en Supabase Storage")
    google_drive_id: Optional[str] = Field(None, description="ID en Google Drive")

    # Datos extraídos y editados
    extracted_data: Dict = Field(default_factory=dict, description="Datos extraídos con IA (JSONB)")
    edited_data: Optional[Dict] = Field(None, description="Datos editados por usuario (JSONB)")

    # Métricas
    confidence_score: Optional[float] = Field(
        None,
        description="Score de confianza de la extracción (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    # Flags
    es_ejemplo_bueno: bool = Field(default=False, description="Marcar como buen ejemplo para entrenamiento")
    requiere_revision: bool = Field(default=False, description="Requiere revisión manual")

    # Metadata
    metadata: Dict = Field(default_factory=dict, description="Metadata adicional (JSONB)")

    # Timestamps
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "660e8400-e29b-41d4-a716-446655440000",
                "case_id": "770e8400-e29b-41d4-a716-446655440000",
                "session_id": "880e8400-e29b-41d4-a716-446655440000",
                "tipo_documento": "cancelacion",
                "nombre_documento": "Escritura Cancelacion BBVA 2024-042.docx",
                "estado": "completado",
                "storage_path": "660e8400/generated/990e8400.docx",
                "confidence_score": 0.95
            }
        }
