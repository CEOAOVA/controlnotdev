"""
ControlNot v2 - Modelos Base
Campos comunes para todos los tipos de documentos notariales

Migrado de por_partes.py líneas 368-374
"""
from pydantic import BaseModel, Field
from typing import Optional


class BaseKeys(BaseModel):
    """
    Campos comunes a todos los tipos de documentos notariales

    Estos campos aparecen en TODOS los documentos independientemente del tipo:
    - Compraventa
    - Donación
    - Testamento
    - Poder
    - Sociedad
    """

    fecha_instrumento: Optional[str] = Field(
        None,
        description="Fecha del día en que se firma el instrumento (formato completo en palabras)"
    )

    lugar_instrumento: Optional[str] = Field(
        None,
        description="Ciudad y estado donde se firma el instrumento"
    )

    numero_instrumento: Optional[str] = Field(
        None,
        description="Número del instrumento notarial en palabras"
    )

    notario_actuante: Optional[str] = Field(
        None,
        description="Nombre completo del notario que autoriza el acto"
    )

    numero_notaria: Optional[str] = Field(
        None,
        description="Número de la notaría en palabras"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "fecha_instrumento": "tres de enero del año dos mil veinticinco",
                "lugar_instrumento": "Guadalajara, Jalisco",
                "numero_instrumento": "mil doscientos treinta y cuatro",
                "notario_actuante": "Licenciado Juan Pérez García",
                "numero_notaria": "quince"
            }
        }
