"""
ControlNot v2 - Case Schemas
Schemas de request/response para endpoints de casos/expedientes
"""
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class CaseCreateRequest(BaseModel):
    """Request para crear un nuevo caso/expediente"""

    client_id: UUID = Field(..., description="UUID del cliente principal")
    case_number: str = Field(..., min_length=1, description="Número de expediente")
    document_type: str = Field(
        ...,
        description="Tipo: compraventa, donacion, testamento, poder, sociedad, cancelacion"
    )
    description: Optional[str] = Field(None, description="Descripción del caso")
    parties: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Partes involucradas: [{\"role\": \"vendedor\", \"client_id\": \"uuid\"}]"
    )
    metadata: Optional[Dict] = Field(default_factory=dict, description="Metadata adicional")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "document_type": "cancelacion",
                "description": "Cancelación de hipoteca BBVA Bancomer - Inmueble en Polanco",
                "parties": [
                    {
                        "role": "deudor",
                        "client_id": "550e8400-e29b-41d4-a716-446655440000",
                        "nombre": "JUAN CARLOS MARTINEZ LOPEZ"
                    },
                    {
                        "role": "acreedor",
                        "nombre": "BBVA BANCOMER S.A."
                    }
                ]
            }
        }


class CaseUpdateRequest(BaseModel):
    """Request para actualizar un caso"""

    description: Optional[str] = None
    parties: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None


class CaseUpdateStatusRequest(BaseModel):
    """Request para actualizar el estado de un caso"""

    status: str = Field(
        ...,
        description="Nuevo estado: draft, documents_uploaded, ocr_processing, data_extracted, validated, document_generated, signed, completed, cancelled"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "documents_uploaded"
            }
        }


class CaseAddPartyRequest(BaseModel):
    """Request para agregar una parte al caso"""

    role: str = Field(..., description="Rol de la parte (vendedor, comprador, testador, etc.)")
    client_id: Optional[UUID] = Field(None, description="UUID del cliente (si existe)")
    nombre: Optional[str] = Field(None, description="Nombre (si no es un cliente registrado)")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Datos adicionales de la parte")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "comprador",
                "client_id": "660e8400-e29b-41d4-a716-446655440000",
                "nombre": "MARIA FERNANDA LOPEZ GARCIA"
            }
        }


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class CaseResponse(BaseModel):
    """Response con datos de un caso"""

    id: UUID
    tenant_id: UUID
    client_id: UUID
    case_number: str
    document_type: str
    status: str
    parties: List[Dict]
    description: Optional[str]
    metadata: Dict
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class CaseWithClientResponse(CaseResponse):
    """Response con caso y datos del cliente"""

    client: Dict = Field(..., description="Datos del cliente principal")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "document_type": "cancelacion",
                "status": "data_extracted",
                "client": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
                    "rfc": "MALJ850315ABC"
                },
                "parties": [
                    {"role": "deudor", "client_id": "550e8400-e29b-41d4-a716-446655440000"},
                    {"role": "acreedor", "nombre": "BBVA BANCOMER S.A."}
                ]
            }
        }


class CaseWithSessionsResponse(CaseWithClientResponse):
    """Response con caso, cliente y sesiones"""

    sessions: List[Dict] = Field(default_factory=list, description="Sesiones de procesamiento")
    documents_count: int = Field(0, description="Número de documentos generados")


class CaseListResponse(BaseModel):
    """Response para lista de casos"""

    cases: List[CaseResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "cases": [],
                "total": 85,
                "page": 1,
                "page_size": 50
            }
        }


class CaseStatisticsResponse(BaseModel):
    """Response con estadísticas de casos"""

    total_cases: int
    by_status: Dict[str, int] = Field(..., description="Casos por estado")
    by_document_type: Dict[str, int] = Field(..., description="Casos por tipo de documento")

    class Config:
        json_schema_extra = {
            "example": {
                "total_cases": 85,
                "by_status": {
                    "draft": 10,
                    "documents_uploaded": 15,
                    "data_extracted": 20,
                    "completed": 40
                },
                "by_document_type": {
                    "compraventa": 30,
                    "cancelacion": 25,
                    "testamento": 15,
                    "poder": 10,
                    "donacion": 3,
                    "sociedad": 2
                }
            }
        }


class CaseTimelineResponse(BaseModel):
    """Response con timeline de un caso (audit logs)"""

    case_id: UUID
    case_number: str
    timeline: List[Dict] = Field(..., description="Eventos del caso en orden cronológico")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "770e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "timeline": [
                    {
                        "timestamp": "2024-01-15T10:00:00Z",
                        "action": "create_case",
                        "user": "Juan Notario",
                        "details": "Caso creado"
                    },
                    {
                        "timestamp": "2024-01-15T10:30:00Z",
                        "action": "upload_documents",
                        "user": "Juan Notario",
                        "details": "5 documentos subidos"
                    }
                ]
            }
        }
