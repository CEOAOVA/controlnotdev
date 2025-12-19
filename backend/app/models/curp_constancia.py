"""
ControlNot v2 - Modelo Constancia CURP
Campos específicos para constancia CURP impresa de RENAPO

Documento oficial con código QR y datos del registro civil
"""
from pydantic import BaseModel, Field
from typing import Optional


class ConstanciaCURP(BaseModel):
    """
    Campos extraídos de constancia CURP de RENAPO

    Los campos tienen descripciones detalladas que sirven como instrucciones
    para Claude Vision sobre dónde encontrar cada dato en la constancia.
    """

    curp: Optional[str] = Field(
        None,
        description="""CURP de 18 caracteres.
FORMATO: 4 letras + 6 digitos + 1 sexo + 5 letras + 2 digitos
UBICACION: Centro del documento, en grande
EJEMPLO: CEAR640813HMNRRL02"""
    )

    nombre_completo: Optional[str] = Field(
        None,
        description="""NOMBRE COMPLETO del titular.
FORMATO: NOMBRE(S) APELLIDO_PATERNO APELLIDO_MATERNO
UBICACION: Debajo del CURP
EJEMPLO: RAUL CERVANTES AREVALO"""
    )

    primer_apellido: Optional[str] = Field(
        None,
        description="""PRIMER APELLIDO (paterno).
EJEMPLO: CERVANTES"""
    )

    segundo_apellido: Optional[str] = Field(
        None,
        description="""SEGUNDO APELLIDO (materno).
EJEMPLO: AREVALO"""
    )

    nombres: Optional[str] = Field(
        None,
        description="""NOMBRE(S) de pila.
EJEMPLO: RAUL"""
    )

    fecha_nacimiento: Optional[str] = Field(
        None,
        description="""FECHA DE NACIMIENTO.
FORMATO: DD/MM/AAAA
EJEMPLO: 13/08/1964"""
    )

    sexo: Optional[str] = Field(
        None,
        description="""SEXO del titular.
FORMATO: HOMBRE o MUJER (o H/M)
EJEMPLO: HOMBRE"""
    )

    entidad_nacimiento: Optional[str] = Field(
        None,
        description="""ENTIDAD DE NACIMIENTO.
FORMATO: Nombre del estado
EJEMPLO: MICHOACAN"""
    )

    nacionalidad: Optional[str] = Field(
        None,
        description="""NACIONALIDAD.
FORMATO: MEXICANA o MEXICANO POR NACIMIENTO
EJEMPLO: MEXICANA"""
    )

    fecha_registro: Optional[str] = Field(
        None,
        description="""FECHA DE REGISTRO en RENAPO.
FORMATO: DD/MM/AAAA
EJEMPLO: 01/01/2000"""
    )

    clave_entidad_registro: Optional[str] = Field(
        None,
        description="""CLAVE DE ENTIDAD DE REGISTRO.
FORMATO: 2 digitos
EJEMPLO: 14 (Jalisco)"""
    )

    folio: Optional[str] = Field(
        None,
        description="""NUMERO DE FOLIO de la constancia.
UBICACION: Parte inferior del documento
EJEMPLO: 1234567890"""
    )

    codigo_verificacion: Optional[str] = Field(
        None,
        description="""CODIGO DE VERIFICACION o hash.
UBICACION: Junto al QR o en el QR
EJEMPLO: ABC123XYZ"""
    )

    class Config:
        json_schema_extra = {
            "example": {
                "curp": "CEAR640813HMNRRL02",
                "nombre_completo": "RAUL CERVANTES AREVALO",
                "primer_apellido": "CERVANTES",
                "segundo_apellido": "AREVALO",
                "nombres": "RAUL",
                "fecha_nacimiento": "13/08/1964",
                "sexo": "HOMBRE",
                "entidad_nacimiento": "MICHOACAN",
                "nacionalidad": "MEXICANA",
                "fecha_registro": "01/01/2000",
                "clave_entidad_registro": "14",
                "folio": "1234567890",
                "codigo_verificacion": "ABC123XYZ"
            }
        }
