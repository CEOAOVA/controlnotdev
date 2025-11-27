"""
ControlNot v2 - Client Schemas
Schemas de request/response para endpoints de clientes
"""
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class ClientCreateRequest(BaseModel):
    """Request para crear un nuevo cliente"""

    tipo_persona: str = Field(..., description="Tipo: 'fisica' o 'moral'")
    nombre_completo: str = Field(..., min_length=1, description="Nombre completo")
    rfc: Optional[str] = Field(None, min_length=12, max_length=13, description="RFC")
    curp: Optional[str] = Field(None, min_length=18, max_length=18, description="CURP (solo personas físicas)")
    email: Optional[EmailStr] = Field(None, description="Email del cliente")
    telefono: Optional[str] = Field(None, description="Teléfono")
    direccion: Optional[str] = Field(None, description="Dirección completa")
    ciudad: Optional[str] = Field(None, description="Ciudad")
    estado: Optional[str] = Field(None, description="Estado")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Metadata adicional")

    class Config:
        json_schema_extra = {
            "example": {
                "tipo_persona": "fisica",
                "nombre_completo": "Juan Carlos Martinez Lopez",
                "rfc": "MALJ850315ABC",
                "curp": "MALJ850315HDFPRN08",
                "email": "juan.martinez@example.com",
                "telefono": "5551234567",
                "direccion": "Av. Insurgentes Sur 1234, Col. Del Valle",
                "ciudad": "Ciudad de México",
                "estado": "CDMX",
                "codigo_postal": "03100"
            }
        }


class ClientUpdateRequest(BaseModel):
    """Request para actualizar un cliente existente"""

    nombre_completo: Optional[str] = Field(None, min_length=1)
    rfc: Optional[str] = Field(None, min_length=12, max_length=13)
    curp: Optional[str] = Field(None, min_length=18, max_length=18)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    metadata: Optional[Dict] = None
    activo: Optional[bool] = None


class ClientSearchRequest(BaseModel):
    """Request para búsqueda de clientes"""

    query: str = Field(..., min_length=2, description="Texto a buscar")
    tipo_persona: Optional[str] = Field(None, description="Filtrar por tipo")
    limit: int = Field(20, ge=1, le=100, description="Número máximo de resultados")


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class ClientResponse(BaseModel):
    """Response con datos de un cliente"""

    id: UUID
    tenant_id: UUID
    tipo_persona: str
    nombre_completo: str
    rfc: Optional[str]
    curp: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]
    estado: Optional[str]
    codigo_postal: Optional[str]
    metadata: Dict
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Response para lista de clientes"""

    clients: List[ClientResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "clients": [],
                "total": 150,
                "page": 1,
                "page_size": 50
            }
        }


class ClientWithCasesResponse(ClientResponse):
    """Response con cliente y sus casos"""

    cases_count: int = Field(..., description="Número de casos del cliente")
    recent_cases: List[Dict] = Field(default_factory=list, description="Casos recientes")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
                "rfc": "MALJ850315ABC",
                "cases_count": 5,
                "recent_cases": [
                    {
                        "case_number": "EXP-CANC-2024-042",
                        "document_type": "cancelacion",
                        "status": "completed"
                    }
                ]
            }
        }
