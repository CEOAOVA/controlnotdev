"""
ControlNot v2 - Case DB Model
Modelo Pydantic para la tabla 'cases'
"""
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CaseDB(BaseModel):
    """
    Modelo que representa un caso/expediente en la base de datos

    Mapea directamente a la tabla 'cases'
    """

    id: UUID = Field(..., description="UUID del caso")
    tenant_id: UUID = Field(..., description="UUID de la notaría")
    client_id: UUID = Field(..., description="UUID del cliente principal")

    # Identificación del caso
    case_number: str = Field(..., description="Número de expediente")
    document_type: str = Field(
        ...,
        description="Tipo de documento: compraventa, donacion, testamento, poder, sociedad, cancelacion"
    )

    # Estado del trámite
    status: str = Field(
        default="draft",
        description="Estado: draft, documents_uploaded, ocr_processing, data_extracted, validated, document_generated, signed, completed, cancelled"
    )

    # Partes involucradas
    parties: List[Dict] = Field(
        default_factory=list,
        description="Array JSON con partes involucradas: [{\"role\": \"vendedor\", \"client_id\": \"uuid\"}]"
    )

    # Descripción
    description: Optional[str] = Field(None, description="Descripción del caso")
    metadata: Dict = Field(default_factory=dict, description="Metadata adicional (JSONB)")

    # Timestamps
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "660e8400-e29b-41d4-a716-446655440000",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "document_type": "cancelacion",
                "status": "draft",
                "description": "Cancelación de hipoteca BBVA Bancomer",
                "parties": [
                    {"role": "deudor", "client_id": "550e8400-e29b-41d4-a716-446655440000"},
                    {"role": "acreedor", "nombre": "BBVA BANCOMER S.A."}
                ]
            }
        }
