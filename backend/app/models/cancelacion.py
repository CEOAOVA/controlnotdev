"""
ControlNot v2 - Modelo Cancelación de Hipotecas
Descriptions SIMPLIFICADAS para mejor extracción con IA (patrón movil_cancelaciones.py)

Migrado de movil_cancelaciones.py - CLAVES_ESTANDARIZADAS
Optimizado: 1 línea por descripción + ejemplo explícito
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

    Deudor_RFC: Optional[str] = Field(
        None,
        description="RFC del deudor en mayúsculas sin guiones. Ejemplo: 'MALJ850615XY7'",
        json_schema_extra={
            "aliases": ["RFC_Deudor", "RFC_Cliente", "RFC_Titular", "RFC_Acreditado", "RFC"]
        }
    )

    Deudor_CURP: Optional[str] = Field(
        None,
        description="CURP del deudor en mayúsculas sin espacios. Ejemplo: 'MALJ850615HMCRPS09'",
        json_schema_extra={
            "aliases": ["CURP_Deudor", "CURP_Cliente", "CURP_Titular", "CURP"]
        }
    )

    Deudor_Estado_Civil: Optional[str] = Field(
        None,
        description="Estado civil del deudor en minúsculas. Ejemplo: 'casado'",
        json_schema_extra={
            "aliases": ["Estado_Civil_Deudor", "Estado_Civil_Cliente", "Estado_Civil"]
        }
    )

    Deudor_Domicilio: Optional[str] = Field(
        None,
        description="Domicilio completo del deudor. Ejemplo: 'Calle Morelos número 123, Colonia Centro, C.P. 58000, Morelia, Michoacán'",
        json_schema_extra={
            "aliases": ["Domicilio_Deudor", "Direccion_Deudor", "Domicilio_Cliente", "Direccion_Cliente"]
        }
    )

    # ==========================================
    # DATOS DE LA INSTITUCIÓN FINANCIERA
    # ==========================================

    Acreedor_Nombre: Optional[str] = Field(
        None,
        description="Nombre del banco/institución en MAYÚSCULAS. Ejemplo: 'HSBC MEXICO S.A. INSTITUCION DE BANCA MULTIPLE'",
        json_schema_extra={
            "aliases": ["Banco", "Institucion", "Financiera", "Nombre_Banco", "Institucion_Financiera", "Acreedor", "Nombre_Acreedor", "Hipotecaria"]
        }
    )

    Numero_Credito: Optional[str] = Field(
        None,
        description="Número de crédito bancario. Ejemplo: '1234567890'",
        json_schema_extra={
            "aliases": ["Credito_Numero", "Num_Credito", "Cuenta", "Numero_Cuenta", "Folio_Credito", "No_Credito"]
        }
    )

    Fecha_Credito: Optional[str] = Field(
        None,
        description="Fecha del crédito en palabras minúsculas. Ejemplo: 'quince de marzo de dos mil diez'",
        json_schema_extra={
            "aliases": ["Fecha_Otorgamiento_Credito", "Fecha_Contrato", "Fecha_Escritura_Credito"]
        }
    )

    Monto_Credito_Original: Optional[str] = Field(
        None,
        description="Monto original en palabras minúsculas. Ejemplo: 'trescientos mil pesos 00/100 M.N.'",
        json_schema_extra={
            "aliases": ["Monto_Original", "Capital_Original", "Importe_Original", "Credito_Original"]
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

    Inmueble_Tipo: Optional[str] = Field(
        None,
        description="Tipo de inmueble en minúsculas. Ejemplo: 'casa habitación'",
        json_schema_extra={
            "aliases": ["Tipo_Inmueble", "Tipo_Propiedad", "Clase_Inmueble"]
        }
    )

    Inmueble_Direccion: Optional[str] = Field(
        None,
        description="Dirección completa del inmueble. Ejemplo: 'Calle Hidalgo número 456, Colonia Chapultepec, C.P. 58260, Morelia'",
        json_schema_extra={
            "aliases": ["Domicilio_Inmueble", "Ubicacion", "Direccion", "Direccion_Propiedad", "Domicilio_Propiedad", "Ubicacion_Propiedad"]
        }
    )

    Inmueble_Superficie: Optional[str] = Field(
        None,
        description="Superficie del inmueble con unidad. Ejemplo: '120.50 metros cuadrados'",
        json_schema_extra={
            "aliases": ["Superficie", "Superficie_Inmueble", "Area", "Metros_Cuadrados", "M2"]
        }
    )

    Inmueble_Colindancias: Optional[str] = Field(
        None,
        description="Colindancias separadas por punto y coma. Ejemplo: 'al norte con calle Hidalgo; al sur con propiedad privada'",
        json_schema_extra={
            "aliases": ["Colindancias", "Linderos", "Medidas_Colindancias"]
        }
    )

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

    Folio_Real: Optional[str] = Field(
        None,
        description="Número de folio real del inmueble. Ejemplo: '123456'",
        json_schema_extra={
            "aliases": ["Folio", "Folio_Electronico", "Numero_Folio", "Folio_Inmueble", "Folio_RPP"]
        }
    )

    Partida_Registral: Optional[str] = Field(
        None,
        description="Datos de partida registral. Ejemplo: 'partida 789 de la sección primera del volumen 45'",
        json_schema_extra={
            "aliases": ["Partida", "Numero_Partida", "Partida_Registro"]
        }
    )

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

    Fecha_Inscripcion_Hipoteca: Optional[str] = Field(
        None,
        description="Fecha de inscripción de la hipoteca en palabras minúsculas. Ejemplo: 'veinte de abril de dos mil diez'",
        json_schema_extra={
            "aliases": ["Fecha_Inscripcion", "Fecha_Registro_Hipoteca", "Inscripcion_Hipoteca", "Fecha_Hipoteca"]
        }
    )

    # ==========================================
    # DATOS MULTI-CRÉDITO FOVISSSTE/BANCO
    # ==========================================

    Intermediario_Financiero: Optional[str] = Field(
        None,
        description="Intermediario financiero del crédito. Ejemplo: 'HIPOTECARIA VANGUARDIA'",
        json_schema_extra={
            "aliases": ["Intermediario", "Sofol", "Sofom", "Entidad_Financiera"]
        }
    )

    Credito_Banco_Reg_Propiedad: Optional[str] = Field(
        None,
        description="Registro del crédito BANCO en Libro Propiedad (número/tomo). Ejemplo: '60/1575'",
        json_schema_extra={
            "aliases": ["Reg_Banco_Propiedad", "Banco_Registro_Propiedad", "Inscripcion_Banco_Propiedad"]
        }
    )

    Credito_Banco_Reg_Gravamen: Optional[str] = Field(
        None,
        description="Registro del crédito BANCO en Libro Gravamen (número/tomo). Ejemplo: '28/839'",
        json_schema_extra={
            "aliases": ["Reg_Banco_Gravamen", "Banco_Registro_Gravamen", "Inscripcion_Banco_Gravamen"]
        }
    )

    Credito_FOVISSSTE_Reg_Propiedad: Optional[str] = Field(
        None,
        description="Registro FOVISSSTE en Libro Propiedad. Si es igual al banco, repetir valor",
        json_schema_extra={
            "aliases": ["Reg_FOVISSSTE_Propiedad", "FOVISSSTE_Registro_Propiedad", "Inscripcion_FOVISSSTE_Propiedad"]
        }
    )

    Credito_FOVISSSTE_Reg_Gravamen: Optional[str] = Field(
        None,
        description="Registro FOVISSSTE en Libro Gravamen. Si es igual al banco, repetir valor",
        json_schema_extra={
            "aliases": ["Reg_FOVISSSTE_Gravamen", "FOVISSSTE_Registro_Gravamen", "Inscripcion_FOVISSSTE_Gravamen"]
        }
    )

    # ==========================================
    # DATOS DE LA CANCELACIÓN
    # ==========================================

    Fecha_Liquidacion: Optional[str] = Field(
        None,
        description="Fecha de liquidación en palabras minúsculas. Ejemplo: 'treinta de noviembre de dos mil veinticuatro'",
        json_schema_extra={
            "aliases": ["Liquidacion_Fecha", "Fecha_Pago_Total", "Fecha_Finiquito_Credito"]
        }
    )

    Monto_Liquidacion: Optional[str] = Field(
        None,
        description="Monto adeudado al liquidar. Ejemplo: 'cero pesos 00/100 M.N.'",
        json_schema_extra={
            "aliases": ["Liquidacion_Monto", "Importe_Liquidacion", "Saldo_Liquidacion"]
        }
    )

    Numero_Finiquito: Optional[str] = Field(
        None,
        description="Número de folio del finiquito. Ejemplo: 'FIN-2024-123456'",
        json_schema_extra={
            "aliases": ["Finiquito_Numero", "Folio_Finiquito", "No_Finiquito"]
        }
    )

    Fecha_Finiquito: Optional[str] = Field(
        None,
        description="Fecha del finiquito en palabras minúsculas. Ejemplo: 'cinco de diciembre de dos mil veinticuatro'",
        json_schema_extra={
            "aliases": ["Finiquito_Fecha", "Fecha_Constancia_Finiquito"]
        }
    )

    # ==========================================
    # DATOS DE REPRESENTACIÓN LEGAL
    # ==========================================

    Representante_Banco_Nombre: Optional[str] = Field(
        None,
        description="Nombre del representante del banco en mayúsculas. Ejemplo: 'LIC. MARIA FERNANDA GUTIERREZ RAMIREZ'",
        json_schema_extra={
            "aliases": ["Nombre_Representante", "Apoderado_Nombre", "Representante_Legal", "Nombre_Apoderado"]
        }
    )

    Representante_Banco_Cargo: Optional[str] = Field(
        None,
        description="Cargo del representante del banco. Ejemplo: 'Apoderado Legal'",
        json_schema_extra={
            "aliases": ["Cargo_Representante", "Apoderado_Cargo", "Cargo_Apoderado"]
        }
    )

    Poder_Notarial_Numero: Optional[str] = Field(
        None,
        description="Número del poder notarial en palabras. Ejemplo: 'ciento veintitrés mil quinientos cuarenta y seis'",
        json_schema_extra={
            "aliases": ["Numero_Poder", "Escritura_Poder", "Poder_Numero", "No_Poder"]
        }
    )

    Poder_Notarial_Fecha: Optional[str] = Field(
        None,
        description="Fecha del poder notarial en palabras minúsculas. Ejemplo: 'diez de enero de dos mil veinte'",
        json_schema_extra={
            "aliases": ["Fecha_Poder", "Poder_Fecha", "Fecha_Escritura_Poder"]
        }
    )

    Poder_Notarial_Notario: Optional[str] = Field(
        None,
        description="Nombre y datos del notario del poder. Ejemplo: 'Licenciado Carlos Alberto Mendez Torres, Notario Público número 15 de Morelia'",
        json_schema_extra={
            "aliases": ["Notario_Poder", "Notario_Otorgante_Poder", "Datos_Notario_Poder"]
        }
    )

    Poder_Notarial_Ciudad: Optional[str] = Field(
        None,
        description="Ciudad del notario del poder. Ejemplo: 'Morelia'",
        json_schema_extra={
            "aliases": ["Ciudad_Poder", "Lugar_Poder", "Ciudad_Notario_Poder"]
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

    # ==========================================
    # OBSERVACIONES
    # ==========================================

    Observaciones: Optional[str] = Field(
        None,
        description="Observaciones adicionales relevantes. Si no hay: 'NINGUNA'",
        json_schema_extra={
            "aliases": ["Notas", "Comentarios", "Notas_Adicionales", "Obs"]
        }
    )


# Alias para compatibilidad
Cancelacion = CancelacionKeys


# Metadatos del modelo
CANCELACION_METADATA = {
    "tipo_documento": "cancelacion",
    "nombre_largo": "Cancelación de Hipoteca",
    "total_campos": 61,  # 56 específicos + 5 heredados de BaseKeys
    "campos_heredados": 5,
    "campos_especificos": 56,
    "categorias": [
        "Deudor/Propietario",
        "Institución Financiera",
        "Datos del Crédito",
        "Cesión de Crédito",
        "Inmueble Hipotecado",
        "Datos Registrales Propiedad",
        "Datos Registrales Gravamen",
        "Multi-Crédito FOVISSSTE",
        "Datos de Cancelación",
        "Constancia de Finiquito",
        "Carta de Instrucciones",
        "Representación Legal",
        "Observaciones"
    ],
    "campos_criticos": [
        "Deudor_Nombre_Completo",
        "Acreedor_Nombre",
        "Numero_Credito",
        "Suma_Credito",
        "Suma_Credito_Letras",
        "Equivalente_Salario_Minimo",
        "Numero_Registro_Libro_Propiedad",
        "Tomo_Libro_Propiedad",
        "Numero_Registro_Libro_Gravamen",
        "Tomo_Libro_Gravamen",
        "Inmueble_Direccion",
        "Folio_Real",
        "Fecha_Liquidacion",
        "Carta_Instrucciones_Tipo_Credito"
    ],
    "descripcion": """
    Modelo OPTIMIZADO para extracción de datos de Cancelaciones de Hipotecas.

    CAMBIO CLAVE: Descriptions simplificadas a 1 línea + ejemplo explícito
    (patrón de movil_cancelaciones.py que tiene alta efectividad)

    Incluye campos para multi-crédito FOVISSSTE/BANCO.
    """
}
