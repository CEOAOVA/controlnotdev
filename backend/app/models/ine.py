"""
ControlNot v2 - Modelo INE/IFE
Campos específicos para credencial de elector mexicana

Soporta:
- INE (Instituto Nacional Electoral) - actual
- IFE (Instituto Federal Electoral) - anterior
- Cualquier orientación (Claude Vision lo maneja)
"""
from pydantic import BaseModel, Field
from typing import Optional


class INECredencial(BaseModel):
    """
    Campos extraídos de credencial INE/IFE mexicana

    Los campos tienen descripciones detalladas que sirven como instrucciones
    para Claude Vision sobre dónde encontrar cada dato en la credencial.
    """

    nombre_completo: Optional[str] = Field(
        None,
        description="""NOMBRE COMPLETO del titular como aparece en la INE.
FORMATO: APELLIDO PATERNO APELLIDO MATERNO NOMBRE(S) en MAYUSCULAS
UBICACION: Frente de la credencial, debajo de la foto
EJEMPLO: CERVANTES AREVALO RAUL"""
    )

    clave_elector: Optional[str] = Field(
        None,
        description="""CLAVE DE ELECTOR de 18 caracteres alfanumericos.
FORMATO: 6 letras + 8 digitos + 4 caracteres
UBICACION: Frente de la credencial
EJEMPLO: CRVRAL64081314H100"""
    )

    curp: Optional[str] = Field(
        None,
        description="""CURP de 18 caracteres.
FORMATO: 4 letras + 6 digitos + 1 letra sexo + 5 letras + 2 digitos
UBICACION: Frente de la credencial, bajo el nombre
EJEMPLO: CEAR640813HMNRRL02
VALIDACION: H=Hombre, M=Mujer en posicion 11"""
    )

    fecha_nacimiento: Optional[str] = Field(
        None,
        description="""FECHA DE NACIMIENTO del titular.
FORMATO: DD/MM/AAAA
UBICACION: Frente de la credencial
EJEMPLO: 13/08/1964"""
    )

    sexo: Optional[str] = Field(
        None,
        description="""SEXO del titular.
FORMATO: H para Hombre, M para Mujer
UBICACION: Frente de la credencial o inferido del CURP (posicion 11)"""
    )

    domicilio: Optional[str] = Field(
        None,
        description="""DOMICILIO COMPLETO del titular.
FORMATO: Calle, numero, colonia, municipio, estado, CP
UBICACION: REVERSO de la credencial
EJEMPLO: AV HIDALGO 123 COL CENTRO GUADALAJARA JALISCO 44100"""
    )

    seccion_electoral: Optional[str] = Field(
        None,
        description="""SECCION ELECTORAL de 4 digitos.
FORMATO: 4 digitos numericos
UBICACION: Frente de la credencial
EJEMPLO: 1234"""
    )

    estado: Optional[str] = Field(
        None,
        description="""ESTADO de emision de la credencial.
FORMATO: Nombre del estado en MAYUSCULAS
UBICACION: Frente o reverso de la credencial
EJEMPLO: JALISCO"""
    )

    municipio: Optional[str] = Field(
        None,
        description="""MUNICIPIO o DELEGACION del domicilio.
FORMATO: Nombre en MAYUSCULAS
UBICACION: Reverso de la credencial
EJEMPLO: GUADALAJARA"""
    )

    vigencia: Optional[str] = Field(
        None,
        description="""AÑO DE VIGENCIA de la credencial.
FORMATO: 4 digitos (año)
UBICACION: Frente de la credencial
EJEMPLO: 2029"""
    )

    numero_vertical: Optional[str] = Field(
        None,
        description="""NUMERO VERTICAL o CIC de la credencial.
FORMATO: 9 digitos
UBICACION: Frente, costado derecho vertical
EJEMPLO: 123456789"""
    )

    numero_ocr: Optional[str] = Field(
        None,
        description="""NUMERO OCR de la credencial (codigo de barras/MRZ).
FORMATO: Alfanumerico variable
UBICACION: REVERSO de la credencial
EJEMPLO: IDMEX2650430777<<<<<<<<<<<"""
    )

    emision: Optional[str] = Field(
        None,
        description="""AÑO DE EMISION de la credencial.
FORMATO: 4 digitos (año)
UBICACION: Frente o reverso
EJEMPLO: 2019"""
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nombre_completo": "CERVANTES AREVALO RAUL",
                "clave_elector": "CRVRAL64081314H100",
                "curp": "CEAR640813HMNRRL02",
                "fecha_nacimiento": "13/08/1964",
                "sexo": "H",
                "domicilio": "AV HIDALGO 123 COL CENTRO GUADALAJARA JALISCO 44100",
                "seccion_electoral": "1234",
                "estado": "JALISCO",
                "municipio": "GUADALAJARA",
                "vigencia": "2029",
                "numero_vertical": "123456789",
                "numero_ocr": "IDMEX2650430777",
                "emision": "2019"
            }
        }
