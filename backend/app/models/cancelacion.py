"""
ControlNot v2 - Modelo Cancelación de Hipotecas
26 campos específicos para documentos de cancelación de hipotecas

Migrado de movil_cancelaciones.py - CLAVES_ESTANDARIZADAS
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

    Agrega 26 campos específicos de cancelación de hipotecas
    """

    # ==========================================
    # DATOS DEL DEUDOR/PROPIETARIO
    # ==========================================

    Deudor_Nombre_Completo: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR AL DEUDOR/PROPIETARIO===

FORMATO DE SALIDA: NOMBRES Y APELLIDOS EN MAYÚSCULAS
Ejemplo: JUAN CARLOS MARTINEZ LOPEZ

El DEUDOR es la persona o entidad que contrató la hipoteca y ahora la está cancelando.

BUSCAR EN:
1. Certificado de Libertad de Gravamen - sección "PROPIETARIO"
2. Constancia de No Adeudo - sección "NOMBRE DEL DEUDOR" o "ACREDITADO"
3. Estado de cuenta del banco - sección "CLIENTE" o "TITULAR"
4. Escritura original de hipoteca - sección "DEUDOR" o "ACREDITADO"

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Deudor_RFC: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: RFC en mayúsculas sin guiones
Ejemplo: MALJ850615XY7

RFC del deudor/propietario.
Buscar en documentos fiscales, constancias SAT, o identificaciones oficiales.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Deudor_CURP: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: CURP en mayúsculas sin espacios
Ejemplo: MALJ850615HMCRPS09

CURP del deudor/propietario.
Buscar en credencial INE, acta de nacimiento, o documentos oficiales.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Deudor_Estado_Civil: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Estado civil en minúsculas
Valores permitidos: soltero/a, casado/a, divorciado/a, viudo/a, unión libre

Estado civil del deudor al momento de la cancelación.
Buscar en identificaciones o actas.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Deudor_Domicilio: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Domicilio completo
Ejemplo: Calle Morelos número 123, Colonia Centro, C.P. 58000, Morelia, Michoacán

Domicilio actual del deudor.
Buscar en comprobante de domicilio, credencial INE, o documentos oficiales.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE LA INSTITUCIÓN FINANCIERA
    # ==========================================

    Acreedor_Nombre: Optional[str] = Field(
        None,
        description="""===IDENTIFICAR A LA INSTITUCIÓN FINANCIERA===

FORMATO DE SALIDA: Nombre completo de la institución en mayúsculas
Ejemplo: HSBC MEXICO S.A. INSTITUCION DE BANCA MULTIPLE GRUPO FINANCIERO HSBC

El ACREEDOR es el banco o institución financiera que otorgó el crédito hipotecario.

BUSCAR EN:
1. Constancia de No Adeudo - encabezado o pie de página
2. Estado de cuenta - nombre del banco
3. Escritura original de hipoteca - sección "ACREEDOR" o "BANCO"
4. Finiquito - membrete institucional

Bancos comunes: BBVA, HSBC, Santander, Banorte, Scotiabank, Infonavit, Fovissste

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Numero_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de crédito sin espacios ni guiones
Ejemplo: 1234567890

Número de crédito o cuenta del préstamo hipotecario.
Buscar en estados de cuenta, constancia de no adeudo, o contrato de crédito.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Fecha_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: quince de marzo de dos mil diez

Fecha en que se otorgó el crédito hipotecario original.
Buscar en escritura de hipoteca original o contrato de crédito.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Monto_Credito_Original: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad en palabras minúsculas + moneda
Ejemplo: trescientos mil pesos 00/100 M.N.

Monto original del crédito hipotecario otorgado.
Buscar en escritura de hipoteca o contrato de crédito.

Incluir centavos y moneda (M.N. para pesos mexicanos, USD para dólares).

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Suma_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad numérica con formato de moneda
Ejemplo: $250,000.00

Suma de crédito con garantía hipotecaria (monto original otorgado).
Buscar en escritura de hipoteca original o contrato de crédito.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Suma_Credito_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad en letras MAYÚSCULAS
Ejemplo: DOSCIENTOS CINCUENTA MIL PESOS 00/100 M.N.

Monto del crédito escrito en letras MAYÚSCULAS.
Convertir el monto numérico a palabras en MAYÚSCULAS.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Equivalente_Salario_Minimo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número entero
Ejemplo: 500

Equivalente del monto del crédito en salarios mínimos vigentes (VSMGM).
Buscar en escritura de hipoteca original.

IMPORTANTE: Este dato es requerido por ley para créditos de vivienda.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Equivalente_Salario_Minimo_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en letras MAYÚSCULAS
Ejemplo: QUINIENTOS VECES EL SALARIO MÍNIMO

Equivalente en salarios mínimos escrito en letras MAYÚSCULAS.
Convertir el número a palabras en MAYÚSCULAS.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DEL INMUEBLE HIPOTECADO
    # ==========================================

    Inmueble_Tipo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Tipo de inmueble en minúsculas
Valores comunes: casa habitación, departamento, terreno, local comercial, bodega, oficina

Tipo de inmueble que fue hipotecado.
Buscar en certificado de libertad de gravamen, avalúo, o escritura original.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Inmueble_Direccion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Dirección completa del inmueble
Ejemplo: Calle Hidalgo número 456, Colonia Chapultepec, C.P. 58260, Morelia, Michoacán

Dirección completa del inmueble hipotecado.
Buscar en certificado de libertad de gravamen, avalúo, certificado catastral.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Inmueble_Superficie: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Superficie con unidad
Ejemplo: 120.50 metros cuadrados

Superficie del inmueble (terreno y/o construcción).
Buscar en certificado de libertad de gravamen, avalúo, o escritura.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Inmueble_Colindancias: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Colindancias separadas por puntos y coma
Ejemplo: al norte con calle Hidalgo; al sur con propiedad privada; al oriente con casa número 458; al poniente con casa número 454

Colindancias del inmueble (norte, sur, oriente, poniente).
Buscar en certificado de libertad de gravamen o escritura.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE CESIÓN DE CRÉDITO (Si aplica)
    # ==========================================

    Cesion_Credito_Fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: quince de julio de dos mil veintitrés

Fecha en que se realizó la cesión de derechos de crédito (si hubo cesión).
Buscar en escritura de cesión o documento de transmisión de derechos.

IMPORTANTE: Solo aplicable si el crédito fue cedido a otra institución.

Si no aplica o no se encuentra, devuelve 'NO APLICA'"""
    )

    Cesion_Credito_Valor: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción en palabras minúsculas
Ejemplo: tres derechos hipotecarios

Descripción de los derechos transmitidos en la cesión de crédito.
Buscar en escritura de cesión.

IMPORTANTE: Solo aplicable si el crédito fue cedido.

Si no aplica o no se encuentra, devuelve 'NO APLICA'"""
    )

    # ==========================================
    # DATOS REGISTRALES
    # ==========================================

    Folio_Real: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de folio real
Ejemplo: 123456

Número de folio real del inmueble en el Registro Público.
Buscar en certificado de libertad de gravamen o certificado de inscripción.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Partida_Registral: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número y detalles de partida
Ejemplo: partida 789 de la sección primera del volumen 45

Datos de inscripción registral (partida, sección, volumen, libro).
Buscar en certificado de libertad de gravamen o asiento registral.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Numero_Registro_Libro_Propiedad: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
Ejemplo: DIECINUEVE

Número de registro en el libro de PROPIEDAD (no gravamen).
Buscar en certificado de libertad de gravamen o asiento registral.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Tomo_Libro_Propiedad: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de tomo en palabras MAYÚSCULAS
Ejemplo: SIETE MIL SESENTA Y NUEVE

Tomo del libro de PROPIEDAD donde se registró.
Buscar en certificado de libertad de gravamen.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Numero_Registro_Libro_Gravamen: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
Ejemplo: CUATRO

Número de registro en el libro de GRAVÁMENES (hipoteca).
Buscar en certificado de libertad de gravamen o asiento de hipoteca.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Tomo_Libro_Gravamen: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de tomo en palabras MAYÚSCULAS
Ejemplo: CUATRO

Tomo del libro de GRAVÁMENES donde se registró la hipoteca.
Buscar en certificado de libertad de gravamen.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Fecha_Inscripcion_Hipoteca: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: veinte de abril de dos mil diez

Fecha en que se inscribió la hipoteca en el Registro Público.
Buscar en certificado de libertad de gravamen o asiento registral.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE LA CANCELACIÓN
    # ==========================================

    Fecha_Liquidacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: treinta de noviembre de dos mil veinticuatro

Fecha en que se liquidó completamente el crédito hipotecario.
Buscar en constancia de no adeudo, finiquito, o carta de liberación.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Monto_Liquidacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cantidad en palabras minúsculas + moneda
Ejemplo: cero pesos 00/100 M.N.

Monto adeudado al momento de la liquidación (generalmente $0.00 si está liquidado).
Buscar en constancia de no adeudo o estado de cuenta final.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Numero_Finiquito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de finiquito o folio
Ejemplo: FIN-2024-123456

Número de folio del finiquito o constancia de no adeudo emitida por el banco.
Buscar en la constancia de no adeudo o carta de liberación.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Fecha_Finiquito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: cinco de diciembre de dos mil veinticuatro

Fecha de emisión del finiquito o constancia de no adeudo.
Buscar en la constancia de no adeudo.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE REPRESENTACIÓN LEGAL
    # ==========================================

    Representante_Banco_Nombre: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre completo del representante en mayúsculas
Ejemplo: LIC. MARIA FERNANDA GUTIERREZ RAMIREZ

Nombre del representante legal del banco que firma la cancelación.
Buscar en poder notarial del banco o constancia de no adeudo.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Representante_Banco_Cargo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Cargo del representante
Ejemplo: Apoderado Legal

Cargo o puesto del representante del banco.
Buscar en poder notarial o constancia.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Poder_Notarial_Numero: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número del instrumento notarial en palabras
Ejemplo: ciento veintitrés mil quinientos cuarenta y seis

Número del instrumento notarial que acredita la representación del banco.
Buscar en poder notarial.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Poder_Notarial_Fecha: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha completa en palabras minúsculas
Ejemplo: diez de enero de dos mil veinte

Fecha del poder notarial.
Buscar en testimonio del poder.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Poder_Notarial_Notario: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre completo del notario
Ejemplo: Licenciado Carlos Alberto Mendez Torres, Notario Público número 15 de Morelia, Michoacán

Nombre y datos del notario que otorgó el poder.
Buscar en testimonio del poder.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Poder_Notarial_Ciudad: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre de la ciudad
Ejemplo: Morelia

Ciudad de residencia del notario que otorgó el poder.
Buscar en testimonio del poder notarial.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE CARTA DE INSTRUCCIONES (Documento Bancario)
    # ==========================================

    Carta_Instrucciones_Numero_Oficio: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de expediente en formato original
Ejemplo: EXP. No. CANC-SOFOL/2023/12

Número de expediente u oficio de la carta de instrucciones emitida por el banco.
Buscar en carta de instrucciones o carta de liberación.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Fecha_Constancia_Liquidacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha en palabras minúsculas
Ejemplo: veinte de abril de dos mil veintidós

Fecha de la constancia de liquidación mencionada en la carta de instrucciones.
Buscar en carta de instrucciones del banco.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Nombre_Titular_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Nombre completo del titular
Ejemplo: María López Ramírez

Nombre del titular del crédito según la carta de instrucciones.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Numero_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de crédito
Ejemplo: 123456789

Número de crédito o cuenta según carta de instrucciones.
Buscar en carta de instrucciones del banco.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Tipo_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Tipo de crédito en minúsculas
Ejemplo: crédito hipotecario con garantía hipotecaria en primer lugar y grado

Tipo de crédito según la carta de instrucciones.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Fecha_Adjudicacion: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha en palabras minúsculas
Ejemplo: uno de marzo de dos mil veintiuno

Fecha de adjudicación del crédito según carta de instrucciones.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Ubicacion_Inmueble: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Descripción completa de ubicación
Ejemplo: CASA HABITACIÓN UBICADA EN LA CALLE PRIMER RETORNO DE LA ESTACAS, NUMERO 49 (CUARENTA Y NUEVE), CASA "B"...

Descripción completa de la ubicación del inmueble según carta de instrucciones.
Buscar en carta de instrucciones del banco.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Valor_Credito: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Valor numérico sin formato
Ejemplo: 500000

Valor del crédito en números según carta de instrucciones.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Valor_Credito_Letras: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Valor en letras MAYÚSCULAS
Ejemplo: QUINIENTOS MIL PESOS 00/100 M.N.

Valor del crédito escrito en letras MAYÚSCULAS según carta de instrucciones.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Numero_Registro: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número en palabras MAYÚSCULAS
Ejemplo: TRESCIENTOS DOS

Número de registro del crédito según carta de instrucciones, en palabras MAYÚSCULAS.
Buscar en carta de instrucciones.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Carta_Instrucciones_Tomo: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de tomo en palabras MAYÚSCULAS
Ejemplo: VEINTISIETE

Tomo donde se inscribió el crédito según carta de instrucciones, en palabras MAYÚSCULAS.
Buscar en carta de instrucciones del banco.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # DATOS DE CONSTANCIA DE FINIQUITO
    # ==========================================

    Constancia_Finiquito_Numero_Oficio: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Número de oficio completo
Ejemplo: OFICIO NO. JSGR-PROG-30-60/2023/4885

Número de oficio de la constancia de finiquito emitida por el banco.
Buscar en constancia de finiquito o constancia de no adeudo.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    Constancia_Finiquito_Fecha_Emision: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Fecha en palabras minúsculas
Ejemplo: doce de junio de dos mil veintidós

Fecha de emisión de la constancia de finiquito.
Buscar en constancia de finiquito.

Si no se encuentra, devuelve 'NO LOCALIZADO'"""
    )

    # ==========================================
    # OBSERVACIONES
    # ==========================================

    Observaciones: Optional[str] = Field(
        None,
        description="""FORMATO DE SALIDA: Texto libre con observaciones relevantes

Cualquier observación, nota o dato adicional relevante para la cancelación.
Incluir información sobre gravámenes adicionales, anotaciones marginales, etc.

Si no hay observaciones, devuelve 'NINGUNA'"""
    )


# Alias para compatibilidad
Cancelacion = CancelacionKeys


# Metadatos del modelo
CANCELACION_METADATA = {
    "tipo_documento": "cancelacion",
    "nombre_largo": "Cancelación de Hipoteca",
    "total_campos": 55,  # 50 específicos + 5 heredados de BaseKeys
    "campos_heredados": 5,  # fecha_instrumento, lugar_instrumento, numero_instrumento, notario_actuante, numero_notaria
    "campos_especificos": 50,
    "categorias": [
        "Deudor/Propietario",
        "Institución Financiera",
        "Datos del Crédito",
        "Cesión de Crédito",
        "Inmueble Hipotecado",
        "Datos Registrales",
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
        "Monto_Credito_Original",
        "Suma_Credito",
        "Suma_Credito_Letras",
        "Equivalente_Salario_Minimo",
        "Inmueble_Direccion",
        "Folio_Real",
        "Fecha_Liquidacion",
        "Numero_Finiquito",
        "Fecha_Finiquito"
    ],
    "documentos_fuente_tipicos": [
        "Constancia de No Adeudo",
        "Finiquito del Banco",
        "Certificado de Libertad de Gravamen",
        "Estado de Cuenta Final",
        "Escritura Original de Hipoteca",
        "Carta de Instrucciones del Banco",
        "Poder Notarial del Banco",
        "Certificado de Inscripción RPP",
        "Identificación del Deudor (INE)",
        "Comprobante de Domicilio",
        "Escritura de Cesión de Crédito (si aplica)"
    ],
    "descripcion": """
    Modelo COMPLETO para extracción de datos de documentos de Cancelación de Hipotecas.

    Migrado completamente de movil_cancelaciones.py con 50 campos específicos.

    Este tipo de documento se utiliza cuando un deudor ha liquidado completamente
    su crédito hipotecario y el banco (acreedor) acepta liberar el gravamen sobre
    el inmueble, permitiendo su inscripción en el Registro Público de la Propiedad.

    Documentos clave requeridos:
    - Constancia de No Adeudo o Finiquito (del banco)
    - Certificado de Libertad de Gravamen (RPP)
    - Carta de Instrucciones del Banco (documento crítico con datos del crédito)
    - Poder Notarial del representante legal del banco
    - Escritura original de la hipoteca
    - Identificaciones oficiales del deudor (INE, RFC, CURP)
    - Comprobante de domicilio actualizado
    - Escritura de cesión de crédito (si el crédito fue cedido)

    El notario público certifica la cancelación y la envía al RPP para su inscripción,
    quedando el inmueble libre de gravámenes hipotecarios.

    CAMPOS ESPECIALES:
    - Equivalente en salarios mínimos (requerido por ley para créditos de vivienda)
    - Datos separados de libros de propiedad y gravámenes (RPP)
    - 11 campos específicos de Carta de Instrucciones bancaria
    - Campos de cesión de crédito (si aplica)
    """,
    "notas_especiales": """
    IMPORTANTE:
    - El equivalente en salarios mínimos (VSMGM) es OBLIGATORIO por ley
    - La Carta de Instrucciones es un documento crítico emitido por el banco
    - Diferenciar claramente entre datos de libro de propiedad vs libro de gravamen
    - Si hubo cesión de crédito, documentar todos los datos de la cesión
    - El finiquito debe tener número de oficio y fecha de emisión
    """
}
