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
        description="Fecha del día en que se firma el instrumento (formato completo en palabras)",
        json_schema_extra={
            "aliases": ["Fecha_Escritura", "Fecha_Documento", "Fecha_Firma", "Fecha_Acto", "Fecha"]
        }
    )

    lugar_instrumento: Optional[str] = Field(
        None,
        description="Ciudad y estado donde se firma el instrumento",
        json_schema_extra={
            "aliases": [
                "Lugar_Escritura", "Ciudad_Instrumento", "Lugar_Firma", "Ciudad", "Plaza",
                "ciudad_residencia", "Ciudad_Residencia", "Residencia"
            ]
        }
    )

    numero_instrumento: Optional[str] = Field(
        None,
        description="Número del instrumento notarial en palabras",
        json_schema_extra={
            "aliases": ["Numero_Escritura", "Escritura_Numero", "No_Instrumento", "Numero", "Instrumento"]
        }
    )

    notario_actuante: Optional[str] = Field(
        None,
        description="Nombre completo del notario que autoriza el acto",
        json_schema_extra={
            "aliases": [
                "Notario", "Nombre_Notario", "Notario_Publico", "Fedatario", "Notario_Nombre",
                "notario"
            ]
        }
    )

    numero_notaria: Optional[str] = Field(
        None,
        description="Número de la notaría en palabras",
        json_schema_extra={
            "aliases": ["Notaria_Numero", "No_Notaria", "Numero_Notario", "Notaria"]
        }
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
