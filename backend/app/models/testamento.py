"""
ControlNot v2 - Modelo Testamento
15 campos específicos para documentos de testamento

Migrado de por_partes.py líneas 1287-1309
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class TestamentoKeys(BaseKeys):
    """
    Campos específicos para documentos de TESTAMENTO

    Hereda 5 campos comunes de BaseKeys
    Agrega 15 campos específicos de testamento
    """

    Testador_Nombre_Completo: Optional[str] = Field(
        None,
        description="Nombre completo del testador en MAYÚSCULAS"
    )

    Tipo_Testamento: Optional[str] = Field(
        None,
        description="Tipo de testamento (público abierto, cerrado, etc.)"
    )

    Declaracion_Capacidad: Optional[str] = Field(
        None,
        description="Declaración sobre la capacidad mental del testador"
    )

    # Datos del testador
    Edad_Testador: Optional[str] = Field(
        None,
        description="Edad del testador en letras + años"
    )

    Estado_civil_Testador: Optional[str] = Field(
        None,
        description="Estado civil del testador"
    )

    RFC_Testador: Optional[str] = Field(
        None,
        description="RFC completo del testador"
    )

    CURP_Testador: Optional[str] = Field(
        None,
        description="CURP completa del testador"
    )

    INE_Testador_numero: Optional[str] = Field(
        None,
        description="Número de credencial INE del testador"
    )

    Comprobante_Domicilio_Testador: Optional[str] = Field(
        None,
        description="Domicilio completo del testador"
    )

    # Herederos y legatarios
    Herederos_Universales: Optional[str] = Field(
        None,
        description="Lista de herederos universales con sus datos"
    )

    Legatarios: Optional[str] = Field(
        None,
        description="Lista de legatarios específicos con sus legados"
    )

    Albacea: Optional[str] = Field(
        None,
        description="Nombre y datos del albacea designado"
    )

    # Disposiciones testamentarias
    Disposiciones_Generales: Optional[str] = Field(
        None,
        description="Disposiciones generales del testador"
    )

    Revocacion_Testamentos: Optional[str] = Field(
        None,
        description="Cláusula de revocación de testamentos anteriores"
    )

    Reconocimiento_Deudas: Optional[str] = Field(
        None,
        description="Reconocimiento de deudas y obligaciones"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Testador_Nombre_Completo": "JUAN PÉREZ GARCÍA",
                "Tipo_Testamento": "público abierto",
                "Edad_Testador": "setenta y cinco años",
                "RFC_Testador": "PEGJ490310JJ8",
                "Herederos_Universales": "Sus hijos: María Pérez López y José Pérez López"
            }
        }
