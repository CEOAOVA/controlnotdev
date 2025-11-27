"""
ControlNot v2 - Client DB Model
Modelo Pydantic para la tabla 'clients'
"""
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ClientDB(BaseModel):
    """
    Modelo que representa un cliente en la base de datos

    Mapea directamente a la tabla 'clients'
    """

    id: UUID = Field(..., description="UUID del cliente")
    tenant_id: UUID = Field(..., description="UUID de la notaría")

    # Identificación
    tipo_persona: str = Field(..., description="Tipo: 'fisica' o 'moral'")
    nombre_completo: str = Field(..., description="Nombre completo (MAYÚSCULAS)")
    rfc: Optional[str] = Field(None, description="RFC del cliente")
    curp: Optional[str] = Field(None, description="CURP (solo personas físicas)")

    # Contacto
    email: Optional[EmailStr] = Field(None, description="Email del cliente")
    telefono: Optional[str] = Field(None, description="Teléfono")
    direccion: Optional[str] = Field(None, description="Dirección completa")
    ciudad: Optional[str] = Field(None, description="Ciudad")
    estado: Optional[str] = Field(None, description="Estado")
    codigo_postal: Optional[str] = Field(None, description="Código postal")

    # Metadata
    metadata: Dict = Field(default_factory=dict, description="Metadata adicional (JSONB)")
    activo: bool = Field(True, description="Si el cliente está activo")

    # Timestamps
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "660e8400-e29b-41d4-a716-446655440000",
                "tipo_persona": "fisica",
                "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
                "rfc": "MALJ850315ABC",
                "curp": "MALJ850315HDFPRN08",
                "email": "juan.martinez@example.com",
                "telefono": "5551234567",
                "ciudad": "Ciudad de México",
                "estado": "CDMX",
                "activo": True
            }
        }
