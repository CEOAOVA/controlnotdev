"""
ControlNot v2 - Modelo Cancelación de Hipotecas
Descriptions SIMPLIFICADAS para mejor extracción con IA (patrón movil_cancelaciones.py)

Migrado de movil_cancelaciones.py - CLAVES_ESTANDARIZADAS
Optimizado: 1 línea por descripción + ejemplo explícito

AJUSTADO: 30 campos específicos según PDF "documentos notaria.pdf"
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.base import BaseKeys


class CancelacionKeys(BaseKeys):
    """
    Campos específicos para documentos de CANCELACIÓN DE HIPOTECAS

    Hereda 5 campos comunes de BaseKeys:
    - fecha_instrumento, lugar_instrumento, numero_instrumento
    - notario_actuante, numero_notaria

    DESCRIPTIONS SIMPLIFICADAS: 1 línea + ejemplo (estilo movil_cancelaciones.py)

    TOTAL: 35 campos (30 específicos + 5 heredados de BaseKeys)
    """

    # ==========================================
    # DATOS DEL DEUDOR/PROPIETARIO
    # ==========================================

    Deudor_Nombre_Completo: Optional[str] = Field(
        None,
        description="Nombre completo del deudor en MAYÚSCULAS. Ejemplo: 'JUAN CARLOS MARTINEZ LOPEZ'",
        json_schema_extra={
            "aliases": [
                "Nombre_Deudor", "Cliente_Nombre", "Acreditado", "Titular", "Propietario",
                "Nombre_Cliente", "Nombre_Titular", "Deudor", "deudor"
            ]
        }
    )

    # ==========================================
    # DATOS DE LA INSTITUCIÓN FINANCIERA / CRÉDITO
    # ==========================================

    Intermediario_Financiero: Optional[str] = Field(
        None,
        description="Intermediario financiero del crédito. Ejemplo: 'HIPOTECARIA VANGUARDIA'",
        json_schema_extra={
            "aliases": ["Intermediario", "Sofol", "Sofom", "Entidad_Financiera"]
        }
    )

    Suma_Credito: Optional[str] = Field(
        None,
        description="Monto del crédito hipotecario. Ejemplo: '$250,000.00'",
        json_schema_extra={
            "aliases": ["Monto_Credito", "Monto_Hipoteca", "Capital", "Importe_Credito", "Monto", "Importe", "Cantidad_Credito"]
        }
    )

    Suma_Credito_Letras: Optional[str] = Field(
        None,
        description="Monto en letras MAYÚSCULAS. Ejemplo: 'DOSCIENTOS CINCUENTA MIL PESOS 00/100 M.N.'",
        json_schema_extra={
            "aliases": ["Monto_Letras", "Capital_Letras", "Monto_Credito_Letras", "Importe_Letras", "Cantidad_Letras"]
        }
    )

    Equivalente_Salario_Minimo: Optional[str] = Field(
        None,
        description="Equivalente en salarios mínimos (número). Ejemplo: '500'",
        json_schema_extra={
            "aliases": ["Salarios_Minimos", "VSM", "Veces_Salario", "VSMM"]
        }
    )

    Equivalente_Salario_Minimo_Letras: Optional[str] = Field(
        None,
        description="Equivalente en salarios en letras MAYÚSCULAS. Ejemplo: 'QUINIENTOS VECES EL SALARIO MÍNIMO'",
        json_schema_extra={
            "aliases": ["Salarios_Minimos_Letras", "VSM_Letras", "Veces_Salario_Letras"]
        }
    )

    # ==========================================
    # DATOS DEL INMUEBLE HIPOTECADO
    # ==========================================

    Ubicacion_Inmueble: Optional[str] = Field(
        None,
        description="Ubicación completa del inmueble hipotecado. Ejemplo: 'CASA HABITACIÓN UBICADA EN LA CALLE PRIMER RETORNO DE LA ESTACAS, NUMERO 49...'",
        json_schema_extra={
            "aliases": ["Ubicacion_Completa", "Descripcion_Inmueble", "Inmueble_Completo"]
        }
    )

    # ==========================================
    # DATOS DE CESIÓN DE CRÉDITO (Si aplica)
    # ==========================================

    Cesion_Credito_Fecha: Optional[str] = Field(
        None,
        description="Fecha de cesión en palabras minúsculas. Ejemplo: 'quince de julio de dos mil veintitrés'. Si no aplica: 'NO APLICA'",
        json_schema_extra={
            "aliases": ["Fecha_Cesion", "Fecha_Cesion_Credito", "Cesion_Fecha"]
        }
    )

    Cesion_Credito_Valor: Optional[str] = Field(
        None,
        description="Derechos transmitidos en la cesión. Ejemplo: 'tres derechos hipotecarios'. Si no aplica: 'NO APLICA'",
        json_schema_extra={
            "aliases": ["Valor_Cesion", "Derechos_Cesion", "Cesion_Valor"]
        }
    )

    # ==========================================
    # DATOS REGISTRALES - LIBRO DE PROPIEDAD
    # ==========================================

    Numero_Registro_Libro_Propiedad: Optional[str] = Field(
        None,
        description="Número de registro en palabras MAYÚSCULAS. Ejemplo: 19 → 'DIECINUEVE'",
        json_schema_extra={
            "aliases": [
                "Registro_Propiedad", "Num_Reg_Propiedad", "Numero_Propiedad",
                "Registro_Libro_Propiedad", "No_Registro_Propiedad",
                "numero_registro_libro_propiedad"
            ]
        }
    )

    Tomo_Libro_Propiedad: Optional[str] = Field(
        None,
        description="Tomo del libro de propiedad en palabras MAYÚSCULAS. Ejemplo: 7069 → 'SIETE MIL SESENTA Y NUEVE'",
        json_schema_extra={
            "aliases": ["Tomo_Propiedad", "Volumen_Propiedad", "Tomo_Libro_Prop", "Libro_Propiedad"]
        }
    )

    # ==========================================
    # DATOS REGISTRALES - LIBRO DE GRAVÁMENES
    # ==========================================

    Numero_Registro_Libro_Gravamen: Optional[str] = Field(
        None,
        description="Número de registro del gravamen en palabras MAYÚSCULAS. Ejemplo: 4 → 'CUATRO'",
        json_schema_extra={
            "aliases": [
                "Registro_Gravamen", "Num_Reg_Gravamen", "Numero_Gravamen",
                "Registro_Libro_Gravamen", "No_Registro_Gravamen",
                "numero_registro_libro_gravamen"
            ]
        }
    )

    Tomo_Libro_Gravamen: Optional[str] = Field(
        None,
        description="Tomo del libro de gravamen en palabras MAYÚSCULAS. Ejemplo: 839 → 'OCHOCIENTOS TREINTA Y NUEVE'",
        json_schema_extra={
            "aliases": ["Tomo_Gravamen", "Volumen_Gravamen", "Tomo_Libro_Grav", "Libro_Gravamen"]
        }
    )

    # ==========================================
    # CARTA DE INSTRUCCIONES (Documento Bancario Crítico)
    # ==========================================

    Carta_Instrucciones_Numero_Oficio: Optional[str] = Field(
        None,
        description="Número de expediente de carta de instrucciones. Ejemplo: 'EXP. No. CANC-SOFOL/2023/12'",
        json_schema_extra={
            "aliases": [
                "Numero_Oficio", "Oficio_Carta", "Expediente_Carta", "No_Expediente",
                "carta_instrucciones_numero_oficio"
            ]
        }
    )

    Carta_Instrucciones_Fecha_Constancia_Liquidacion: Optional[str] = Field(
        None,
        description="Fecha de constancia de liquidación en palabras minúsculas. Ejemplo: 'veinte de abril de dos mil veintidós'",
        json_schema_extra={
            "aliases": ["Fecha_Constancia_Liquidacion", "Constancia_Liquidacion_Fecha"]
        }
    )

    Carta_Instrucciones_Nombre_Titular_Credito: Optional[str] = Field(
        None,
        description="Nombre del titular del crédito. Ejemplo: 'María López Ramírez'",
        json_schema_extra={
            "aliases": ["Titular_Credito", "Nombre_Titular_Carta", "Titular_Carta"]
        }
    )

    Carta_Instrucciones_Numero_Credito: Optional[str] = Field(
        None,
        description="Número de crédito según carta. Ejemplo: '123456789'",
        json_schema_extra={
            "aliases": ["Credito_Carta", "Numero_Credito_Carta"]
        }
    )

    Carta_Instrucciones_Tipo_Credito: Optional[str] = Field(
        None,
        description="Tipo de crédito. Ejemplo: 'FOVISSSTE-BANOBRAS CONS.(76)'",
        json_schema_extra={
            "aliases": ["Tipo_Credito", "Programa_Credito", "Modalidad_Credito", "Tipo_Programa", "FOVISSSTE", "INFONAVIT", "Cofinanciado"]
        }
    )

    Carta_Instrucciones_Fecha_Adjudicacion: Optional[str] = Field(
        None,
        description="Fecha de adjudicación en palabras minúsculas. Ejemplo: 'catorce de noviembre de mil novecientos noventa y dos'",
        json_schema_extra={
            "aliases": ["Fecha_Adjudicacion", "Adjudicacion_Fecha"]
        }
    )

    Carta_Instrucciones_Ubicacion_Inmueble: Optional[str] = Field(
        None,
        description="Ubicación del inmueble según carta. Ejemplo: 'CASA HABITACIÓN UBICADA EN LA CALLE...'",
        json_schema_extra={
            "aliases": ["Ubicacion_Inmueble_Carta", "Inmueble_Carta"]
        }
    )

    Carta_Instrucciones_Valor_Credito: Optional[str] = Field(
        None,
        description="Valor del crédito en números. Ejemplo: '500000'",
        json_schema_extra={
            "aliases": ["Valor_Credito", "Monto_Credito_Carta", "Importe_Carta"]
        }
    )

    Carta_Instrucciones_Valor_Credito_Letras: Optional[str] = Field(
        None,
        description="Valor del crédito en letras MAYÚSCULAS. Ejemplo: 'QUINIENTOS MIL PESOS 00/100 M.N.'",
        json_schema_extra={
            "aliases": ["Valor_Credito_Letras", "Monto_Credito_Carta_Letras"]
        }
    )

    Carta_Instrucciones_Numero_Registro: Optional[str] = Field(
        None,
        description="Número de registro en palabras MAYÚSCULAS. Ejemplo: 302 → 'TRESCIENTOS DOS'",
        json_schema_extra={
            "aliases": ["Registro_Carta", "Numero_Registro_Carta"]
        }
    )

    Carta_Instrucciones_Tomo: Optional[str] = Field(
        None,
        description="Tomo en palabras MAYÚSCULAS. Ejemplo: 27 → 'VEINTISIETE'",
        json_schema_extra={
            "aliases": ["Tomo_Carta", "Volumen_Carta"]
        }
    )

    # ==========================================
    # CONSTANCIA DE FINIQUITO
    # ==========================================

    Constancia_Finiquito_Numero_Oficio: Optional[str] = Field(
        None,
        description="Número de oficio de constancia de finiquito. Ejemplo: 'OFICIO NO. JSGR-PROG-30-60/2023/4885'",
        json_schema_extra={
            "aliases": [
                "Oficio_Finiquito", "Numero_Oficio_Finiquito", "No_Oficio_Finiquito",
                "constancia_finiquito_numero_oficio"
            ]
        }
    )

    Constancia_Finiquito_Fecha_Emision: Optional[str] = Field(
        None,
        description="Fecha de emisión de constancia en palabras minúsculas. Ejemplo: 'doce de junio de dos mil veintidós'",
        json_schema_extra={
            "aliases": ["Fecha_Emision_Finiquito", "Emision_Constancia", "Fecha_Constancia"]
        }
    )


# Alias para compatibilidad
Cancelacion = CancelacionKeys


# Metadatos del modelo
CANCELACION_METADATA = {
    "tipo_documento": "cancelacion",
    "nombre_largo": "Cancelación de Hipoteca",
    "total_campos": 35,  # 30 específicos + 5 heredados de BaseKeys
    "campos_heredados": 5,
    "campos_especificos": 30,
    "categorias": [
        "Deudor/Propietario",
        "Institución Financiera/Crédito",
        "Inmueble Hipotecado",
        "Cesión de Crédito",
        "Datos Registrales Propiedad",
        "Datos Registrales Gravamen",
        "Carta de Instrucciones",
        "Constancia de Finiquito"
    ],
    "campos_criticos": [
        "Deudor_Nombre_Completo",
        "Intermediario_Financiero",
        "Suma_Credito",
        "Suma_Credito_Letras",
        "Equivalente_Salario_Minimo",
        "Ubicacion_Inmueble",
        "Numero_Registro_Libro_Propiedad",
        "Tomo_Libro_Propiedad",
        "Numero_Registro_Libro_Gravamen",
        "Tomo_Libro_Gravamen",
        "Carta_Instrucciones_Tipo_Credito"
    ],
    "descripcion": """
    Modelo OPTIMIZADO para extracción de datos de Cancelaciones de Hipotecas.

    AJUSTADO según PDF "documentos notaria.pdf":
    - 30 campos específicos + 5 heredados de BaseKeys = 35 total
    - Eliminados 30 campos extras no requeridos por el PDF

    CAMBIO CLAVE: Descriptions simplificadas a 1 línea + ejemplo explícito
    (patrón de movil_cancelaciones.py que tiene alta efectividad)
    """
}
