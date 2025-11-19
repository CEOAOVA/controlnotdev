"""
ControlNot v2 - Modelo Sociedad
15 campos específicos para documentos de constitución de sociedad

Migrado de por_partes.py líneas 1339-1360
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class SociedadKeys(BaseKeys):
    """
    Campos específicos para documentos de CONSTITUCIÓN DE SOCIEDAD

    Hereda 5 campos comunes de BaseKeys
    Agrega 15 campos específicos de sociedad
    """

    Denominacion_Social: Optional[str] = Field(
        None,
        description="Denominación o razón social completa"
    )

    Tipo_Sociedad: Optional[str] = Field(
        None,
        description="Tipo de sociedad (S.A., S.R.L., S.C., etc.)"
    )

    Objeto_Social: Optional[str] = Field(
        None,
        description="Descripción del objeto social"
    )

    Capital_Social: Optional[str] = Field(
        None,
        description="Monto del capital social"
    )

    Duracion_Sociedad: Optional[str] = Field(
        None,
        description="Duración de la sociedad"
    )

    # Socios
    Socios_Lista: Optional[str] = Field(
        None,
        description="Lista completa de socios con sus datos"
    )

    Aportaciones_Socios: Optional[str] = Field(
        None,
        description="Aportaciones de cada socio al capital"
    )

    Participacion_Socios: Optional[str] = Field(
        None,
        description="Porcentaje de participación de cada socio"
    )

    # Administración
    Administradores: Optional[str] = Field(
        None,
        description="Nombre y datos de los administradores"
    )

    Facultades_Administracion: Optional[str] = Field(
        None,
        description="Facultades de administración y representación"
    )

    Organos_Gobierno: Optional[str] = Field(
        None,
        description="Estructura de órganos de gobierno"
    )

    # Domicilio y otros
    Domicilio_Social: Optional[str] = Field(
        None,
        description="Domicilio social de la sociedad"
    )

    Representante_Legal: Optional[str] = Field(
        None,
        description="Representante legal designado"
    )

    Ejercicio_Social: Optional[str] = Field(
        None,
        description="Período del ejercicio social"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Denominacion_Social": "Tecnología e Innovación, S.A. de C.V.",
                "Tipo_Sociedad": "S.A. de C.V.",
                "Capital_Social": "$50,000.00 (cincuenta mil pesos 00/100 M.N.)",
                "Socios_Lista": "Socio 1: Juan Pérez García, Socio 2: María López Hernández",
                "Domicilio_Social": "Avenida Principal número 123, Colonia Centro, Guadalajara, Jalisco"
            }
        }
