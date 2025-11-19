"""
ControlNot v2 - Modelo Poder
15 campos específicos para documentos de poder notarial

Migrado de por_partes.py líneas 1312-1336
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class PoderKeys(BaseKeys):
    """
    Campos específicos para documentos de PODER NOTARIAL

    Hereda 5 campos comunes de BaseKeys
    Agrega 15 campos específicos de poder
    """

    Otorgante_Nombre_Completo: Optional[str] = Field(
        None,
        description="Nombre completo del otorgante en MAYÚSCULAS"
    )

    Apoderado_Nombre_Completo: Optional[str] = Field(
        None,
        description="Nombre completo del apoderado en MAYÚSCULAS"
    )

    Tipo_Poder: Optional[str] = Field(
        None,
        description="Tipo de poder (general, especial, para pleitos y cobranzas, etc.)"
    )

    Facultades_Otorgadas: Optional[str] = Field(
        None,
        description="Descripción detallada de las facultades otorgadas"
    )

    # Datos del otorgante
    Edad_Otorgante: Optional[str] = Field(
        None,
        description="Edad del otorgante en letras + años"
    )

    Estado_civil_Otorgante: Optional[str] = Field(
        None,
        description="Estado civil del otorgante"
    )

    RFC_Otorgante: Optional[str] = Field(
        None,
        description="RFC completo del otorgante"
    )

    CURP_Otorgante: Optional[str] = Field(
        None,
        description="CURP completa del otorgante"
    )

    INE_Otorgante_numero: Optional[str] = Field(
        None,
        description="Número de credencial INE del otorgante"
    )

    # Datos del apoderado
    Edad_Apoderado: Optional[str] = Field(
        None,
        description="Edad del apoderado en letras + años"
    )

    Estado_civil_Apoderado: Optional[str] = Field(
        None,
        description="Estado civil del apoderado"
    )

    RFC_Apoderado: Optional[str] = Field(
        None,
        description="RFC completo del apoderado"
    )

    CURP_Apoderado: Optional[str] = Field(
        None,
        description="CURP completa del apoderado"
    )

    INE_Apoderado_numero: Optional[str] = Field(
        None,
        description="Número de credencial INE del apoderado"
    )

    # Condiciones del poder
    Vigencia_Poder: Optional[str] = Field(
        None,
        description="Vigencia del poder (indefinido, hasta fecha específica, etc.)"
    )

    Limitaciones: Optional[str] = Field(
        None,
        description="Limitaciones específicas del poder"
    )

    Revocabilidad: Optional[str] = Field(
        None,
        description="Condiciones de revocabilidad del poder"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Otorgante_Nombre_Completo": "MARÍA LÓPEZ HERNÁNDEZ",
                "Apoderado_Nombre_Completo": "CARLOS GARCÍA RODRÍGUEZ",
                "Tipo_Poder": "general para pleitos y cobranzas",
                "RFC_Otorgante": "LOHM650420JJ8",
                "RFC_Apoderado": "GARC780815EG6"
            }
        }
