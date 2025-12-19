"""
ControlNot v2 - Modelo Pasaporte Mexicano
Campos específicos para pasaporte de México

Incluye datos de la página de datos y MRZ (Machine Readable Zone)
"""
from pydantic import BaseModel, Field
from typing import Optional


class PasaporteMexicano(BaseModel):
    """
    Campos extraídos de pasaporte mexicano

    Los campos tienen descripciones detalladas que sirven como instrucciones
    para Claude Vision sobre dónde encontrar cada dato en el pasaporte.
    """

    nombre_completo: Optional[str] = Field(
        None,
        description="""NOMBRE COMPLETO del titular.
FORMATO: APELLIDOS / NOMBRES en MAYUSCULAS
UBICACION: Pagina de datos, campo "Apellidos/Surname" y "Nombres/Given names"
EJEMPLO: CERVANTES AREVALO / RAUL"""
    )

    apellidos: Optional[str] = Field(
        None,
        description="""APELLIDOS del titular separados.
FORMATO: MAYUSCULAS
EJEMPLO: CERVANTES AREVALO"""
    )

    nombres: Optional[str] = Field(
        None,
        description="""NOMBRES del titular.
FORMATO: MAYUSCULAS
EJEMPLO: RAUL"""
    )

    nacionalidad: Optional[str] = Field(
        None,
        description="""NACIONALIDAD del titular.
FORMATO: MEXICANA o MEX
EJEMPLO: MEXICANA"""
    )

    fecha_nacimiento: Optional[str] = Field(
        None,
        description="""FECHA DE NACIMIENTO.
FORMATO: DD/MM/AAAA o DD MMM AAAA
EJEMPLO: 13/08/1964"""
    )

    sexo: Optional[str] = Field(
        None,
        description="""SEXO del titular.
FORMATO: H/M o M/F
EJEMPLO: H"""
    )

    lugar_nacimiento: Optional[str] = Field(
        None,
        description="""LUGAR DE NACIMIENTO.
FORMATO: ESTADO, MEXICO o ciudad
EJEMPLO: JALISCO, MEXICO"""
    )

    curp: Optional[str] = Field(
        None,
        description="""CURP del titular (18 caracteres).
FORMATO: Alfanumerico 18 caracteres
UBICACION: Pagina de datos
EJEMPLO: CEAR640813HMNRRL02"""
    )

    numero_pasaporte: Optional[str] = Field(
        None,
        description="""NUMERO DE PASAPORTE.
FORMATO: Alfanumerico (usualmente G + 8 digitos)
EJEMPLO: G12345678"""
    )

    fecha_expedicion: Optional[str] = Field(
        None,
        description="""FECHA DE EXPEDICION.
FORMATO: DD/MM/AAAA
EJEMPLO: 15/03/2020"""
    )

    fecha_vencimiento: Optional[str] = Field(
        None,
        description="""FECHA DE VENCIMIENTO.
FORMATO: DD/MM/AAAA
EJEMPLO: 14/03/2030"""
    )

    autoridad_expedidora: Optional[str] = Field(
        None,
        description="""AUTORIDAD QUE EXPIDIO.
FORMATO: Texto
EJEMPLO: SRE GUADALAJARA"""
    )

    mrz_linea1: Optional[str] = Field(
        None,
        description="""PRIMERA LINEA DEL MRZ (Machine Readable Zone).
FORMATO: 44 caracteres
UBICACION: Parte inferior de la pagina de datos
EJEMPLO: P<MEXCERVANTES<AREVALO<<RAUL<<<<<<<<<<<<<<<"""
    )

    mrz_linea2: Optional[str] = Field(
        None,
        description="""SEGUNDA LINEA DEL MRZ.
FORMATO: 44 caracteres
EJEMPLO: G123456780MEX6408131M3003146<<<<<<<<<<<<<<02"""
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nombre_completo": "CERVANTES AREVALO / RAUL",
                "apellidos": "CERVANTES AREVALO",
                "nombres": "RAUL",
                "nacionalidad": "MEXICANA",
                "fecha_nacimiento": "13/08/1964",
                "sexo": "H",
                "lugar_nacimiento": "JALISCO, MEXICO",
                "curp": "CEAR640813HMNRRL02",
                "numero_pasaporte": "G12345678",
                "fecha_expedicion": "15/03/2020",
                "fecha_vencimiento": "14/03/2030",
                "autoridad_expedidora": "SRE GUADALAJARA",
                "mrz_linea1": "P<MEXCERVANTES<AREVALO<<RAUL<<<<<<<<<<<<<<<",
                "mrz_linea2": "G123456780MEX6408131M3003146<<<<<<<<<<<<<<02"
            }
        }
