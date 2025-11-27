"""
ControlNot v2 - Session Schemas
Schemas de request/response para endpoints de sesiones
"""
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class SessionCreateRequest(BaseModel):
    """Request para crear una nueva sesión de procesamiento"""

    case_id: UUID = Field(..., description="UUID del caso al que pertenece")
    tipo_documento: str = Field(..., description="Tipo de documento a procesar")
    total_archivos: int = Field(0, ge=0, description="Total de archivos a procesar")
    session_data: Optional[Dict] = Field(default_factory=dict, description="Datos adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "770e8400-e29b-41d4-a716-446655440000",
                "tipo_documento": "cancelacion",
                "total_archivos": 5
            }
        }


class SessionProgressUpdate(BaseModel):
    """Request para actualizar progreso de una sesión"""

    archivos_procesados: int = Field(..., ge=0, description="Archivos procesados")
    total_archivos: Optional[int] = Field(None, ge=0, description="Total (si cambió)")

    class Config:
        json_schema_extra = {
            "example": {
                "archivos_procesados": 3,
                "total_archivos": 5
            }
        }


class SessionCompleteRequest(BaseModel):
    """Request para marcar sesión como completada"""

    error_message: Optional[str] = Field(None, description="Mensaje de error (si falló)")

    class Config:
        json_schema_extra = {
            "example": {
                "error_message": None
            }
        }


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class SessionResponse(BaseModel):
    """Response con datos de una sesión"""

    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    case_id: Optional[UUID]
    tipo_documento: str
    estado: str
    total_archivos: int
    archivos_procesados: int
    progreso_porcentaje: float
    session_data: Dict
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SessionWithCaseResponse(SessionResponse):
    """Response con sesión y datos del caso"""

    case: Dict = Field(..., description="Datos del caso")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "case_id": "770e8400-e29b-41d4-a716-446655440000",
                "tipo_documento": "cancelacion",
                "estado": "procesando",
                "total_archivos": 5,
                "archivos_procesados": 3,
                "progreso_porcentaje": 60.0,
                "case": {
                    "case_number": "EXP-CANC-2024-042",
                    "client": {
                        "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ"
                    }
                }
            }
        }


class SessionListResponse(BaseModel):
    """Response para lista de sesiones"""

    sessions: List[SessionResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [],
                "total": 25
            }
        }
